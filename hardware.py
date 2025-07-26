#!/usr/bin/env python3
# aa '25
from luma.core.interface.serial import i2c, spi
from luma.core.render import canvas
from luma.oled.device import ssd1309
from PIL import ImageFont, Image, ImageDraw
from time import sleep
import numpy
import cv2
import numpy as np
# Create an interface for the SSD1309. Only needs basic functionality, such as:
# Draw a point onto the screen at certain coordinates.

class TransparentDisplay:
    def __init__(self, type="ssd1309", address=0x3C):
        self.type = type
        self.address = address # in some displays/modules it may be 0x3D

        serial = i2c(port=1, address=self.address)
        self.device = ssd1309(serial)

    
    def point(self, coords, brightness=1): # -> coords is a 1-dimensional numpy array containg [x, y]

        image = Image.new("1", self.device.size) # probably can be optimised
        draw = ImageDraw.Draw(image)

        x = coords[0]
        y = coords[1]
        draw.ellipse((x - 1, y - 1, x + 1, y + 1), fill=255*brightness) # Can scale down brightness from 0-1

        self.device.display()

    def clear(self):
        self.device.clear()
    


def undistort(frame, map1, map2, flip_180=True):

    # 1) undistort / rectify
    undist = cv2.remap(frame, map1, map2, interpolation=cv2.INTER_LINEAR)
    
    # 2) flip 180° if mounted upside-down
    if flip_180:
        undist = cv2.rotate(undist, cv2.ROTATE_180)
    
    return undist

def from_observer(aruco_from_front_facing, observer_from_front_facing):
    return aruco_from_front_facing - observer_from_front_facing # VECTOR THAT SHOWS ARUCO FROM OBSERVER CAMERA

def intersect_display(plane_center, plane_width, plane_height, resolution, vector):
    """
    Find the pixel hit on a display plane by a 3D vector from the origin.

    Args:
        plane_center (np.ndarray): 3D point, center of the plane (display).
        plane_width (float): Width of the plane in world units.
        plane_height (float): Height of the plane in world units.
        resolution (tuple): (width_px, height_px) resolution of the display.
        vector (np.ndarray): Direction vector from the origin (3D).

    Returns:
        (int, int): Pixel coordinates (x, y) if intersection occurs, else None.
    """
    # Step 1: Define the plane
    normal = plane_center / np.linalg.norm(plane_center)  # Assume plane faces origin

    # Step 2: Ray-plane intersection
    denom = np.dot(normal, vector)
    if np.abs(denom) < 1e-6:
        return None  # No intersection, vector is parallel to plane

    t = np.dot(normal, plane_center) / denom
    if t <= 0:
        return None  # Intersection is behind the origin

    # Step 3: Get intersection point in world space
    intersection = t * vector

    # Step 4: Find local 2D coordinates on the plane
    # Create an orthonormal basis (u, v, n) on the plane
    n = normal
    # Arbitrary vector not parallel to n
    up = np.array([0, 1, 0]) if np.abs(n[1]) < 0.9 else np.array([1, 0, 0])
    u = np.cross(up, n)
    u = u / np.linalg.norm(u)
    v = np.cross(n, u)

    # Offset from center in local plane coordinates
    local = intersection - plane_center
    x_disp = np.dot(local, u)
    y_disp = np.dot(local, v)

    # Step 5: Map to pixel coordinates
    w_px, h_px = resolution
    if np.abs(x_disp) > plane_width / 2 or np.abs(y_disp) > plane_height / 2:
        return None  # Outside bounds of the display

    x_norm = (x_disp + plane_width / 2) / plane_width
    y_norm = (y_disp + plane_height / 2) / plane_height

    x_pix = int(x_norm * w_px)
    y_pix = int((1 - y_norm) * h_px)  # Flip Y for screen coordinates

    return x_pix, y_pix