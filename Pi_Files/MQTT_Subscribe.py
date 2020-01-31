#!/usr/bin/env python3

#based on https://pypi.org/project/paho-mqtt/#client
import paho.mqtt.client as mqtt
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import time,threading, sys, os, ssl

disp_time = ""
disp_message = ""
topic = "Mini Project"
cert_path = "./ca.crt"
broker = "3.82.77.12"
broker_port = 8883

def initialise_oled():
    # Define the Reset Pin
    oled_reset = digitalio.DigitalInOut(board.D4)

    # Change these
    # to the right size for your display!
    WIDTH = 128
    HEIGHT = 64     # Change to 64 if needed
    BORDER = 3

    # Use for SPI
    spi = board.SPI()
    oled_cs = digitalio.DigitalInOut(board.D5)
    oled_dc = digitalio.DigitalInOut(board.D6)
    oled = adafruit_ssd1306.SSD1306_SPI(WIDTH, HEIGHT, spi, oled_dc, oled_reset, oled_cs)

    return oled

# draws information on the SSD1306 128x64 OLED display (source: https://learn.adafruit.com/monochrome-oled-breakouts/python-usage-2)
def draw_on_display():
    oled = initialise_oled()
    font_size = 14

    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    image = Image.new('1', (oled.width, oled.height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Load default font.
    # font = ImageFont.load_default()

    # Load custom font
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', font_size)
    
    # print some text in the middle of the display
    # (font_width, font_height) = font.getsize(message)
    # draw.text((oled.width//2 - font_width//2, oled.height//2 - font_height//2), message, font=font, fill=255)
    
    # print clock on top of display, centered vertically
    (font_width, font_height) = font.getsize(disp_time)
    draw.text((oled.width//2 - font_width//2, 0), disp_time, font=font, fill=255)

    # print weather in centre of display under clock
    if disp_message:
        border = 2 # 2 pixel border for chars with tails (j,y,p,g, etc.)
        text = disp_message.splitlines()
        # print location in centre of display under clock (line 1)
        (font_width, font_height) = font.getsize(text[0])
        draw.text((oled.width//2 - font_width//2, 0 + font_size), text[0], font=font, fill=255)
        # print temperature on next line down, centered (line 2)
        (font_width, font_height) = font.getsize(text[1])
        draw.text((oled.width//2 - font_width//2, (0 + font_size*2) + border), text[1], font=font, fill=255)
        # print weather description on bottom line (line)
        (font_width, font_height) = font.getsize(text[2])
        draw.text((oled.width//2 - font_width//2, (0 +  font_size*3) + border), text[2], font=font, fill=255)

    # Display image
    oled.image(image)
    oled.show()

# The callback for when the client receives a CONN-ACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
    client.subscribe(topic)

def blink_led():
    os.system("/home/pi/Pi_Files/LED_Control.bin togglepin 12 250 6")    # toggles pin 12 3 times

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global disp_message
    message = msg.topic+" - Payload: "
    payload = msg.payload.decode('utf-8')
    message += payload

    # payload FORMAT: [city]:[description]:[temperature]:[humidity]
    s = payload.split(':')
    print(s)
    text = s[0] + "\n" + s[2] + "°C" + "\n" + s[1]
    if disp_message != text:
        disp_message = text
        draw_on_display()

    led_thread = threading.Thread(target=blink_led)
    led_thread.start()
    led_thread.join()

def print_time():
    global disp_time
    while True:
        localtime = time.localtime()
        result = time.strftime("%H:%M", localtime)
        if result != disp_time:
            disp_time = result
            draw_on_display()
        time.sleep(1)

def connect_to_MQTT():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set("MQTT_user", password="MQTTServer")
    client.tls_set(cert_path,cert_reqs=ssl.CERT_NONE)
    client.connect(broker, broker_port, 60)

    client.loop_forever()

if __name__ == "__main__":
    clock_thread = threading.Thread(target=print_time)
    MQTT_thread = threading.Thread(target=connect_to_MQTT)
    try:
        clock_thread.start()
        MQTT_thread.start()
    except KeyboardInterrupt:
        clock_thread.join()
        MQTT_thread.join()
        sys.exit()