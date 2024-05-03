from collections import deque
import board
import digitalio
from adafruit_rgb_display.st7789 import ST7789
import matplotlib.pyplot as plt
plt.style.use('ggplot')  # Use the 'ggplot' style
from PIL import Image, ImageDraw
from gpiozero import Device, Button, PWMLED
import time

from homeassistant_api import Client

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

weather_icons = {
    'clear-night': 'weather-night',
    'cloudy': 'weather-cloudy',
    'fog': 'weather-fog',
    'hail': 'weather-hail',
    'lightning': 'weather-lightning',
    'lightning-rainy': 'weather-lightning-rainy',
    'partlycloudy': 'weather-partly-cloudy',
    'pouring': 'weather-pouring',
    'rainy': 'weather-rainy',
    'snowy': 'weather-snowy',
    'snowy-rainy': 'weather-snowy-rainy',
    'sunny': 'weather-sunny',
    'windy': 'weather-windy',
    'windy-variant': 'weather-windy-variant',
    'exceptional': 'alert-circle-outline'
}

def update_display():
    global draw1, draw2, buffer1, buffer2

    # Clear the display
    disp.fill(0)

    # Redefine draw1 and draw2 after swapping buffers
    draw1, draw2 = draw2, draw1
    buffer1, buffer2 = buffer2, buffer1
    draw1 = ImageDraw.Draw(buffer1)

    with Client(
        'https://ha.belangerlab.ca/api',
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI1ZWM1MTJmODI1MGM0NDNkODM4MTZlNDhkYjdiODBkMCIsImlhdCI6MTcxMzU1OTg4NSwiZXhwIjoyMDI4OTE5ODg1fQ.Qh-mQlLjSjVAvOoRn1fugUayHlzg-GNKYiZtS1XDYMc'
    ) as client:


        weather = client.get_state(entity_id="weather.forecast_the_condo")

        # Get the MDI name for the current weather state
        mdi_name = weather_icons.get(weather.state, 'question-mark-circle-outline')

        # Draw the weather state and the corresponding MDI icon on the display
        weather_info = f"Weather: {weather.state}, Icon: {mdi_name}"
        draw1.text((0, 0), weather_info, fill=(255, 255, 255))

    # Display the buffer
    disp.image(buffer1)
    

try:
    print("Looping")
    while True:
        update_display()
        time.sleep(REFRESH_RATE)
except KeyboardInterrupt:
    print("Loop interrupted by user.")
finally:
    print("Exiting program.")
