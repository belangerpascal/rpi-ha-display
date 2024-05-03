from collections import deque
import os
import sys
import psutil
import board
import digitalio
from adafruit_rgb_display.st7789 import ST7789
import matplotlib.pyplot as plt
plt.style.use('ggplot')  # Use the 'ggplot' style
from PIL import Image, ImageDraw, ImageFont
from gpiozero import Device, Button, PWMLED
import time
import socket
import platform
#import docker
#dockerClient = docker.DockerClient()

from homeassistant_api import Client

with Client(
    'https://ha.belangerlab.ca/api',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI1ZWM1MTJmODI1MGM0NDNkODM4MTZlNDhkYjdiODBkMCIsImlhdCI6MTcxMzU1OTg4NSwiZXhwIjoyMDI4OTE5ODg1fQ.Qh-mQlLjSjVAvOoRn1fugUayHlzg-GNKYiZtS1XDYMc'
) as client:

    light = client.get_domain("light")

    light.turn_on(entity_id="light.living_room_lamp")

#    weather = client.get_domain("weather")

    forecast = client,get_state("weather.forecast_the_condo")


backlight_pin = 18
backlight = PWMLED(backlight_pin)

def set_backlight_intensity(intensity):
    # Check that the intensity is within the valid range
    if 0 <= intensity <= 1:
        backlight.value = intensity
    else:
        print("Error: Intensity must be between 0 and 1")

# Now you can control the backlight intensity by calling the function
# For example, to set the backlight intensity to 50%

# User Config
REFRESH_RATE = 0.033
HIST_SIZE = 61


# Setup display
disp = ST7789(board.SPI(), height=280, width=280, y_offset=20, rotation=90,
                     baudrate=40000000,
                     cs=digitalio.DigitalInOut(board.CE0),
                     dc=digitalio.DigitalInOut(board.D25),
                     rst=digitalio.DigitalInOut(board.D27))

buffer1 = Image.new('RGB', (280, 240))
buffer2 = Image.new('RGB', (280, 240))
draw1 = ImageDraw.Draw(buffer1)
draw2 = ImageDraw.Draw(buffer2)

#def getContainers():
#    containersReturn = []
#    containers = dockerClient.containers.list()
#    for container in containers:
#        if ("ceph" not in container.name):
#          containersReturn.append(container.name.split(".", 1)[0])
#    return containersReturn

def update_data_disk():
    global draw1, draw2, buffer1, buffer2, prev_disk_activity

    # Redefine draw1 and draw2 after swapping buffers
    draw1, draw2 = draw2, draw1
    buffer1, buffer2 = buffer2, buffer1
    draw1 = ImageDraw.Draw(buffer1)

    # Get the current disk activity
    disk_activity = psutil.disk_io_counters()

    # Clear the buffer
    draw1.rectangle((0, 0, 280, 240), fill=(0, 0, 0))

    # If the disk is active, display the active image
    if disk_activity.read_count > prev_disk_activity.read_count or disk_activity.write_count > prev_disk_activity.write_count:
        # Resize the image to 50x50 pixels
        small_active_image = disk_active_image.resize((50, 50))
        # Display the image in the bottom right corner
        buffer1.paste(small_active_image, (210, 170))
        # Turn on the backlight
        set_backlight_intensity(0.5)
    else:
        # If the disk is idle, turn off the backlight
        set_backlight_intensity(0.5)

    # Display the buffer
    disp.image(buffer1)

    # Update the previous disk activity counters
    prev_disk_activity = disk_activity
    set_backlight_intensity(0.5)

def update_display():
    

try:
    print("Looping")
    while True:
        update_display()
        time.sleep(REFRESH_RATE)
except KeyboardInterrupt:
    print("Loop interrupted by user.")
finally:
    pin7.close()
    print("Exiting program.")
