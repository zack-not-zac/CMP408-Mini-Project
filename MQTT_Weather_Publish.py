#!/usr/bin/env python3

#based on https://pypi.org/project/paho-mqtt/#client
import paho.mqtt.client as mqtt
import requests, json, sys, time, ssl

topic = "Mini Project"
cert_path = "./ca.crt"
broker = "3.82.77.12"
broker_port = 8883

# The callback for when the client receives a CONN-ACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
    client.subscribe(topic)

def on_publish(client, userdata, mid):
    print("Message Published")
    
def send_to_MQTT(msg):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.username_pw_set("MQTT_user", password="MQTTServer")
    client.tls_set(cert_path, cert_reqs=ssl.CERT_NONE)
    client.on_publish = on_publish

    client.connect(broker, port=broker_port, keepalive=60)
    client.publish(topic, payload=msg, qos=0, retain=False)
    client.disconnect()

def get_weather_data(city):         #based on: https://www.geeksforgeeks.org/python-find-current-weather-of-any-city-using-openweathermap-api/
    # Enter your API key here 
    api_key = "a634f496559253ffe79a96a1ca74d93e"
    # base_url variable to store url 
    url = "http://api.openweathermap.org/data/2.5/weather?"
    # Give city name 
    city_name = city 
    # complete_url variable to store 
    # complete url address 
    url += "APPID=" + api_key + "&q=" + city_name 
    # get method of requests module 
    # return response object 
    response = requests.get(url)
    # json method of response object convert json format data into python format data 
    x = response.json() 
    # Now x contains list of nested dictionaries 
    # Check the value of "cod" key is equal to 200, otherwise, prints error message and closes program
    if x["cod"] == 200: 
        # store the value of "main" key in variable y 
        y = x["main"] 
        # store the value corresponding to the "temp" key of y 
        current_temperature = y["temp"] 
        # store the value corresponding to the "humidity" key of y 
        current_humidity = y["humidity"] 
        # store the value of "weather" key in variable z 
        z = x["weather"] 
        # store the value corresponding to the "description" key at  the 0th index of z 
        weather_description = z[0]["description"] 
        #convert temperature from Kelvin to Celcius
        current_temperature = round(current_temperature - 273.15, 2)
        output = str(weather_description)
        output += ":" + str(current_temperature)
        output += ":" + str(current_humidity) + "%"
        return output
    else: 
        print("Failed: " + str(x))
        sys.exit()

if __name__ == "__main__":
    if len(sys.argv) != 2:   # if city name arg is missing
        print("Usage: " + sys.argv[0] + " [city name]")
    else:
        city = sys.argv[1]
        msg = get_weather_data(city)
        # msg FORMAT: [topic] - Message: [city]:[description]:[temperature]:[humidity]
        print("Current weather in " + city + ":" + msg)
        send_to_MQTT(city + ":" + msg)
