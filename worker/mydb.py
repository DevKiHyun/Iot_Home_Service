'''
This module is for access user_mysqlDB.
'''

import pymysql, time

def get_db():
    db = pymysql.connect(host = "", #Your host
                   user = "",   #Your db user_name
                   passwd = "", #your db user_password
                   db = "")

    return db


class Sensor_Table:

    def __init__(self, database):
        self.db =  database
        self.cur = self.db.cursor()

    def table_create(self, table_name):
        self.query = """
        CREATE TABLE %s(
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

    def inspectdb(self):
        table_list = []
        self.cur.execute("SHOW TABLES")
        result = self.cur.fetchall()
        for row in result:
            if 'iot_' in row[0] :
                table_list.append(row[0])
        os.system("python manage.py inspectdb %s > iots/models.py" % " ".join(table_list))
        os.system("python manage.py migrate")
'''
def init():
    print("Database initiate")
    cur = get_db().cursor()

    #if auth_user exist, but not exist app_table
'''

def create_app_email(current_user):
    table_list = []
    db = get_db()
    cur = db.cursor()
    cur.execute("SHOW TABLES")

    result = cur.fetchall()
    for row in result:
        table_list.append(row[0])

    if "app_email" in table_list:
        user_id_list = []
        cur.execute('''SELECT user_id FROM app_email
        ''' )

        result = cur.fetchall()
        for row in result:
            user_id_list.append(row[0])

        if not current_user in user_id_list:
            cur.execute("""INSERT INTO app_email (user_id, is_create)
            VALUES('%s', %d)""" %(current_user, 0))
            db.commit()

    else:
        query = """
        CREATE TABLE app_email(
        user_id varchar(254),
        email_list longtext,
        is_create tinyint(1) )
        """
        cur.execute(query)

        cur.execute("""INSERT INTO app_email (user_id, is_create)
        VALUES('%s', %d)""" %(current_user, 0))
        db.commit()

def get_email_dict(master):
    cur = get_db().cursor()
    cur.execute('''SELECT email_list FROM app_email
    WHERE user_id = '%s'
    ''' %master)

    email_dict = cur.fetchone()[0]

    return email_dict

def view_email_dict(master):
    email_dict = get_email_dict(master)

    if email_dict == None:
        return {}

    else:
        email_list = list(eval(email_dict).keys())
        temp = list()
        email_dict = dict()

        for email in email_list:
            index = email.find("@")
            host = email[index+1:]
            email_id = email[:index]
            temp.append((host,email_id))

        temp.sort(key=lambda tup:tup[0]) #sort by host

        # { (host_1, host_1.domain) : [mail_id_1, mail_id_2], (host_2, host_2.domain) : [mail_id_1, mail_id_2] }
        for (host,email_id) in temp:
            index = host.find('.')
            domain = host[index+1:]
            host_name = host[:index]

            if not (host_name,domain) in email_dict:
                email_dict[(host_name,domain)] = list()

            email_dict[(host_name,domain)].append(email_id)


        return email_dict

def email_exist(master, email):
    #print("master is " + master)
    #print("check email " + email)
    cur = get_db().cursor()

    email_dict = get_email_dict(master)

    if not email_dict:
        #print("email_dict is None")
        return False

    else:
        #print("user's email_dict is " + email_list)
        if email in email_dict:
            return True
        else:
            return False

def add_email(master, user_email, user_password):
    db = get_db()
    cur = db.cursor()

    result = get_email_dict(master);

    email_dict = dict()

    if result == None:
        email_dict[user_email] = user_password

    else :
        email_dict = eval(result)
        email_dict[user_email] = user_password

    cur.execute('''UPDATE app_email
    SET email_list = "%s"
    WHERE user_id = '%s'
    ''' %(email_dict, master))

    db.commit()

def is_add_email(current_user):
    cur = get_db().cursor()

    cur.execute('''SELECT is_create FROM app_email
    WHERE user_id = '%s'
    ''' %current_user)

    result = cur.fetchone()[0]

    return result


#def create_app_calender():


def view_sensor_dict():
    cur = get_db().cursor()
    table_list, place_list, sensor_list = [], [], []
    value, dict_odd, dict_even, dict_temp = dict(), dict(), dict(), dict()

    cur.execute("SHOW TABLES")
    result = cur.fetchall()
    for row in result:
        if 'iot_' in row[0] :
            temp = row[0].split("_")
            table_list.append(row[0])
            place_list.append(temp[1])
            sensor_list.append(temp[2])

    for i in range(0,len(table_list)):
        query = """
        SELECT sensor_data From %s
        """ %table_list[i]

        cur.execute(query)
        sensor_data = cur.fetchall()[-1][0]

        if i+1 < len(place_list) :
            if place_list[i] == place_list[i+1] :
                value[sensor_list[i]] = sensor_data
            else :
                value[sensor_list[i]] = sensor_data
                dict_temp[place_list[i]] = dict(value)
                value.clear()
        else :
                value[sensor_list[i]] = sensor_data
                dict_temp[place_list[i]] = dict(value)
                value.clear()

    list_key = list(dict_temp.keys())
    for i in range(0, len(list_key)):
        if i%2 == 0 :
            dict_even[list_key[i]] = dict_temp[list_key[i]]
        else :
            dict_odd[list_key[i]] = dict_temp[list_key[i]]

    sensor_dict = { "even" : dict_even , "odd" : dict_odd }

    return sensor_dict
