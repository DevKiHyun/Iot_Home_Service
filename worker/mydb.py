'''
This module is for access user_mysqlDB.
'''

import pymysql, time, json

def get_db():
    db = pymysql.connect(
        host = "",
        user = "",
        passwd = "",
        db = "",
        charset = "utf8")

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

def create_app_email(master):
    table_list = []
    db = get_db()
    cur = db.cursor()
    cur.execute("SHOW TABLES")

    result = cur.fetchall()
    for row in result:
        table_list.append(row[0])

    if "app_email" in table_list:
        user_id_list = []
        cur.execute("SELECT master FROM app_email")

        result = cur.fetchall()
        for row in result:
            user_id_list.append(row[0])

        if not master in user_id_list:
            query = "INSERT INTO app_email (master, is_create) VALUES(%s,%d)"
            cur.execute(query %(master, 0))
            db.commit()

    else:
        query = """
        CREATE TABLE app_email(
        master varchar(254),
        email_list longtext,
        is_create tinyint(1))
        """
        cur.execute(query)

        query = "INSERT INTO app_email (master, is_create) VALUES(%s,%d)"
        cur.execute(query %(master, 0))
        db.commit()

def create_app_email_folder():
    table_list = []
    cur = get_db().cursor()
    cur.execute("SHOW TABLES")

    result = cur.fetchall()
    for row in result:
        table_list.append(row[0])

    if not "app_email_folder" in table_list:
        query = """
        CREATE TABLE app_email_folder(
        user_email varchar(254),
        email_folder longtext)
        """
        cur.execute(query)

def get_email_details(master):
    cur = get_db().cursor()
    query = "SELECT email_list FROM app_email WHERE master = %s"
    cur.execute(query, master)

    email_dict = eval(cur.fetchone()[0])

    return email_dict

def view_email_dict(master):
    email_details = get_email_details(master)

    if email_details == None:
        return {}

    else:
        email_list = list(email_details.keys())
        temp = []
        email_dict = {}

        for email in email_list:
            # email = my_example@gmail.com
            index = email.find("@")
            #ex) host =  gmail.com
            host = email[index+1:]
            #ex) email_id = my_example
            email_id = email[:index]
            temp.append((host,email_id))

        temp.sort(key=lambda tup:tup[0]) #sort by host

        # { (host_1, host_1.domain) : [mail_id_1, mail_id_2], (host_2, host_2.domain) : [mail_id_1, mail_id_2] }
        for (host,email_id) in temp:
            index = host.find('.')
            #ex) domain = com
            domain = host[index+1:]
            #ex) host_name = gmail
            host_name = host[:index]

            if not (host_name,domain) in email_dict:
                email_dict[(host_name,domain)] = []

            email_dict[(host_name,domain)].append(email_id)

        return email_dict

def email_exist(master, user_email):
    cur = get_db().cursor()

    email_dict = get_email_details(master)

    if not email_dict:
        return False

    else:
        if user_email in email_dict:
            return True
        else:
            return False

def email_folder(user_email):
    cur = get_db().cursor()

    query = "SELECT email_folder FROM app_email_folder WHERE user_email = %s"
    cur.execute(query, user_email)

    result = cur.fetchone()[0]

    email_folder = json.loads(result) if result else None

    return email_folder

def add_email(master, user_email, user_password):
    db = get_db()
    cur = db.cursor()

    result = get_email_details(master);

    email_dict, details = ({} for i in range(2))

    if result :
        email_dict = eval(result)

    details["password"] = user_password
    details["is_email_box"] = None
    details["folder"] = None
    details["oauth"] = False
    email_dict[user_email] = details

    query = "UPDATE app_email SET email_list = %s WHERE master = %s"
    cur.execute(query, (str(email_dict), master))

    query = "INSERT INTO app_email_folder (user_email) VALUES(%s)"
    cur.execute(query, user_email)
    db.commit()

def add_email_folder(master, user_email, folder):
    db = get_db()
    cur = db.cursor()
    query = "SELECT email_list FROM app_email WHERE master = %s"
    cur.execute(query, master)
    result = eval(cur.fetchone()[0])

    email_details = result[user_email]
    folder_list = email_details["folder"]
    is_email_box = email_details["is_email_box"]

    if not folder_list:
        folder_list, is_email_box = ([] for i in range(2))

    if not folder in folder_list:
        folder_list.append(folder)
        is_email_box.append(False)

        result[user_email]["folder"] = folder_list
        result[user_email]["is_email_box"] = is_email_box

        query = "UPDATE app_email SET email_list = %s WHERE master = %s"
        cur.execute(query, (str(result), master))

        db.commit()

def add_email_box(master, user_email, folder):
    db = get_db()
    cur = db.cursor()

    added_folder_name = list(folder.keys())[0]

    query  = "SELECT email_folder FROM app_email_folder WHERE user_email = %s"
    cur.execute(query, user_email)

    result = cur.fetchone()[0]
    email_folder = json.loads(result) if result else {}

    if not email_folder:
        email_folder = folder

    elif not added_folder_name in email_folder:
        email_folder.update(folder)

    query = "UPDATE app_email_folder SET email_folder = %s WHERE user_email = %s"
    cur.execute(query, (json.dumps(email_folder), user_email))

    # update is_email_box's state in app_email
    query = "SELECT email_list FROM app_email WHERE master = %s"
    cur.execute(query, master)
    result = eval(cur.fetchone()[0])

    email_details = result[user_email]
    folder_list = email_details["folder"]
    is_email_box = email_details["is_email_box"]

    index = folder_list.index(added_folder_name)
    is_email_box[index] = True

    result[user_email]["is_email_box"] = is_email_box

    query = "UPDATE app_email SET email_list = %s WHERE master = %s"
    cur.execute(query, (str(result), master))
    db.commit()

def is_add_email(master):
    cur = get_db().cursor()

    query = "SELECT is_create FROM app_email WHERE master = %s"
    cur.execute(query, master)

    result = cur.fetchone()[0]

    return result

# check the folder's mailbox has been fetched
def is_email_box(master, user_email, folder):
    cur = get_db().cursor()

    query = "SELECT email_list FROM app_email WHERE master = %s"
    cur.execute(query, master)

    result = cur.fetchone()[0]
    folder_list = result["folder"]
    is_email_box_list = result["is_email_box"]

    index = folder_list.index(folder)

    return is_email_box_list[index]

#def create_app_calender():

def view_sensor_dict():
    cur = get_db().cursor()
    table_list, place_list, sensor_list = ([] for i in range(3))
    value, dict_odd, dict_even, dict_temp = ({} for i in range(4))

    cur.execute("SHOW TABLES")
    result = cur.fetchall()
    for row in result:
        if 'iot_' in row[0] :
            temp = row[0].split("_")
            table_list.append(row[0])
            place_list.append(temp[1])
            sensor_list.append(temp[2])

    for i in range(0,len(table_list)):
        query = "SELECT sensor_data From %s"

        cur.execute(query, table_list[i])
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
