import time
from Xlib import X, display

d = display.Display()
s = d.screen()
root = s.root

while True:
    root.warp_pointer(1000, 1000)
    d.sync()
    time.sleep(0.1)
    root.warp_pointer(1000, 990)
    d.sync()
    time.sleep(0.1)


