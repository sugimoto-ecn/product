import RPi.GPIO as GPIO
import time
from LCD1602I2C.LCD import LCD

##################### HERE IS THE KEYPAD LIBRARY TRANSPLANTED FROM Arduino ############
#class Key:Define some of the properties of Key
class Keypad():

    def __init__(self, rowsPins, colsPins, keys):
        self.rowsPins = rowsPins
        self.colsPins = colsPins
        self.keys = keys
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.rowsPins, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.colsPins, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def read(self):
        pressed_keys = []
        for i, row in enumerate(self.rowsPins):
            GPIO.output(row, GPIO.HIGH)
            for j, col in enumerate(self.colsPins):
                index = i * len(self.colsPins) + j
                if (GPIO.input(col) == 1):
                    pressed_keys.append(self.keys[index])
            GPIO.output(row, GPIO.LOW)
        return pressed_keys

################ EXAMPLE CODE START HERE ################
LENS = 4
password=['1','9','8','4']
testword=['','','','']
keyIndex=0

def check():
    print("password",password)
    print("testword",testword)
    for i in range(0,LENS):
        if(password[i]!=testword[i]):
            return 0
    return 1

def setup():
    global keypad, last_key_pressed
    rowsPins = [18,23,24,25]
    colsPins = [10,22,27,17]
    keys = ["1","2","3","A",
            "4","5","6","B",
            "7","8","9","C",
            "*","0","#","D"]
    keypad = Keypad(rowsPins, colsPins, keys)
    last_key_pressed = []
    lcd = LCD(2,0x27,True)   # init(slave address, background light)
    lcd.clear()
    lcd.message('WELCOME!',1)
    lcd.message('Enter password',2)
    time.sleep(2)

def destroy():
    lcd.clear()
    GPIO.cleanup()

def loop():
    global keyIndex
    global LENS
    global keypad, last_key_pressed
    lcd = LCD(2,0x27,True)
    while(True):
        pressed_keys = keypad.read()
        if len(pressed_keys) != 0 and last_key_pressed != pressed_keys:
            lcd.clear()         
            testword[keyIndex]=pressed_keys[0]
            keyIndex+=1
            lcd.message("Enter password:", 1)
            lcd.message("".join(testword), 2)   
            if (keyIndex is LENS):
                if (check() is 0):
                    lcd.clear()
                    lcd.message("WRONG KEY!", 1)
                    lcd.message("please try again", 2)
                    testword[0]=""
                    testword[1]=""
                    testword[2]=""
                    testword[3]=""
                else:
                    lcd.clear()
                    lcd.message("CORRECT!", 1)
                    lcd.message("welcome back", 2)
            keyIndex=keyIndex%LENS

        last_key_pressed = pressed_keys
        time.sleep(0.1)

if __name__ == '__main__':     # Program start from here
    try:
        setup()
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the program destroy() will be  executed.
        destroy()