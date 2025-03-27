import time
from Xlib import X, display

d = display.Display()
s = d.screen()
root = s.root

while True:
    root.warp_pointer(1, 1)
    d.sync()
    time.sleep(10)
    root.warp_pointer(20, 20)
    d.sync()
    time.sleep(10)


