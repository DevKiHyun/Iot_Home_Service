import time, datetime, json, threading, sys, mydb, myschedule
import paho.mqtt.client as mqtt
sys.path.append('/home/nkh/IOT_test/api')
import weather
from myemail import Email
from socketIO_client import SocketIO
from apscheduler.schedulers.background import BackgroundScheduler

def connected_master(master):
    global connected_master_list

    if connected_master_list:
        for i in range(len(connected_master_list)):
            if connected_master_list[i][0] == master:
                connected_master_list[i][1] = connected_master_list[i][1] + 1
                break
            elif connected_master_list[i][0] != master and i == len(connected_master_list)-1:
                connected_master_list.append([master, 1])
                add_schedule(master)
    else:
        connected_master_list.append([master, 1])
        add_schedule(master)

def disconnected_master(master):
    global connected_master_list

    if connected_master_list:
        for i in range(len(connected_master_list)):
            if connected_master_list[i][0] == master:
                if connected_master_list[i][1] > 1:
                    connected_master_list[i][1] = connected_master_list[i][1] - 1
                    break
                else:
                    del connected_master_list[i]
                    delete_schedule(master)

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
        io.emit("message", "worker have no '{0}' method. Or Error in this method".format(method))

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
                print("{0} table does not exists".format(iot_name))
                Iot_Sensor.table_create(iot_name)
                Iot_Sensor.inspectdb()

            Iot_Sensor.insert_data(iot_name, dict["value"][name])
            print('{0} {1} {2}'.format(iot_name, str(dict["value"][name]),now))

    def run(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("192.168.0.13", 1883, 60)
        self.client.loop_forever()

def delete_schedule(master):
    global schedule, thread_job_list

    schedule_list = ['email_{0}', 'weather_{0}']
    for job_id in schedule_list:
        schedule.remove_job(job_id.format(master))

    for thread_job in thread_job_list:
        thread_job[1].do_run = False


def add_schedule(master):
    global schedule, thread_job_list, io
    thread_list = []

    thread_schedule_idle_email = threading.Thread(target = myschedule.schedule_idle_email, args = (master,))
    thread_list.append(thread_schedule_idle_email)

    for thread_func in thread_list:
        thread_job_list.append((master, thread_func))
        thread_func.do_run = True
        thread_func.start()

    myschedule.schedule_polling_email(master, init = True)
    schedule.add_job(myschedule.schedule_polling_email, 'interval', args = [master , False], minutes = 10, id = 'email_{0}'.format(master))
    schedule.add_job(myschedule.schedule_today_weather, 'interval', args = [master, io], minutes = 10, id = 'weather_{0}'.format(master))

def main():
    print(datetime.datetime.now())
    print("Worker starts work!")

    global connected_master_list, thread_job_list
    connected_master_list, thread_job_list = ([] for i in range(2))

    global myemail #, mysensor
    myemail = globals()['Email']()

    global schedule
    schedule = BackgroundScheduler()
    schedule.start()

    global io
    io = SocketIO('localhost', 8080)

    io.emit("connected_worker", "Worker")

    io.on("check_connected_master", connected_master)
    io.on("check_disconnected_master", disconnected_master)
    io.on("Worker", request_to_worker)
    io.wait()

if __name__ == "__main__":
    main()
