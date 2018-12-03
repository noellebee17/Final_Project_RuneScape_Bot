# Final Project: RuneScape Bot
# Python Version 2.7.12
# OpenCV Version 3.4.3.18
# OpenCV Package "opencv-python"

import numpy as np
import cv2
import matplotlib.pyplot as plt
import pyautogui
import time
import serial


# Initiate communication with X-Carve.
def GRBL_I_SUMMON_THEE():
    # Open grbl serial port
    s = serial.Serial('COM3', 115200)

    # Open g-code file
    f = open('grbl.gcode', 'r');

    # Wake up grbl
    s.write("\r\n\r\n")
    time.sleep(2)  # Wait for grbl to initialize
    s.flushInput()  # Flush startup text in serial input

    # Stream g-code to grbl
    for line in f:
        l = line.strip()  # Strip all EOL characters for consistency
        print 'Sending: ' + l,
        s.write(l + '\n')  # Send g-code block to grbl
        grbl_out = s.readline()  # Wait for grbl response with carriage return
        print ' : ' + grbl_out.strip()

    # Switches screen from RuneScape to Pycharm, executes "Press <Enter>" command, and switches back.
    time.sleep(2)
    pyautogui.hotkey("altleft", "tab")
    time.sleep(2)
    pyautogui.press("enter")
    time.sleep(.5)
    pyautogui.hotkey("altleft", "tab")
    # Wait here until grbl is finished to close serial port and file.
    raw_input("  Press <Enter> to exit and disable grbl.")

    # Close file and serial port
    f.close()
    s.close()


# Takes a screenshot of the current screen.
def screen_shot():
    pic = pyautogui.screenshot()
    pic.save('imagefolder2/screenshot.png')


