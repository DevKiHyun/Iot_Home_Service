from socketIO_client import SocketIO
from imapclient import IMAPClient
from backports import ssl
from email.header import  Header, decode_header, make_header
import email, imapclient, threading, datetime, mydb, queue

class Email():
    def __init__(self):
        self.io  = SocketIO('localhost', 8080)
        self.context = imapclient.create_default_context()
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_NONE

    def _server_login(self, user_email, user_password):
        index = user_email.find("@")
        host = "imap." + user_email[index+1:]

        try:
            server = IMAPClient(host, use_uid = True, ssl = True, ssl_context = self.context)

        except Exception as e:
            print("Error in 'host' or 'ssl_context'. Check please!")
            print(e)

        try:
            server.login(user_email,user_password)
            return server

        except Exception as e:
            print(e)

    def _email_fetch(self, server, start, end, mailbox_list, Queue):
        mailbox = []

        for i in range(start, end):
            if not isinstance(mailbox_list[i], tuple):
                state = 'seen'
                index = mailbox_list[i]
            else :
                index = mailbox_list[i][0]
                state = mailbox_list[i][1]

            message = server.fetch([index], ('BODY[HEADER.FIELDS (FROM DATE SUBJECT)]'))
            msg = email.message_from_bytes(message[index][b'BODY[HEADER.FIELDS (FROM DATE SUBJECT)]'])
            subject = str(make_header(decode_header(msg['Subject'])))

            msg_from = str(make_header(decode_header(msg['From'])))
            if '<' in msg_from:
                msg_from = msg_from.replace('<','(').replace('>', ')')

            mailbox_dict = {'id' : index, 'from' : msg_from, 'subject' : subject, 'date' : msg['Date'], 'state' : state}
            mailbox.append(mailbox_dict)

        print("Clear FETCH email")

        if Queue:
            Queue.put(mailbox)

        else:
            return mailbox

    def _thread_email_fetch(self, user_email, user_password, folder_name, mailbox_list):
        print("Start FETCH email")

        thread_list = []
        mailbox = []
        Queue = queue.Queue()
        length = len(mailbox_list)
        count = 4

        if length < 10:
            server = self._server_login(user_email, user_password)
            server.select_folder(folder_name)
            mailbox = self._email_fetch(server, 0, length, mailbox_list, None)

        else:
            for i in range(0,count):
                start = i * int((length/count))
                if i != count-1:
                    end = (i+1) * int((length/count))
                else :
                    end = length

                thread_server = self._server_login(user_email, user_password)
                thread_server.select_folder(folder_name)
                thread_fetch = threading.Thread(target= self._email_fetch,
                                                args = (thread_server, start, end,
                                                        mailbox_list, Queue))
                thread_list.append(thread_fetch)

            for thread_fetch in thread_list:
                thread_fetch.start()

            for thread_fetch in thread_list:
                thread_fetch.join()

            while not Queue.empty():
                mailbox.extend(Queue.get_nowait())

        return mailbox

    def _change_flag(self, server, email_id, flag):
        if flag == 'unseen':
            flag = b'\Seen'

        if flag == 'seen':
            flag = b'\UnSeen'

        server.add_flags(email_id, flag)


    def add_email(self, master, data):
        print("Add new email account")

        user_email = data["email"]
        user_password = data["password"]

        responses = {}
        responses["master"] = master
        responses["method"] = "responses_add_email"
        responses["data"] = user_email

        try:
            server = self._server_login(user_email, user_password)
            try:
                if mydb.email_exist(master, user_email) == False:
                    is_idle = True if server.has_capability("IDLE") else False
                    mydb.add_email(master, user_email, user_password, is_idle)

                    responses["success"] = True
                    print("Add new email")

                else:
                    responses["success"] = False
                    print("Already exists")

            except Exception as e:
                print("Error in 'email_exist' or 'add_email' in mydb.py")
                print(e)
                responses["success"] = False

        except Exception as e:
            print(e)
            responses["success"] = False
            self.io.emit("message", "login fail")

        self.io.emit("to-master", responses)

    def click_email(self, master, data):
        user_email = data["email"]
        email_details = mydb.get_email_dict(master)[user_email]
        added_folder_list = email_details["folder"]
        responses , responses["data"] = ({} for i in range(2))
        responses["master"] = master
        responses["method"] = "responses_click_email"
        responses["data"] = { "email" : user_email, "folder" : mydb.email_folder(user_email),
                              "added_folder_list" : added_folder_list,
                              "total_folder_list" : self.get_email_folder(master, user_email) }
        responses["success"] = True

        print("click email - {0}".format(user_email))

        self.io.emit("to-master", responses)

    def add_email_folder(self, master, data):
        user_email = data["email"]
        added_folder = data["add_folder"]

        print("Add {0} folder of {1}".format(added_folder, user_email))

        responses = {}
        responses["master"] = master
        responses["method"] = "responses_add_email_folder"

        try:
            mydb.add_email_folder(master, user_email, added_folder)
            responses["data"] = { "email" : user_email, "added_folder" : added_folder }
            responses["success"] = True

        except Exception as e:
            print(e)
            responses["data"] = { "email" : user_email, "added_folder" : added_folder }
            responses["success"] = False

        self.io.emit("to-master", responses)

    def get_email_folder(self, master, email):
        user_email = email
        user_password = mydb.get_email_dict(master)[user_email]["password"]

        try:
            server = self._server_login(user_email, user_password)
            result = server.list_folders()
            folder_list = []
            for folder in result:
                folder_list.append(folder[2])
            return folder_list

        except Exception as e:
            print(e)

    def update_email_box(self, user_email, user_password, folder_name):
        print("Update {0} folder in {1}".format(folder_name, user_email))

        prev_mailbox, prev_mailbox_list = mydb.get_email_box(user_email, folder_name)
        prev_unseen_list = [dic["id"] for index, dic in enumerate(prev_mailbox) if dic["state"] == "unseen"]

        server = self._server_login(user_email, user_password)
        server.select_folder(folder_name)

        not_delete_list = server.search("NOT DELETED")
        not_delete_list.sort(reverse = True)
        mailbox_list = not_delete_list[:]
        unseen_list = server.search("UNSEEN")

        #Get difference between two lists
        set_not_delete_list = set(not_delete_list)
        set_prev_mailbox_list = set(prev_mailbox_list)
        set_unseen_list = set(unseen_list)
        set_prev_unseen_list = set(prev_unseen_list)

        delete_email_list = [elem for elem in prev_mailbox_list if not elem  in set_not_delete_list]
        add_email_list =  [elem for elem in not_delete_list if not elem in set_prev_mailbox_list]
        seen_flag_list = [elem for elem in set_prev_unseen_list if not elem in set_unseen_list]
        unseen_flag_list = [elem for elem in unseen_list if not elem in set_prev_unseen_list]

        # If change anything
        if any((delete_email_list, add_email_list, seen_flag_list, unseen_flag_list)):
            find_delete_index = [prev_mailbox_list.index(index) for index in delete_email_list]
            find_delete_index.sort(reverse = True)
            find_seen_flag_index = [prev_mailbox_list.index(find_index) for find_index in seen_flag_list if find_index in prev_mailbox_list]
            find_unseen_flag_index = [prev_mailbox_list.index(find_index) for find_index in unseen_flag_list if find_index in prev_mailbox_list]

            for index in find_delete_index:
                del prev_mailbox[index]

            check_delete_list = [elem for elem in find_seen_flag_index if not elem in find_delete_index]
            if check_delete_list:
                for index in find_seen_flag_index:
                    prev_mailbox[index]["state"] = "seen"

            for index in find_unseen_flag_index:
                prev_email = prev_mailbox[index]
                if prev_email:
                    prev_email["state"] = "unseen"

            for flag in unseen_flag_list:
                if flag in add_email_list:
                    index = add_email_list.index(flag)
                    add_email_list[index] = (flag, "unseen")

            mailbox = self._thread_email_fetch(user_email, user_password, folder_name, add_email_list)

            if mailbox:
                mailbox.extend(prev_mailbox)
                mailbox = sorted(mailbox, key = lambda k : k['id'], reverse = True)

            else:
                mailbox = prev_mailbox

            do_update = True

        else:
            mailbox = prev_mailbox
            do_update = False

        return mailbox, mailbox_list, len(unseen_list), do_update

    def get_email_box(self, master, data):
        print("Start 'get_email_box'")

        user_email = data["email"]
        user_password = mydb.get_email_dict(master)[user_email]["password"]
        folder_name = data["folder"]

        is_email_box = mydb.is_email_box(master, user_email, folder_name)

        folder, responses, responses["data"] = ({} for i in range(3))
        responses["master"] = master
        responses["method"] = "responses_get_email_box"
        responses["data"]["email"] = user_email

        try:
            if is_email_box:
                mailbox, mailbox_list, unseen_num, do_update = self.update_email_box(user_email, user_password, folder_name)

                if do_update:
                    folder = { "mailbox" : mailbox, "mailbox_list" : mailbox_list, "unseen_num" : unseen_num }

                    mydb.update_email_box(user_email, folder, folder_name)

            else:
                server = self._server_login(user_email, user_password)
                server.select_folder(folder_name)

                not_delete_list = server.search("NOT DELETED")
                not_delete_list.sort(reverse = True)
                mailbox_list = not_delete_list[:]
                unseen_list = server.search("UNSEEN")
                unseen_num = len(unseen_list)

                if unseen_list:
                    for item in unseen_list:
                        index = not_delete_list.index(item)
                        not_delete_list[index] = (item, "unseen")

                mailbox = self._thread_email_fetch(user_email, user_password, folder_name, not_delete_list)

                if mailbox:
                    mailbox = sorted(mailbox, key = lambda k : k['id'], reverse = True)

                    folder[folder_name] = { "mailbox" : mailbox, "mailbox_list" : mailbox_list, "unseen_num" : unseen_num }
                    mydb.add_email_box(master, user_email, folder, folder_name)

            responses["data"]["folder"] = { folder_name :
                                              {
                                                "mailbox" : mailbox,
                                                "mailbox_list" : mailbox_list,
                                                "unseen_num" : unseen_num
                                               }
                                          }
            responses["success"] = True

        except Exception as e:
            print(e)
            responses["data"] = None
            responses["success"] = False
            mailbox = None;

        self.io.emit("to-master", responses)

        print("End 'get_email_box'")

    def get_email_content(self, master, data):
        print("Start 'get_email_content'")

        user_email = data["email"]
        user_password = mydb.get_email_dict(master)[user_email]["password"]
        folder_name = data["folder"]
        email_id = data["id"]
        index = data["index"]
        state = data["state"]
        responses = {}
        responses["master"] = master
        responses["method"] = "responses_get_email_content"
        responses["data"] = { "folder" : folder_name, "state" : state, "id" : email_id, "email" : user_email }

        try:
            server = self._server_login(user_email, user_password)
            server.select_folder(folder_name)

            message = server.fetch([email_id],('RFC822'))
            msg = email.message_from_bytes(message[email_id][b'RFC822'])

            for part in msg.walk():
                charset = part.get_content_charset()
                if part.get_content_type() == 'text/html':
                    email_content = part.get_payload(decode=True).decode(charset)
                    responses["data"]["email_content"] = email_content

            responses["success"] = True

        except Exception as e:
            print(e)
            responses["success"] = False

        self.io.emit("to-master", responses)

        if state == "unseen":
            mydb.change_email_flag(user_email, folder_name, index, None, state)
            self._change_flag(server, email_id, state)

        print("End 'get_email_content'")

    def _thread_idle_email(self, master, server, user_email, folder_name):
        user_password = mydb.get_email_dict(master)[user_email]["password"]

        server.select_folder(folder_name)
        current_thread = threading.currentThread()

        responses, responses["data"] = ({} for i in range(2))
        responses["master"] = master
        responses["method"] = "update_email"
        responses["data"][user_email] = {}

        try:
            while current_thread.do_run:
                server.idle()
                result = server.idle_check(600)
                if result:
                    mailbox, mailbox_list, unseen_num, do_update = self.update_email_box(user_email, user_password, folder_name)
                    folder = { "mailbox" : mailbox, "mailbox_list" : mailbox_list, "unseen_num" : unseen_num }

                    if do_update:
                        mydb.update_email_box(user_email, folder, folder_name)


                    responses["data"][user_email][folder_name] = folder
                    responses["success"] = True

                    self.io.emit("to-master", responses)

                server.idle_done()

        except Exception as e:
            print(e)
            responses["success"] = False
            self.io.emit("to-master", responses)

    def idle_email(self, master, user_email):
        user_password = mydb.get_email_dict(master)[user_email]["password"]
        current_folder_list, idle_list = ([] for i in range(2))
        current_thread  = threading.currentThread()

        while current_thread.do_run:
            email_dict = mydb.get_email_dict(master)[user_email]
            is_email_box = email_dict["is_email_box"]
            prev_folder_list = []

            if is_email_box:
                length = len(is_email_box)
                for i in range(length):
                    if is_email_box[i]:
                        prev_folder_list.append(email_dict["folder"][i])

                if current_folder_list:
                    add_folder_list = [folder for folder in prev_folder_list if not folder in current_folder_list]
                    delete_folder_list = [folder for folder in current_folder_list if not folder in prev_folder_list]

                    if add_folder_list:
                        for folder in add_folder_list:
                            server = self._server_login(user_email, user_password)
                            thread_func = threading.Thread(target = self._thread_idle_email, args = (master, server, user_email, folder))
                            idle_list.append((folder, thread_func))
                            idle_list[-1][1].start()

                    if delete_folder_list:
                        for folder in delete_folder_list:
                            for idle_func in idle_list:
                                if idle_func[0] == folder:
                                    idle_func[1].do_run = False
                                    del idle_list[idle_func]
                                    break

                else:
                    current_folder_list = prev_folder_list[:]
                    for folder in current_folder_list:
                        server = self._server_login(user_email, user_password)
                        thread_func = threading.Thread(target = self._thread_idle_email, args = (master, server, user_email, folder))
                        thread_func.do_run = True
                        idle_list.append((folder, thread_func))

                    for (folder, thread_func) in idle_list:
                        thread_func.start()

        for (folder, idle_func) in idle_list:
            idle_func.do_run = False

    def polling_email(self, master, init):
        print("Polling email - {0}".format(master))

        email_list = mydb.get_email_dict(master)

        if init:
            email_account_list = [email for email in email_list]
        else:
            email_account_list = [email for email in email_list if not 'gmail' in email]

        responses, responses["data"] = ({} for i in range(2))
        responses["master"] = master
        responses["method"] = "update_email"

        try:
            for user_email in email_account_list:
                email_details = email_list[user_email]
                user_password = email_details['password']
                folder_list = email_details['folder']
                is_email_box_list = email_details['is_email_box']
                if folder_list:
                    length = len(folder_list)
                    responses["data"][user_email] = {}

                    for i in range(0,length):
                        if is_email_box_list[i]:
                            mailbox, mailbox_list, unseen_num, do_update = self.update_email_box(user_email, user_password, folder_list[i])
                            folder = { "mailbox" : mailbox, "mailbox_list" : mailbox_list, "unseen_num" : unseen_num }

                            if do_update:
                                mydb.update_email_box(user_email, folder, folder_list[i])

                            responses["data"][user_email][folder_list[i]] = folder

            responses["success"] = True

        except Exception as e:
            print(e)
            responses["success"] = False

        self.io.emit("to-master", responses)
