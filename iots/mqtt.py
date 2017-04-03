import paho.mqtt.client as mqtt
import json, datetime, pymysql, os, mydb

class Sensor_Table:
    cur = mydb.cur
    db = mydb.db

    def table_create(self, table_name):
        self.query = """
        CREATE TABLE IF NOT EXISTS %s(
        id serial NOT NULL PRIMARY KEY,
        sensor_data VARCHAR(100),
        pub_date DATETIME)
        """ % table_name
        self.cur.execute(self.query)

    def table_check(self, table_name):
        self.cur.execute("SHOW TABLES")
        result = self.cur.fetchall()
        table_list = []

        for row in result:
            if 'iot_' in row[0] :
                table_list.append(row[0])
        return (table_name in table_list)

    def insert_data(self, table_name, value):
        self.cur.execute("INSERT INTO %s (sensor_data, pub_date) VALUES(%d, NOW())" %(table_name, value))
        self.db.commit()
        #print("save")

    def inspectdb(self):
        table_list = []
        self.cur.execute("SHOW TABLES")
        result = self.cur.fetchall()
        for row in result:
            if 'iot_' in row[0] :
                table_list.append(row[0])
        os.system("python manage.py inspectdb %s > iots/models.py" % " ".join(table_list))
        os.system("python manage.py migrate")

def on_connect(client, userdata, flag, rc) :
    print("Connected with result coe " + str(rc))
    print(str(flag))
    client.subscribe("#", 0)

def on_message(client, userdata, msg):
    check_table = True
    Iot_Sensor = Sensor_Table()

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

        if check_table == False:
            Iot_Sensor.inspectdb()
            print(check)
        Iot_Sensor.insert_data(iot_name, dict["value"][name])
        print(iot_name + " " + str(dict["value"][name]) + " " + str(now))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.0.13", 1883, 60)
client.loop_forever()
