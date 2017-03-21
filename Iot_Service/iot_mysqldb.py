'''
This module is for access user_mysqlDB.
'''

import pymysql

db = pymysql.connect(host = "", #Your host
                   user = "",   #Your db user_name
                   passwd = "", #your db user_password
                   db = "")     #yotu db name
cur = db.cursor()
