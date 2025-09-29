#!/usr/bin/env python3
# aa '25
from luma.core.interface.serial import i2c, spi
from luma.core.render import canvas
from luma.oled.device import ssd1309
from PIL import ImageFont, Image, ImageDraw
from time import sleep

# Create an interface for the SSD1309. Only needs basic functionality, such as:
# - Draw a quadrilateral around a set of 4 points (given from aruco detection)
# - Draw text to the screen

class TransparentDisplay:
    def __init__(self, type="ssd1309", address=0x3C):
        self.type = type
        self.address = address # in some displays/modules it may be 0x3D

        serial = i2c(port=1, address=self.address)
        self.device = ssd1309(serial)
        self.font = ImageFont.load_default()

    def draw_text(self, text, x, y):
        with canvas(self.device) as draw:
            draw.text((x, y), "Hello SSD1309!", font=self.font, fill=255) 

    def draw_bounding_box(self, points): # Where points is a tuple as follows (top left, top right, bottom left, bottom right)
        assert len(points)==4 # Exactly 4 points are required.

        image = Image.new("1", self.device.size)
        draw = ImageDraw.Draw(image)

        # Draw polygon using the 4 points
        draw.polygon(points, outline=255, fill=0)  # outline=255 for white

        # Display the image
        self.device.display(image)
    
    def draw_midpoint(self, points):
        x = 0
        y = 0

        image = Image.new("1", self.device.size)
        draw = ImageDraw.Draw(image)

        for point in points:
            x += point[0]
            y += point[1]
        x = x/4
        y = y/4

        draw.ellipse((x - 1, y - 1, x + 1, y + 1), fill=255)

        self.device.display(image)

    def clear(self):
        self.device.clear()
    
    def map_points_to_display(self, points, src_size=(640, 480), dst_size=(128, 64)):
        src_w, src_h = src_size
        dst_w, dst_h = dst_size

        scale_x = dst_w / src_w
        scale_y = dst_h / src_h

        mapped = tuple(
            (int(x * scale_x), int(y * scale_y)) for (x, y) in points
        )
        return mapped


