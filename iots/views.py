from django.shortcuts import render
from iots import models, mydb
import pymysql, inspect

def index(request):
    #you can get request.user
    cur_1 = mydb.cur
    cur_2 = mydb.cur
    table_list, place_list, sensor_list = [], [], []
    value, dict_odd, dict_even, dict_temp = dict(), dict(), dict(), dict()

    cur_1.execute("SHOW TABLES")
    result = cur_1.fetchall()
    #cur_1.execute("UNLOCK TABLES;")

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
        cur_2.execute(query)

        sensor_data = cur_2.fetchall()[-1][0]
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
        #cur_2.execute("UNLOCK TABLES;")

    list_key = list(dict_temp.keys())
    for i in range(0, len(list_key)):
        if i%2 == 0 :
            dict_even[list_key[i]] = dict_temp[list_key[i]]
        else :
            dict_odd[list_key[i]] = dict_temp[list_key[i]]
    context = { "even" : dict_even , "odd" : dict_odd , "user" : request.user}

    return render(request, 'index.html', context)
