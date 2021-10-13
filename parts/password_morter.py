import RPi.GPIO as GPIO
import time
from LCD1602I2C.LCD import LCD



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

class Servo():
    def __init__(self, pin):
        self.SERVO_MIN_PULSE = 500
        self.SERVO_MAX_PULSE = 2500
        self.pin = 13

    def map(self, value, inMin, inMax, outMin, outMax):
        return (outMax - outMin) * (value - inMin) / (inMax - inMin) + outMin

    def setup(self):
        global p
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
        p = GPIO.PWM(self.pin, 50)     # set Frequecy to 50Hz
        p.start(0)  
    
    def setAngle(self, angle):      # make the servo rotate to specific angle (0-180 degrees)
        angle = max(0, min(180, angle))
        pulse_width = self.map(angle, 0, 180, self.SERVO_MIN_PULSE, self.SERVO_MAX_PULSE)
        pwm = self.map(pulse_width, 0, 20000, 0, 100)
        p.ChangeDutyCycle(pwm)
    
    def rock(self):
        for i in range(0, 181, 5):   #make servo rotate from 0 to 180 deg
            self.setAngle(i)     # Write to servo
            time.sleep(0.002)

    def unrock(self):
        for i in range(180, -1, -5): #make servo rotate from 180 to 0 deg
            self.setAngle(i)
            time.sleep(0.001)

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


servo = Servo(13)
status = False
def swServo(val):
    global servo
    global status
    print(status)
    print(val)
    if not status and val:
        servo.rock()
        status = val
    if not val:
        status = val

def loop():
    global keyIndex
    global LENS
    global servo
    global status
    global keypad, last_key_pressed
    lcd = LCD(2,0x27,True)
    servo.setup()
    servo.rock()

    BUTTON_PIN = 26
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
    # GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=swServo)
    while(True):
        pressed_keys = keypad.read()
        if GPIO.input(BUTTON_PIN) == GPIO.HIGH:
            # print('hin')
            swServo(False)
        else:
            print('yaa')
            swServo(True)

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
                    servo.rock()
                else:
                    lcd.clear()
                    lcd.message("CORRECT!", 1)
                    lcd.message("welcome back", 2)
                    servo.unrock()
            keyIndex=keyIndex%LENS

        last_key_pressed = pressed_keys
        time.sleep(0.1)

if __name__ == '__main__':     # 
    try:
        setup()
        loop()
    except KeyboardInterrupt:  #
        destroy()