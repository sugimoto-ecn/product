import RPi.GPIO as GPIO
import threading
import requests
from utils import time_format
from models import btn
import time
import pigpio
import json
import datetime;
from LCD1602I2C.LCD import LCD
from controller import lcd_clock_controller , active_buzzer_controller

# mkmkm
#

class Servo():
    
    def __init__(self):
        self.pi = pi = pigpio.pi()
        self.SERVO_MIN_PULSE = 500
        self.SERVO_MAX_PULSE = 2500
        self.pin = 18

    def map(self, value, inMin, inMax, outMin, outMax):
        return (outMax - outMin) * (value - inMin) / (inMax - inMin) + outMin

    def setup(self):
        global p
        # GPIO.setmode(GPIO.BCM)
        # GPIO.setup(self.pin, GPIO.OUT)
        # GPIO.output(self.pin, GPIO.LOW)
        # p = GPIO.PWM(self.pin, 50)     # set Frequecy to 50Hz
        # p.start(0) 
        gp_out = 18
        GPIO.setup(gp_out, GPIO.OUT) 
        self.servo = GPIO.PWM(gp_out, 50)
        self.servo.start(0)
    # def setAngle(self, angle):      # make the servo rotate to specific angle (0-180 degrees)
    #     angle = max(0, min(90, angle))
    #     pulse_width = self.map(angle, 0, 90, self.SERVO_MIN_PULSE, self.SERVO_MAX_PULSE)
    #     pwm = self.map(pulse_width, 0, 20000, 0, 100)
    #     p.ChangeDutyCycle(pwm)
    
    def rock(self):
        # for i in range(0, 91, 5):   #make servo rotate from 0 to 180 deg
        #     self.setAngle(i)     # Write to servo
        #     time.sleep(0.002)su

        self.servo.ChangeDutyCycle(12)

        # self.pi.set_servo_pulsewidth( SERVO_PIN, 1500 )
    def unrock(self):
        # self.pi.set_servo_pulsewidth( SERVO_PIN, 500 )
        self.servo.ChangeDutyCycle(7.25)
        

        # for i in range(90, -1, -5): #make servo rotate from 180 to 0 deg
        #     self.setAngle(i)
        #     time.sleep(0.001)

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
sleep_time = "**:**:**"
BTN_PIN=21
LED_PIN = 20
clock = lcd_clock_controller.ClockController(alerm_time, sleep_time)
button = btn.Btn(BTN_PIN)
keypad = None
last_key_pressed = None
alerm=False
url = 'https://www.tomomin-dev.link/v1'
user_info = None
SERVO_PIN=18
servo = Servo()
is_close = False
is_sleeping = False
id = None



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


"""
キーパッド関連
"""
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


"""
モニター関連
"""
def show_display():
    global keypad, last_key_pressed,is_sleeping
    while True:
        # lcd.clear()  
        current_time = time_format.current_time_format()
        pressed_keys = keypad.read()
        
        #未ログイン + 入力値なし
        if user_info == None and input_value_1[0] == "?":
            if button.status:
                clock.show_current_time()
            else:
                lcd.message("", 2)
                lcd.message("Enter productId:", 1)
        #ログイン　＋　入力値なし
        if user_info != None and input_value_2[0] == "?":
            if button.status:
                clock.show_current_time()
            else:
                # night = clock.show_time() 
                night = clock.show_alerm_time()

        #未ログイン ＋ 入力中
        if user_info == None and input_value_1[0] != "?":
            lcd.message("Enter id:", 1)
            lcd.message("".join(input_value_1), 2)

        #ログイン　＋　入力中
        if input_value_2[0] != "?":
            lcd.message("Enter password:", 1)
            lcd.message("".join(input_value_2), 2) 
        time.sleep(0.1)


