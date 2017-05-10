from socketIO_client import SocketIO
from myemail import Email
import time, datetime, json, mydb
import paho.mqtt.client as mqtt

def request_to_worker(data):
    global myemail, io

    method = data["method"]
    call_method = None

    try:
        if hasattr(myemail, method):
            call_method = getattr(myemail, method)
        #elif hasattr(mysensor, method):
        call_method(data["master"], data["data"])

    except Exception as e:
        print(e)
        print("Have no method or Error in this method ")
        io.emit("message", "worker have no '%s' method.Or Error in this method" %method)

class Sensor(threading.Thread):
    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.io = socket

    def on_connect(self, client, userdata, flag, rc) :
        print("Connected with result coe " + str(rc))
        print(str(flag))
        client.subscribe("#", 0)

    def on_message(self, client, userdata, msg):
        Iot_Sensor = mydb.Sensor_Table(mydb.get_db())

        now = datetime.datetime.now().replace(microsecond = 0)
        msg.payload = msg.payload.decode("utf-8")
        dict = json.loads(msg.payload)
        iot_topic = "iot_" + dict["place"].replace("/","_") + "_"

        print("Topic: " + msg.topic + '\nMessage: ' + msg.payload)

        for name in dict["value"].keys():
            iot_name = iot_topic + name
            if Iot_Sensor.table_check(iot_name) == False:
                check_table = False
                print("%s table does not exists" % iot_name)
                Iot_Sensor.table_create(iot_name)
                Iot_Sensor.inspectdb()

            Iot_Sensor.insert_data(iot_name, dict["value"][name])
            print(iot_name + " " + str(dict["value"][name]) + " " + str(now))

    def run(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("192.168.0.13", 1883, 60)
        self.client.loop_forever()


print(datetime.datetime.now())
print("Worker starts work!")

global myemail #, mysensor
myemail = globals()['Email']()

global io
io = SocketIO('localhost', 8080)
io.emit("connected", "Worker")
io.on("Worker", request_to_worker)
io.wait()
