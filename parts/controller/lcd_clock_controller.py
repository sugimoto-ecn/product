from models import lcd_clock
from utils import time_format
import time


class ClockController(object):
    def __init__(self, alerm):
        self.alerm=alerm
        self.clock = lcd_clock.Lcd()

    def show_current_time(self):
        current_time = time_format.current_time_format()
        self.clock.show_display(current_time["ymd"] , current_time["hms"])
    
    def show_alerm_time(self):
        self.clock.show_display("Alerm time:", self.alerm)
    
    def change_alerm(self, new_val):
        self.alerm=new_val

    def off(self):
        del self.clock