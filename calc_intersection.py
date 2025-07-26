import numpy as np

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


if __name__ == "__main__":
    plane_center = np.array([0, 0, 38.3])  # Display 38.3mm in front of camera
    plane_width = 42.04  # Active screen width in mm
    plane_height = 27.22  # Active screen width in mm
    resolution = (128, 56)  # Active screen resolution
    vector = np.array([-0.1, 0.1, 1])  

    pixel = intersect_display(plane_center, plane_width, plane_height, resolution, vector)
    print("Hit pixel:", pixel)