"""
ユーザー情報取得＋格納
"""
def set_user():
    global user_info, alerm_time, password,url,input_value_1,servo,id
    if(input_value_1[0] != "?"):
        id = "".join(input_value_1)
    response = requests.post(url+'/users/product',json={
        'id':id
    })
    print(response.text)
    print('*******')
    datas = json.loads(response.text)
    if "email" not in datas["user"]:
        input_value_1[0]="?"
        input_value_1[1]="?"
        input_value_1[2]="?"
        input_value_1[3]="?"
        input_value_1[4]="?"
        input_value_1[5]="?"
        input_value_1[6]="?"
        input_value_1[7]="?"
        return
    user_info = {
        "user_id":datas["user"]["id"],
        "name":datas["user"]["email"],
        "alerm":datas["schedule"][0]["wakeup"],
        "sleep":datas["schedule"][0]["sleep"],
        "password":"1111"
    }
    print(user_info)
    alerm_time = user_info["alerm"]
    sleep_time = user_info["sleep"]
    password[0] = user_info["password"][0]
    password[1] = user_info["password"][1]
    password[2] = user_info["password"][2]
    password[3] = user_info["password"][3]

    clock.change_alerm(alerm_time)
    clock.change_seep(sleep_time)
    # response = requests.get(url,
    # params = {
    # 'api_key': api_key,
    # 'field1': brightness
    # })
    # user_info = response


"""
パスワード入力チェック
"""
def check(target, value, LENS):
    for i in range(0,LENS):
        if(target[i]!=value[i]):
            return 0
    return 1



"""
ブザーを鳴らす系
"""
def buzzer_func():
    global button, servo, alerm,is_close
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
                    button.init_status()
                    is_close = True

        time.sleep(0.1)



def update_info():
    global user_info
    status = False
    while True:
        # if status != True and user_info != None:
        #     user_info_thread = threading.Thread(target=set_user)
        #     user_info_thread.start()
        #     status = True

        if user_info != None:
            # get_user()
            print('--------')
            set_user()
            response = requests.get(url+'/sleep/'+ str(user_info["user_id"]) +'/get',
            params = {
            })
            print(response.text)
        time.sleep(60 * 60)

def post_sleep():
    global user_info
    time = datetime.datetime.now()
    print(time)
    response = requests.post(url+'/sleep/create',json={
        "type":"sleep",
        # "value":time,
        "user_id":user_info["user_id"]
    })
    datas = json.loads(response.text)

def post_wakeup():
    global user_info
    time = datetime.datetime.now()
    print(time)
    response = requests.post(url+'/sleep/create',json={
        "type":"wakeup",
        # "value":time,
        "user_id":user_info["user_id"]
    })
    datas = json.loads(response.text)

    
"""
メインのループ
"""
def loop():
    global lcd
    global input_value_1, last_key_pressed,product_id
    global servo
    global password,alerm,is_close
    keyIndex=0
    LENS1 = 8
    LENS2 = 4
    setup_key()
    
    display_thread = threading.Thread(target=show_display)
    display_thread.start()

    alerm_thread = threading.Thread(target=buzzer_func)
    alerm_thread.start()

    user_info_thread = threading.Thread(target=update_info)
    user_info_thread.start()

    servo.setup()
    servo.unrock()
    while True:
        if user_info == None:
            pressed_keys = keypad.read()
            if len(pressed_keys) != 0 and last_key_pressed != pressed_keys:       
                input_value_1[keyIndex]=pressed_keys[0]
                keyIndex+=1
            if (keyIndex is LENS1):
                set_user()
                # servo.rock()
            keyIndex=keyIndex%LENS1
        else:
            pressed_keys = keypad.read()
            if len(pressed_keys) != 0 and last_key_pressed != pressed_keys:       
                input_value_2[keyIndex]=pressed_keys[0]
                keyIndex+=1
            if (keyIndex is LENS2):
                if (check(password, input_value_2,LENS2 ) is 1):
                    if is_close == False:
                        post_sleep()
                        servo.rock()
                        is_close = True
                    else:
                        post_wakeup()
                        servo.unrock()
                        is_close = False
                input_value_2[0]="?"
                input_value_2[1]="?"
                input_value_2[2]="?"
                input_value_2[3]="?"
            keyIndex=keyIndex%LENS2

            # if is_close == True:
            #     if button.status:
            #         is_close = False
            #         servo.rock()
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