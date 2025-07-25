from transparent_display import TransparentDisplay
from time import sleep

display = TransparentDisplay()
points = ((1,1), (20,1), (1,20), (20,20))
display.draw_bounding_box(points)
sleep(1)
display.clear()
display.draw_midpoint(points)
sleep(1)
display.clear()
display.draw_text(0,0,0)
sleep(10)
#######
#     #
#     #
#######

  ##
  ##