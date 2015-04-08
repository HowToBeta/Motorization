import time
from debug_log import debug_print
lg = debug_print(debug_level=150, save_level=0, save_debug=True, filename="debug_print/debugprint"+str(time.time())+".txt", time_stamp=False)

from drive import *

time.sleep(2)

current_status = ['break', 'slow', 'straight']

while True:
	raw_input('left45')
	left45(current_status)
	raw_input('right45')
	right45(current_status)
	raw_input('left90')
	left90(current_status)
	raw_input('right90')
	right90(current_status)
