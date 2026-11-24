import time
import time as t
import json
import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT
from flask import *
import threading
import time
import logging

finalJson = "["

def thread_function(name):
    global finalJson
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,datefmt="%H:%M:%S")
    logging.info("Main    : before creating thread")
    while True:
        myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(CLIENT_ID)
        myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
        myAWSIoTMQTTClient.configureCredentials(PATH_TO_AMAZON_ROOT_CA_1, PATH_TO_PRIVATE_KEY, PATH_TO_CERTIFICATE)

        # AWSIoTMQTTClient connection configuration
        myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
        myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
        myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
        myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
        myAWSIoTMQTTClient.connect()
        myAWSIoTMQTTClient.subscribe(TOPIC1, 1, customCallback)
        print(finalJson + "]")
        message = {}
        messageJson = json.dumps(message)

app = Flask(__name__)

# Define ENDPOINT, CLIENT_ID, PATH_TO_CERTIFICATE, PATH_TO_PRIVATE_KEY, PATH_TO_AMAZON_ROOT_CA_1, MESSAGE, TOPIC, and RANGE
ENDPOINT = "a1pzx5ezyzy051-ats.iot.ca-central-1.amazonaws.com"
CLIENT_ID = "testDevice"
PATH_TO_CERTIFICATE = "C:/Users/shima/Desktop/concordia/1a4d75b138fb1a4eceec4ab6a28f091a164ddebdb5f3c3ce258f5dc7ba427a2e-certificate.pem.crt"
PATH_TO_PRIVATE_KEY = "C:/Users/shima/Desktop/concordia/1a4d75b138fb1a4eceec4ab6a28f091a164ddebdb5f3c3ce258f5dc7ba427a2e-private.pem.key"
PATH_TO_AMAZON_ROOT_CA_1 = "C:/Users/shima/Desktop/concordia/AmazonRootCA1.pem"
MESSAGE = "Switch"
TOPIC = "mTopic"
TOPIC1 = "outTopic"
RANGE = 20

# Connect and subscribe to AWS IoT

def customCallback(client, userdata, message):
    global finalJson
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")
    temp = str(message.payload)
    temp = temp[2:(len(temp) - 1)]
    print(temp)
    if finalJson != "[":
        finalJson += ","
    finalJson += "\n" + temp
    print("inj")
    print(finalJson + "]")
    with open("C:/Users/shima/PycharmProjects/IoTDashboard/data_file.json", "w") as write_file:
        write_file.write(finalJson + "]")
        print("write")
    return
    json_object = json.dumps(message.payload)
    print(json_object)
    with open("C:/Users/shima/PycharmProjects/IoTDashboard/data_file.json", "a") as write_file:
        write_file.write(json_object)
        print("write")
@app.route('/Setpoint', methods=['POST', 'GET'])
def Setpoint():
    if request.method == 'POST':
        set = request.form['setpoint']
        set1= int(set) -1
        format = "%(asctime)s: %(message)s"
        logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
        logging.info("Main 2    : before creating thread")
        # data = "{} [{}]".format(MESSAGE,"ON")
        myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(CLIENT_ID)
        myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
        myAWSIoTMQTTClient.configureCredentials(PATH_TO_AMAZON_ROOT_CA_1, PATH_TO_PRIVATE_KEY, PATH_TO_CERTIFICATE)

        # AWSIoTMQTTClient connection configuration
        myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
        myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
        myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
        myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
        myAWSIoTMQTTClient.connect()
        flag2 = 1
        message = {'Device_ID': 'esp32_609F1C', 'Fan': 0, 'Heater': 0, 'Flag1': 1, 'Flag2': flag2, 'Temp': float(set1),'Setpoint': float(set), 'time_stamp': 2600}
        myAWSIoTMQTTClient.publish(TOPIC1, json.dumps(message), 1)
        print("Published: '" + json.dumps(message) + "' to the topic: " + "'outTopic'")

        return redirect(request.referrer)
    else:
        set = request.args.get('setpoint')
        set1= int(set) -1
        format = "%(asctime)s: %(message)s"
        logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
        logging.info("Main 2    : before creating thread")
        # data = "{} [{}]".format(MESSAGE,"ON")
        myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(CLIENT_ID)
        myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
        myAWSIoTMQTTClient.configureCredentials(PATH_TO_AMAZON_ROOT_CA_1, PATH_TO_PRIVATE_KEY, PATH_TO_CERTIFICATE)

        # AWSIoTMQTTClient connection configuration
        myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
        myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
        myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
        myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
        myAWSIoTMQTTClient.connect()
        message = {'Device_ID': 'esp32_609F1C', 'Fan': 0, 'Heater': 0, 'Flag1': 1, 'Flag2': 1, 'Temp': float(set1),'Setpoint': float(set), 'time_stamp': 2600}
        myAWSIoTMQTTClient.publish(TOPIC1, json.dumps(message), 1)
        print("Published: '" + json.dumps(message) + "' to the topic: " + "'outTopic'")

        return redirect(request.referrer)



