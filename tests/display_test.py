from luma.core.interface.serial import i2c
from luma.oled.device import ssd1309
from PIL import Image, ImageDraw
import time

# Initialize display (adjust i2c port/address if needed)
serial = i2c(port=1, address=0x3C)
device = ssd1309(serial)

# Create a blank image (mode "1" = 1-bit monochrome)
image = Image.new("1", device.size)
draw = ImageDraw.Draw(image)

# Draw a rectangle
draw.rectangle([(10, 10), (100, 40)], outline=255, fill=0)

# Display it
device.display(image)

# Keep it for 5 seconds
time.sleep(5)

# Clear the screen after
device.clear()
