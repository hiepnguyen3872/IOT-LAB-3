import serial.tools.list_ports
import json
import time
import paho.mqtt.client as mqttclient
print("IoT Gateway")

BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
mess = ""

# TODO: Add your token and your comport
# Please check the comport in the device manager
THINGS_BOARD_ACCESS_TOKEN = "kYeonyGsbSUVpOQzZcfA"

def getPort():
    ports = serial.tools.list_ports.comports()
    com_port = ""
    for i in range(0, len(ports)):
        port = ports[i]
        if "USB Serial Device" in str(port):
            com_port = (str(port).split(" ")[0])
    return com_port

bbc_port = getPort()

if len(bbc_port) > 0:
    ser = serial.Serial(port=bbc_port, baudrate=115200)

def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    print(splitData)
    # TODO: Add your source code to publish data to the server
    if splitData[1] == "TEMP":
        temp_status = {"temperature": splitData[2]}
        client.publish('v1/devices/me/telemetry', json.dumps(temp_status), 1)
    if splitData[1] == "LIGHT":
        light_status = {"light": splitData[2]}
        client.publish('v1/devices/me/telemetry', json.dumps(light_status), 1)


def readSerial():
    bytesToRead = ser.inWaiting()
    if (bytesToRead > 0):
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(mess[start:end + 1])
            if (end == len(mess)):
                mess = ""
            else:
                mess = mess[end+1:]


def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")


def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("utf-8"))
    temp_data = {'value': True}
    cmd = 1
    # TODO: Update the cmd to control 2 devices
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setLED":
            temp_data['valueLED'] = jsonobj['params']
            client.publish('v1/devices/me/attributes',json.dumps(temp_data), 1)
            cmd = '0' if(jsonobj['params']) else '1'

        if jsonobj['method'] == "setFAN":
            temp_data['valueFAN'] = jsonobj['params']
            client.publish('v1/devices/me/attributes',json.dumps(temp_data), 1)
            cmd = '2' if(jsonobj['params']) else '3'

    except:
        pass
    if len(bbc_port) > 0:
        print(bbc_port)
        ser.write((str(cmd) + "#").encode())


def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection is failed")


client = mqttclient.Client("Gateway_Thingsboard")
client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message


while True:
    if (len(bbc_port) > 0):
        readSerial()
    time.sleep(1)