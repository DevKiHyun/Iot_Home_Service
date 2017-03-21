import paho.mqtt.client as mqtt
import json, datetime, pymysql, os, iot_mysqldb

class Sensor_Table:
    cur = iot_mysqldb.cur

    # If the DB_table doex not exist, then create a table about sensor data
    def table_create(self, table_name):
        self.query = """
        CREATE TABLE IF NOT EXISTS %s(
        id serial NOT NULL PRIMARY KEY,
        sensor_data VARCHAR(100),
        pub_date DATETIME)
        """ % table_name
        self.cur.execute(self.query)

    # Check the DB_table existence.
    def table_check(self, table_name):
        self.query = "SHOW TABLES LIKE '%s'" % table_name
        return self.cur.execute(self.query)

    # Insert sensor value into the table
    def insert_data(self, table_name, value):
        self.cur.execute("INSERT INTO %s (sensor_data, pub_date) VALUES(%d, NOW())" %(table_name, value))

    # Create a class about the DB_table into models.py
    def inspectdb(self):
        # Get a list of the DB_tables related to the sensor
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
    iot_topic = "iot_" + str(msg.topic).replace("/","_") + "_"

    print("Topic: ", msg.topic + '\nMessage: ' + msg.payload)

    for name in dict.keys():
        iot_name = iot_topic + name

        # If the table about the topic does not exist
        if Iot_Sensor.table_check(iot_name) == False:
            check_table = False
            print("%s table does not exists" % iot_name)
        Iot_Sensor.table_create(iot_name)

        # If new DB_table created, make a class into models.py
        if check_table == False:
            Iot_Sensor.inspectdb()

        # Insert sensor value into the DB_table
        Iot_Sensor.insert_data(iot_name, dict[name])
        print(iot_name + " " + str(dict[name]) + " " + str(now))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("your_mqtt_broker_ip", 1883, 60) #Add your Mqtt Broker ip
client.loop_forever()
