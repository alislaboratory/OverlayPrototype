#!/usr/bin/env python3
from luma.core.interface.serial import i2c, spi
from luma.core.render import canvas
from luma.oled.device import ssd1309
from PIL import ImageFont
from time import sleep


serial = i2c(port=1, address=0x3C)


device = ssd1309(serial)
font   = ImageFont.load_default()

# draw a simple message
with canvas(device) as draw:
    draw.text((0, 0), "Hello SSD1309!", font=font, fill=255)

sleep(5) # show it on the screen for 5 seconds
