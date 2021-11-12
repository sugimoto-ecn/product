from thirdparty.LCD1602I2C.LCD import LCD

    
class Lcd(object):
    def __init__(self):
        self.lcd = LCD(2,0x27,True)

    def show_display(self , first , second):
        self.lcd.message(first, 1)
        self.lcd.message(second, 2)

    def __del__(self):
        self.lcd.clear()