# Executes template matching.
def template_match(base_image, screenshot):
    x_w, y_h = base_image.shape[::-1]
    min_val = 1.0
    while min_val > 0.1:
        result = cv2.matchTemplate(screenshot, base_image, cv2.TM_SQDIFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    top_left = min_loc
    bottom_right = (top_left[0] + x_w, top_left[1] + y_h)
    cv2.rectangle(screenshot, top_left, bottom_right, 1, 5)

    bottom_right = (top_left[0] + x_w/2, top_left[1] + y_h/2)
    top_left = (top_left[0] + x_w / 2, top_left[1] + y_h / 2)
    cv2.rectangle(screenshot, top_left, bottom_right, 1, 5)
    mouse_position = pyautogui.position()
    distance = ((bottom_right[0] - mouse_position[0]), (bottom_right[1] - mouse_position[1]))
    print distance

    return bottom_right[0], bottom_right[1]


# Writes in grbl.gcode.
def write_gcode(x_error, y_error):
    f = open("grbl.gcode", "w+")
    f.write("G91 ")
    f.write("G1 X%.1f" % x_error)
    f.write(" Y%.1f" % y_error)
    f.write(" F1800")
    f.close()


# Performs PID loop.
def PID1(x_goal, y_goal):
    mouse_position = pyautogui.position()   # Get mouse position
    distance = ((x_goal - mouse_position[0]), (y_goal - mouse_position[1])) # Distance to target
    x_old = distance[0]
    y_old = distance[1]
    Kp = -5     # Reciprocal of Proportional Gain
    Kd = -10    # Reciprocal of Derivative Gain
    while 2 > 1:
        mouse_position = pyautogui.position()   # Get mouse position
        distance = ((x_goal - mouse_position[0]), (y_goal - mouse_position[1]))     # Distance to target
        print distance
        error_change = distance[0]-x_old, distance[1]-y_old     # Change of error
        change_p = (distance[0]/Kp), distance[1]/Kp     # Change to make from proportional
        change_d = error_change[0]/Kd, error_change[1]/Kd       # Change to make from derivative
        change = change_p[0]+change_d[0], change_p[1]+change_d[1]       # Total change
        write_gcode(-change[1], -change[0])     # Write g-code
        x_old = distance[0]     # Store old error
        y_old = distance[1]     # Store old error
        print "Error is: ", distance
        print "Change in error is: ", error_change
        print "Movement is: ", change
        print ""
        # pyautogui.moveRel(-change[0], -change[1], .2)
        GRBL_I_SUMMON_THEE()    # Send g-code to X-Carve

        if (-15 < mouse_position[0] - x_goal < 15 and -10 < mouse_position[1] - y_goal < 10):   # Click area
            pyautogui.click()
            print "TARGET HAS BEEN LOCATED!!?!??!?!?!?!?!"
            break


# Performs second PID loop with tighter parameters.
# Same comments as above.
def PID2(x_goal, y_goal):
    mouse_position = pyautogui.position()
    distance = ((x_goal - mouse_position[0]), (y_goal - mouse_position[1]))
    x_old = distance[0]
    y_old = distance[1]
    Kp = -5
    Kd = -10
    while 2 > 1:
        mouse_position = pyautogui.position()
        distance = ((x_goal - mouse_position[0]), (y_goal - mouse_position[1]))
        print distance
        error_change = distance[0]-x_old, distance[1]-y_old
        change_p = (distance[0]/Kp), distance[1]/Kp
        change_d = error_change[0]/Kd, error_change[1]/Kd
        change = change_p[0]+change_d[0], change_p[1]+change_d[1]
        write_gcode(-change[1], -change[0])
        x_old = distance[0]
        y_old = distance[1]
        print "Error is: ", distance
        print "Change in error is: ", error_change
        print "Movement is: ", change
        print ""
        # pyautogui.moveRel(-change[0], -change[1], .2)
        GRBL_I_SUMMON_THEE()

        if (-10 < mouse_position[0] - x_goal < 10 and -10 < mouse_position[1] - y_goal < 10):
            pyautogui.click()
            print "TARGET HAS BEEN LOCATED!!?!??!?!?!?!?!"
            break


def main():
    time.sleep(7)
    print "We have started!"
    screen_shot()

    # Fetch image repository
    bank = cv2.imread('imagefolder2/bank.png', 0)
    fletcher = cv2.imread('imagefolder2/fletcher.png', 0)
    inventory = cv2.imread('imagefolder2/target_inventory.png', 0)
    screenshot = cv2.imread('imagefolder2/screenshot.png', 0)
    bank_slot = cv2.imread('imagefolder2/bank_slot.PNG', 0)
    fletch_target = cv2.imread('imagefolder2/fletch_target.PNG', 0)

    # Endless loop
    while 1 < 2:
        screen_shot()
        screenshot = cv2.imread('imagefolder2/screenshot.png', 0)   # Update screenshot
        x_goal, y_goal = template_match(fletcher, screenshot)   # Find Target
        PID1(x_goal, y_goal)    # PID Loop
        time.sleep(2)
        screen_shot()
        screenshot = cv2.imread('imagefolder2/screenshot.png', 0)   # Update screenshot
        x_goal, y_goal = template_match(fletch_target, screenshot)   # Find Target
        PID1(x_goal, y_goal)    # PID Loop

        time.sleep(63)
        screen_shot()
        screenshot = cv2.imread('imagefolder2/screenshot.png', 0)   # Update screenshot
        x_goal, y_goal = template_match(inventory, screenshot)   # Confirm all items are made
        x_goal, y_goal = template_match(bank, screenshot)   # Find Target
        PID1(x_goal, y_goal)    # PID Loop

        time.sleep(2)
        screen_shot()
        screenshot = cv2.imread('imagefolder2/screenshot.png', 0)   # Update screenshot
        x_goal, y_goal = template_match(bank_slot, screenshot)   # Find Target
        PID2(x_goal, y_goal)    # PID Loop
        time.sleep(2)


if __name__ == "__main__":
    main()