@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        state = request.form['state']
        if state == '1' :
            x = threading.Thread(target=thread_function, args=(1,))
            x.start()
            return redirect(request.referrer)
        if state=='2':
            format = "%(asctime)s: %(message)s"
            logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
            logging.info("Main 2    : before creating thread")
            # data = "{} [{}]".format(MESSAGE,"ON")
            myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(CLIENT_ID)
            myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
            myAWSIoTMQTTClient.configureCredentials(PATH_TO_AMAZON_ROOT_CA_1, PATH_TO_PRIVATE_KEY, PATH_TO_CERTIFICATE)

            # AWSIoTMQTTClient connection configuration
            myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
            myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
            myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
            myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
            myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
            myAWSIoTMQTTClient.connect()
            message = 1
            myAWSIoTMQTTClient.publish(TOPIC, json.dumps(message), 1)
            print("Published: '" + json.dumps(message) + "' to the topic: " + "'inTopic'")

            return redirect(request.referrer)
        if state=='3':
            format = "%(asctime)s: %(message)s"
            logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
            logging.info("Main  3  : before creating thread")
            # data = "{} [{}]".format(MESSAGE,"OFF")
            myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(CLIENT_ID)
            myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
            myAWSIoTMQTTClient.configureCredentials(PATH_TO_AMAZON_ROOT_CA_1, PATH_TO_PRIVATE_KEY, PATH_TO_CERTIFICATE)

            # AWSIoTMQTTClient connection configuration
            myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
            myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
            myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
            myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
            myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
            myAWSIoTMQTTClient.connect()
            message =  0
            myAWSIoTMQTTClient.publish(TOPIC, json.dumps(message), 1)
            print("Published: '" + json.dumps(message) + "' to the topic: " + "'inTopic'")

            return redirect(request.referrer)
        if state=='4':
            format = "%(asctime)s: %(message)s"
            logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
            logging.info("Main 2    : before creating thread")
            # data = "{} [{}]".format(MESSAGE,"ON")
            myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(CLIENT_ID)
            myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
            myAWSIoTMQTTClient.configureCredentials(PATH_TO_AMAZON_ROOT_CA_1, PATH_TO_PRIVATE_KEY, PATH_TO_CERTIFICATE)

            # AWSIoTMQTTClient connection configuration
            myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
            myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
            myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
            myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
            myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
            myAWSIoTMQTTClient.connect()
            message = 3
            myAWSIoTMQTTClient.publish(TOPIC, json.dumps(message), 1)
            print("Published: '" + json.dumps(message) + "' to the topic: " + "'inTopic'")
        if state == '5':
            format = "%(asctime)s: %(message)s"
            logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
            logging.info("Main 2    : before creating thread")
            # data = "{} [{}]".format(MESSAGE,"ON")
            myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(CLIENT_ID)
            myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
            myAWSIoTMQTTClient.configureCredentials(PATH_TO_AMAZON_ROOT_CA_1, PATH_TO_PRIVATE_KEY,
                                                    PATH_TO_CERTIFICATE)

            # AWSIoTMQTTClient connection configuration
            myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
            myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
            myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
            myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
            myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
            myAWSIoTMQTTClient.connect()
            message = 2
            myAWSIoTMQTTClient.publish(TOPIC, json.dumps(message), 1)
            print("Published: '" + json.dumps(message) + "' to the topic: " + "'mTopic'")
            return redirect(request.referrer)
    else:
        state = request.args.get('state')

        if state == '1':
            format = "%(asctime)s: %(message)s"
            logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
            logging.info("  : before creating thread")
            x = threading.Thread(target=thread_function, args=(1,))
            x.start()
            return redirect(request.referrer)
        if state == '2':
            format = "%(asctime)s: %(message)s"
            logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
            logging.info("Main  22  : before creating thread")
            # data = "{} [{}]".format(MESSAGE,"ON")
            myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(CLIENT_ID)
            myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
            myAWSIoTMQTTClient.configureCredentials(PATH_TO_AMAZON_ROOT_CA_1, PATH_TO_PRIVATE_KEY, PATH_TO_CERTIFICATE)

            # AWSIoTMQTTClient connection configuration
            myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
            myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
            myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
            myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
            myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
            myAWSIoTMQTTClient.connect()
            message = 1
            myAWSIoTMQTTClient.publish(TOPIC, json.dumps(message), 1)
            print("Published: '" + json.dumps(message) + "' to the topic: " + "'inTopic'")

            return redirect(request.referrer)
        if state == '3':
            format = "%(asctime)s: %(message)s"
            logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
            logging.info("Main  33  : before creating thread")
            # data = "{} [{}]".format(MESSAGE,"OFF")
            myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(CLIENT_ID)
            myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
            myAWSIoTMQTTClient.configureCredentials(PATH_TO_AMAZON_ROOT_CA_1, PATH_TO_PRIVATE_KEY, PATH_TO_CERTIFICATE)

            # AWSIoTMQTTClient connection configuration
            myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
            myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
            myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
            myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
            myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
            myAWSIoTMQTTClient.connect()
            message = 0
            myAWSIoTMQTTClient.publish(TOPIC, json.dumps(message), 1)
            print("Published: '" + json.dumps(message) + "' to the topic: " + "'inTopic'")

            return redirect(request.referrer)
        if state=='4':
            format = "%(asctime)s: %(message)s"
            logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
            logging.info("Main 2    : before creating thread")
            # data = "{} [{}]".format(MESSAGE,"ON")
            myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(CLIENT_ID)
            myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
            myAWSIoTMQTTClient.configureCredentials(PATH_TO_AMAZON_ROOT_CA_1, PATH_TO_PRIVATE_KEY, PATH_TO_CERTIFICATE)

            # AWSIoTMQTTClient connection configuration
            myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
            myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
            myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
            myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
            myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
            myAWSIoTMQTTClient.connect()
            message = 3
            myAWSIoTMQTTClient.publish(TOPIC, json.dumps(message), 1)
            print("Published: '" + json.dumps(message) + "' to the topic: " + "'inTopic'")
        if state == '5':
            format = "%(asctime)s: %(message)s"
            logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
            logging.info("Main 2    : before creating thread")
            # data = "{} [{}]".format(MESSAGE,"ON")
            myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(CLIENT_ID)
            myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
            myAWSIoTMQTTClient.configureCredentials(PATH_TO_AMAZON_ROOT_CA_1, PATH_TO_PRIVATE_KEY,
                                                    PATH_TO_CERTIFICATE)

            # AWSIoTMQTTClient connection configuration
            myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
            myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
            myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
            myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
            myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
            myAWSIoTMQTTClient.connect()
            message = 2
            myAWSIoTMQTTClient.publish(TOPIC, json.dumps(message), 1)
            return redirect(request.referrer)

# while True:
#     myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(CLIENT_ID)
#     myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
#     myAWSIoTMQTTClient.configureCredentials(PATH_TO_AMAZON_ROOT_CA_1, PATH_TO_PRIVATE_KEY, PATH_TO_CERTIFICATE)
#
#     # AWSIoTMQTTClient connection configuration
#     myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
#     myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
#     myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
#     myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
#     myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
#     myAWSIoTMQTTClient.connect()
#
#     print("inj")






if __name__ == '__main__':
    app.run(debug=True)



