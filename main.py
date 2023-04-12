#
# Pico pump control
#
# version 1.0
#
# @author: Norbert Babineti
#

from machine import Pin
import utime

# Define pins
# Sensors (input)
sensor_1 = Pin(14, Pin.IN, Pin.PULL_UP)
sensor_2 = Pin(17, Pin.IN, Pin.PULL_UP)

# Pump (output)
pump = Pin(6, Pin.OUT)

# LEDs (output)
green_led = Pin(28, Pin.OUT, value=1)
red_led = Pin(22, Pin.OUT)

# Buttons (input)
water_level_reset_button = Pin(9, Pin.IN, Pin.PULL_UP)
    

# Constants
# Max global pump runtime before reset in seconds
MAX_GLOBAL_PUMP_RUNTIME = 55

# Variables
pump_start_time_seconds = 0
pump_stop_time_seconds = 0
global_pump_runtime_after_water_level_reset = 0
pump_on_time_start_ms = 0
pump_on_time_end_ms = 0
last_pump_status = 0
pump_on = False

# Main Loop
while True:        
    # Save the pump start time if the sensor is triggered and the pump is not already running
    if (sensor_1.value() == 0 or sensor_2.value() == 0) and pump_start_time_seconds == 0:
        pump_start_time_seconds = utime.time()
    # Check if the sensor is triggered and the pump start time has been recorded
    elif (sensor_1.value() == 0 or sensor_2.value() == 0) and pump_start_time_seconds != 0:
        # Check if the pump has been running for less than 3 seconds and the global pump runtime is less than the max
        if (utime.time() - pump_start_time_seconds < 3) and global_pump_runtime_after_water_level_reset < MAX_GLOBAL_PUMP_RUNTIME:
            # Turn the pump on
            pump.value(1)
            pump_on = True
        # Check if the maximul global pump runtime has been reached
        elif global_pump_runtime_after_water_level_reset > MAX_GLOBAL_PUMP_RUNTIME:
            # Turn the pump off
            pump.value(0)
            pump_on = False
            # Change LED indication to red
            green_led.value(0)
            red_led.value(1)
        # Turn off pump if it has been running for more than 3 seconds
        else:
            pump.value(0)
            pump_on = False
            if pump_stop_time_seconds == 0:
                pump_stop_time_seconds = utime.time()          
    # Turn off the pump if the sensor is not triggered
    else:
        pump.value(0)
        pump_on = False
        pump_start_time_seconds = 0
        last_sensor_status = 0
        
    # If sesort is triggered and the pump stopped more than 3 seconds ago, reset pump start time and stop time to 0 so the pump can be turned on again
    if (sensor_1.value() == 0 or sensor_2.value() == 0) and pump_stop_time_seconds != 0:
        if (utime.time() - pump_stop_time_seconds > 3) and global_pump_runtime_after_water_level_reset < MAX_GLOBAL_PUMP_RUNTIME:
            pump_start_time_seconds = 0
            pump_stop_time_seconds = 0    
    
    # Calculate the global pump runtime after the water level reset button is pressed
    if pump_on == True and last_pump_status == 0:
        pump_on_time_start_ms = utime.ticks_ms()
        last_pump_status = 1
    elif pump_on == False and last_pump_status == 1:
        # timestamp when pump is turned off
        pump_on_time_end_ms = utime.ticks_ms()
        # calculate the time the pump was on in milliseconds
        pump_time_on_in_ms = utime.ticks_diff(pump_on_time_end_ms, pump_on_time_start_ms)
        # convert milliseconds to seconds
        pump_on_time_in_seconds = pump_time_on_in_ms/1000
        # add the pump runtime to the global pump runtime
        global_pump_runtime_after_water_level_reset += pump_on_time_in_seconds
        # reset the pump on time start and end variables
        last_pump_status = 0
    else:
        pass
            
    # Reset global pump runtime if the water level reset button is pressed
    while water_level_reset_button.value() == 0:
        global_pump_runtime_after_water_level_reset = 0
        red_led.value(0)
        green_led.value(1)
        utime.sleep(2)
