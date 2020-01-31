#based on https://pypi.org/project/paho-mqtt/#client
import paho.mqtt.client as mqtt
import time,ssl

topic = "Mini Project"
cert_path = "/home/zack/Desktop/System Internals Mini-Project/ca.crt"
broker = "3.82.77.12"

# The callback for when the client receives a CONN-ACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
    client.subscribe(topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    message = msg.topic+" - Message: "+(msg.payload).decode('utf-8')
    print(message)

if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.tls_set(cert_path, cert_reqs=ssl.CERT_NONE)
    client.username_pw_set("MQTT_user", password="MQTTServer")

    client.connect(broker, port=8883, keepalive=60)

    client.loop_forever()
