import threading, mydb
from myemail import Email

def schedule_idle_email(master):
    current_thread = threading.currentThread()
    email = Email()
    idle_email = getattr(email, 'idle_email')
    prev_email_list, thread_list = ([] for i in range(2))

    while current_thread.do_run:
        email_dict = mydb.get_email_dict(master)
        current_email_list = [email for email in email_dict if email_dict[email]["is_IDLE"] == True]

        if prev_email_list:
            add_email_list = [email for email in current_email_list if not email in prev_email_list]
            delete_email_list = [email for email in prev_email_list if not email in current_email_list]

            if add_email_list:
                for email in add_email_list:
                    thread_func = threading.Thread(target = idle_email, args = (master, email))
                    thread_func.do_run = True
                    thread_list.append((email, thread_func))
                    thread_func.start()

            if delete_email_list:
                for email in delete_email_list:
                    for index in range(len(thread_list)):
                        if thread_list[index][0] == email:
                            thread_list[index][1].do_run = False
                            del thread_list[index]
                            break

        else:
            prev_email_list = current_email_list[:]

            for email in prev_email_list:
                thread_func = threading.Thread(target = idle_email, args = (master, email))
                thread_func.do_run = True
                thread_list.append((email,thread_func))

            for thread_func in thread_list:
                thread_func[1].start()
    for (email, thread_func) in thread_list:
        thread_func.do_run = False

def schedule_polling_email(master, init):
    email = Email()
    email.polling_email(master, init)

def schedule_today_weather(master, io):
    responses = {}
    responses["method"] = "update_today_weather"
    responses["master"] = master

    try:
        config_weather = weather.config_init()
        weather_details = weather.update_weather(True)
        responses["data"] = weather_details
        responses["success"] = True

    except Exception as e:
        print(e)
        responses["success"] = False

    io.emit("to-master", responses)
