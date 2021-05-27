import logging
import threading
import time
# import ThingSpeak Library
import thingspeak
# import evdev for controller data
from evdev import InputDevice, categorize, ecodes
# import pi-top and robotics stuff
from pitop.pma import EncoderMotor, ForwardDirection, BrakingType, ServoMotor
from pitop import Pitop

# Setting up the ThingSpeak variables
channel_id = 0000000 # PUT CHANNEL ID HERE
write_key  = 'xxxxxxxxxxxxxxxx' # PUT YOUR WRITE KEY HERE
channel = thingspeak.Channel(id=channel_id, api_key=write_key)

# Setup the motors and battery
lmotor = EncoderMotor("M0", ForwardDirection.CLOCKWISE)
rmotor = EncoderMotor("M3", ForwardDirection.COUNTER_CLOCKWISE)
bat = Pitop().battery

# Setting braking_type will change the way the motor stops.
# BrakingType.COAST will make the motor coast to a halt when stopped.
# BrakingType.BRAKE will cause the motor to actively brake when stopped.
# In practice you may not notice much. It's subtle to say the least.
lmotor.braking_type = BrakingType.COAST
rmotor.braking_type = BrakingType.COAST

# creates object 'gamepad' to store the data
# you can call it whatever you like
# use python /usr/local/lib/python3.7/dist-packages/evdev/evtest.py 
# to find the correct path to the controller
gamepad = InputDevice('/dev/input/event3')

# button code variables (change to suit your device)
# uncomment the ones you need to use

# Buttons
# aBtn = 304
# bBtn = 305
# xBtn = 307
# yBtn = 308
# hBtn = 316
# dPady = 17
# dPadx = 16
# start = 315
# select = 158

# Joysticks
lSticky = 1
lStickx = 0
# lStickc = 317
rSticky = 5
rStickx = 2
# rStickc = 218

# Triggers
lTrig = 10
# lBump = 310
rTrig = 9
# rBump = 311

def robot_control(gamepad=gamepad):
    # Function for controlling the the pi-top motors using a
    # Microsoft Xbox One Controller via Bluetooth
    # This is executed in a seperate thread of its own
    for event in gamepad.read_loop():
        if event.type == 1:  
            # If the event is a digital control, a button
            # event type 1, run the code here
            print("Nothing to do")
        elif event.type == 3:
            # If the event is an analog control, a joystick/trigger
            # event type 1, run the code here
            if event.code == lSticky:
                # Looks at the controller data for the left analog joystick
                if event.value <= 25000:
                    # Gets the value data of the left analog stick and converts it
                    # to a 0-100 scale and sets the motor RPM to a +ve number
                    val = 100-((event.value / 25000)*100)
                    perc = round(val,0)
                    lmotor.set_target_rpm(perc)
                elif event.value >= 40535:
                    # Gets the value data of the left analog stick and converts it
                    # to a 0-100 scale and sets the motor RPM to a -ve number
                    val = ((event.value - 40535) / 25000)*100
                    perc = round(val,0)
                    lmotor.set_target_rpm(-perc)
                else:
                    # stops the motoer if the analog stick is between 25001 and 40535
                    # Also known as a deadzone
                    lmotor.stop()            

            if event.code == rSticky:
                # Looks at the controller data for the right analog joystick
                if event.value <= 25000:
                    # Gets the value data of the right analog stick and converts it
                    # to a 0-100 scale and sets the motor RPM to a +ve number
                    val = 100-((event.value / 25000)*100)
                    perc = round(val,0)
                    rmotor.set_target_rpm(perc)
                elif event.value >= 40535:
                    # Gets the value data of the right analog stick and converts it
                    # to a 0-100 scale and sets the motor RPM to a -ve number
                    val = ((event.value - 40535) / 25000)*100
                    perc = round(val,0)
                    rmotor.set_target_rpm(-perc)
                else:
                    # stops the motoer if the analog stick is between 25001 and 40535
                    # Also known as a deadzone
                    rmotor.stop()

def iot_data(channel=channel):
    # This function gets the data from the pi-tip robotics motors and pi-tops battery
    # It will also collect the data and submt it to ThingSpeak every 15 seconds, a limitation
    # for a free account, this can be changed down to 1 second if using a paid account
    while True:
        print(f"Left Motor")
        print(f"Speed:  {lmotor.current_speed}\tRPM : {lmotor.current_rpm}\tDistance : {lmotor.distance}")
        print(f"Right Motor")
        print(f"Speed:  {rmotor.current_speed}\tRPM : {rmotor.current_rpm}\tDistance : {rmotor.distance}")
        print(f"Battery : {bat.capacity}")
        time.sleep(15)
        response = channel.update({'field1': lmotor.current_speed, 
                                   'field2': lmotor.current_rpm,
                                   'field3': lmotor.distance,
                                   'field4': rmotor.current_speed, 
                                   'field5': rmotor.current_rpm,
                                   'field6': rmotor.distance,
                                   'field7': bat.capacity})


if __name__ == "__main__":
    x1 = threading.Thread(target=robot_control)
    x2 = threading.Thread(target=iot_data)
    x1.start()
    x2.start()
    x1.join()
    x2.join()

