from transparent_display import TransparentDisplay
from time import sleep

display = TransparentDisplay()
points = ((1,1), (1,20) (20,1), (20,20))
display.draw_bounding_box(points)
sleep(5)