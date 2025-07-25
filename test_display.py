from transparent_display import TransparentDisplay
from time import sleep
import random

display = TransparentDisplay()
points = ((1,1), (20,1), (1,20), (20,20))
display.draw_bounding_box(points)
sleep(5)
def rx():
    return random.randint(0,127)
def ry():
    return random.randint(0,64)
while True:
    points = ((rx(), ry()), (rx(), ry()), (rx(), ry()), (rx(), ry()))
    display.draw_bounding_box(points)
    sleep(0.01)


#######
#     #
#     #
#######

  ##
  ##