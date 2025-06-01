# Install dependencies:
# circup install adafruit_hid neopixel

# Dino game link:
# https://chrome-dino-game.github.io/

import time
import board
import digitalio
import usb_hid
import analogio
import neopixel
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
                                          
# Built-in led on pin 25                                          
led = digitalio.DigitalInOut(board.GP25)
led.direction = digitalio.Direction.OUTPUT

# NeoPixe on pin 23
pixel = neopixel.NeoPixel(board.GP23, 1, brightness=0.3, auto_write=True)

# Built-in button on pin 24
button = digitalio.DigitalInOut(board.GP24)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

# light sensor on pin 26 (A0)
lightSensor = analogio.AnalogIn(board.A0)

keyboard = Keyboard(usb_hid.devices)

lightSensorMin = 65535
lightSensorMax = 0
lightSensorMid = (lightSensorMin + lightSensorMax) / 2

# Timeouts
lastPrintTime = time.monotonic()
lastJumpTime = time.monotonic()
lastLedUpdateTime = time.monotonic()
calibrationStartTime = time.monotonic()

# Main loop state flags
isCalibrated = False
isStarted = False
isFirstRun = True

# Main loop
while True:
    # light sensor reading
    lightSensorValueRaw = lightSensor.value
    lightSensorValue = False
    if lightSensorValueRaw > lightSensorMid:
        lightSensorValue = True
    
    if not isStarted:
        # Start calibration by button or at first run
        if not button.value or isFirstRun:
            isFirstRun = False
            isCalibrated = False
            isStarted = True
            lightSensorMin = 65535
            lightSensorMax = 0
            calibrationStartTime = time.monotonic()
            print('Calibration begin...')
            pixel[0] = (0, 255, 0)
            time.sleep(3)
        continue
        
    if not isCalibrated:
        # calibration
        if lightSensorValueRaw < lightSensorMin:
           lightSensorMin = lightSensorValueRaw
        if lightSensorValueRaw > lightSensorMax:
           lightSensorMax = lightSensorValueRaw
         
        # calibration finish condition
        if (not button.value or time.monotonic() - calibrationStartTime > 10):        
            isCalibrated = True
            lightSensorMid = (lightSensorMin + lightSensorMax) / 2
            print('Min: ', lightSensorMin, 'Max: ', lightSensorMax, 'Mid: ', lightSensorMid)
            print('Control loop begin...')
            pixel[0] = (0, 0, 0)
            time.sleep(2)
            # break
        
        # update led
        if time.monotonic() - lastLedUpdateTime > 0.1:
            led.value = not led.value
            pixel[0] = (0, 255, 0) if pixel[0] == (0, 0, 0) else (0, 0, 0)  
            lastLedUpdateTime = time.monotonic()        
    
    if isCalibrated:
        # exit main loop condition
        if not button.value and isCalibrated:
            isStarted = False
            print('Stop... Press key to restart')
            pixel[0] = (0, 0, 0)
            time.sleep(3)
            # break 
        
        # update led
        led.value = lightSensorValue 
        pixel[0] = (0, 255, 0) if lightSensorValue else (0, 0, 0)     
        
        # jump by condition
        if (lightSensorValue or time.monotonic() - lastJumpTime > 3):
            time.sleep(0.05)
            print(lightSensorValue, '\t', lightSensorValueRaw, '\t jump')
            keyboard.send(Keycode.SPACE)
            lastJumpTime = time.monotonic()
            # time.sleep(0.01)
    
    # print light sensor data
    if time.monotonic() - lastPrintTime > 0.3:    
        print(lightSensorValue, '\t', lightSensorValueRaw)
        lastPrintTime = time.monotonic()
    
    #keyboard.send(Keycode.ENTER)  
    # time.sleep(0.2)



