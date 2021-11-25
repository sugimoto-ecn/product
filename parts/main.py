import RPi.GPIO as GPIO
import threading
import requests
from utils import time_format
from models import btn
import time
from LCD1602I2C.LCD import LCD
from controller import lcd_clock_controller , active_buzzer_controller

class Servo():
    def __init__(self):
        self.SERVO_MIN_PULSE = 500
        self.SERVO_MAX_PULSE = 2500
        self.pin = 18

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


input_value_1 = ['?', '?', '?', '?','?', '?', '?', '?']
input_value_2 = ['?', '?', '?', '?']
product_id = ['1', '1', '1', '1','1', '1', '1', '1']
password = [0, 0, 0, 0]
alerm_time = "**:**:**"
BTN_PIN=21
clock = lcd_clock_controller.ClockController(alerm_time)
button = btn.Btn(BTN_PIN)
keypad = None
last_key_pressed = None
alerm=False
url = 'https://api.thingspeak.com/update'
user_info = None
SERVO_PIN=18
servo = Servo()



def set_alerm():
    global alerm_time
    while True:
        response = requests.get(url,
        params = {
        'api_key': api_key,
        'field1': brightness
        })
        print(response.json)
        alerm_time = response.json
        time.sleep(60*6)

def setup_key():
    global keypad, last_key_pressed, lcd
    rowsPins = [14,23,24,25]
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
    lcd.message('Enter id',2)

def show_display():
    global keypad, last_key_pressed
    while True:
        # lcd.clear()  
        current_time = time_format.current_time_format()
        pressed_keys = keypad.read()
        # clock.show_current_time()
        # print(button.status)
        if user_info == None and input_value_1[0] == "?":
            if button.status:
                clock.show_current_time()
            else:
                lcd.message("", 2)
                lcd.message("Enter productId:", 1)
        if user_info != None and input_value_2[0] == "?":
            if button.status:
                clock.show_current_time()
            else:
                clock.show_alerm_time() 
        if user_info == None and input_value_1[0] != "?":
            lcd.message("Enter id:", 1)
            lcd.message("".join(input_value_1), 2)

        if input_value_2[0] != "?":
            lcd.message("Enter password:", 1)
            lcd.message("".join(input_value_2), 2) 
        time.sleep(0.1)

def set_user():
    global user_info, alerm_time, password
    user_info = {
        "name":"user1",
        "alerm":"00:04:30",
        "password":"1111"
    }
    alerm_time = user_info["alerm"]
    password[0] = user_info["password"][0]
    password[1] = user_info["password"][1]
    password[2] = user_info["password"][2]
    password[3] = user_info["password"][3]

    clock.change_alerm(alerm_time)
    # response = requests.get(url,
    # params = {
    # 'api_key': api_key,
    # 'field1': brightness
    # })
    # user_info = response

def check(target, value, LENS):
    print("password",target)
    print("testword",value)
    for i in range(0,LENS):
        if(target[i]!=value[i]):
            return 0
    return 1


def buzzer_func():
    global button, servo, alerm
    BUZZER_PIN = 16
    active = active_buzzer_controller.ActiveBuzzerController(BUZZER_PIN)

    ring = 0
    while True:
        current_time = time_format.current_time_format()
        if(user_info != None):            
            if alerm_time==current_time["hms"]:
                button.init_status()
                alerm = True
                print("alerm") 
                servo.unrock()

            if  alerm == True:
                print('alerming')
                status = button.status
                active.on()
                time.sleep(0.08)
                active.off()
                time.sleep(0.05)
                ring += 1
                if ring >= 4:
                    ring = 0
                    time.sleep(0.5)
                if button.status:
                    alerm = False
        time.sleep(0.1)

def loop():
    global lcd
    global input_value_1, last_key_pressed,product_id
    global servo
    global password,alerm
    keyIndex=0
    LENS1 = 8
    LENS2 = 4
    setup_key()
    display_thread = threading.Thread(target=show_display)
    display_thread.start()

    alerm_thread = threading.Thread(target=buzzer_func)
    alerm_thread.start()
    servo.setup()
    servo.unrock()

    while True:
        if user_info == None:
            pressed_keys = keypad.read()
            if len(pressed_keys) != 0 and last_key_pressed != pressed_keys:       
                input_value_1[keyIndex]=pressed_keys[0]
                keyIndex+=1
            if (keyIndex is LENS1):
                if (check(product_id, input_value_1,LENS1 ) is 1):
                    set_user()
                    servo.rock()
                input_value_1[0]="?"
                input_value_1[1]="?"
                input_value_1[2]="?"
                input_value_1[3]="?"
                input_value_1[4]="?"
                input_value_1[5]="?"
                input_value_1[6]="?"
                input_value_1[7]="?"
            keyIndex=keyIndex%LENS1
        else:
            pressed_keys = keypad.read()
            if len(pressed_keys) != 0 and last_key_pressed != pressed_keys:       
                input_value_2[keyIndex]=pressed_keys[0]
                keyIndex+=1
            if (keyIndex is LENS2):
                if (check(password, input_value_2,LENS2 ) is 1):
                    # set_user()
                    servo.unrock()
                input_value_2[0]="?"
                input_value_2[1]="?"
                input_value_2[2]="?"
                input_value_2[3]="?"
            keyIndex=keyIndex%LENS2
        last_key_pressed = pressed_keys
        time.sleep(0.1)

def destroy():
    lcd.clear()
    GPIO.cleanup()

if __name__ == '__main__':
    try:
        loop()
    except KeyboardInterrupt:
        destroy()