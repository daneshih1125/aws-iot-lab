#!/usr/bin/env python
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import logging
import json
import time
from awsConfig import *

shadowOnline = False
# Custom Shadow callback
def customGetCallback(payload, responseStatus, token):
    global shadowOnline
    print(responseStatus)
    if responseStatus != 'accepted':
        return
    shadowOnline = True
    payloadDict = json.loads(payload)
    print("++++++++GET++++++++++")
    try:
        if payloadDict['state']['desired']['motor_enable']:
            print("turn on motor")
        else:
            print("turn off motor")
    except Exception as e:
        print(str(e))
    print("++++++++GET++++++++++")


# Custom Shadow callback
def customShadowCallback_Delta(payload, responseStatus, token):
    if responseStatus != 'accepted':
        return
    payloadDict = json.loads(payload)
    print("++++++++DELTA++++++++++")
    try:
        if payloadDict['state']['motor_enable']:
            print("turn on motor")
        else:
            print("turn off motor")
    except Exception as e:
        print(str(e))
    print("++++++++DELTA++++++++++")

# Configure logging
#logger = logging.getLogger("AWSIoTPythonSDK.core")
#logger.setLevel(logging.DEBUG)
#streamHandler = logging.StreamHandler()
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#streamHandler.setFormatter(formatter)
#logger.addHandler(streamHandler)


myMQTTClient = AWSIoTMQTTClient(CLIENT_ID)
myMQTTClient.configureEndpoint(ENDPOINT, 8883)
myMQTTClient.configureCredentials(ROOT_CA, PRIVATE_KEY, CERT)
myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

myMQTTShadowClient = AWSIoTMQTTShadowClient(CLIENT_ID)
myMQTTShadowClient.configureEndpoint(ENDPOINT, 8883)
myMQTTShadowClient.configureCredentials(ROOT_CA, PRIVATE_KEY, CERT)
myMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
myMQTTShadowClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTShadowClient.configureMQTTOperationTimeout(5)  # 5 sec
myMQTTShadowClient.connect()
deviceShadowHandler = myMQTTShadowClient.createShadowHandlerWithName(AWS_THING, True)
deviceShadowHandler.shadowRegisterDeltaCallback(customShadowCallback_Delta)

retry = 0;
while retry < 5 and  shadowOnline == False:
    print("shadowGet!!!")
    deviceShadowHandler.shadowGet(customGetCallback, 3)
    time.sleep(10)
    retry += 1

myMQTTClient.connect()
topic = "iot/event/recv"
# Loop forever
while True:
    message = {
        'device_id':  DEVICE_ID,
        'created_at': int(time.time())
    }
    print("MQTT Publish " + topic)
    myMQTTClient.publish(topic, json.dumps(message), 0)
    time.sleep(300)
