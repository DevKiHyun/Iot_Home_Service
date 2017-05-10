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
            raise

        try:
            server.login(user_email,user_password)
            print("Login success--'%s'" %user_email)
            return server
        except Exception as e:
            raise print(e)

    def _thread_email_fetch(self, server, start, end, not_delete_list, Queue):
        mailbox_list = []
        for i in range(start, end):
            if not isinstance(not_delete_list[i], tuple):
                state = 'seen'
                index = not_delete_list[i]
            else :
                index = not_delete_list[i][0]
                state = not_delete_list[i][1]

            message = server.fetch([index], ('BODY[HEADER.FIELDS (FROM DATE SUBJECT)]'))
            msg = email.message_from_bytes(message[index][b'BODY[HEADER.FIELDS (FROM DATE SUBJECT)]'])
            subject = str(make_header(decode_header(msg['Subject'])))

            msg_from = str(make_header(decode_header(msg['From'])))
            if '<' in msg_from:
                msg_from = msg_from.replace('<','(').replace('>', ')')

            mailbox_dict = {'index' : index, 'from' : msg_from, 'subject' : subject, 'date' : msg['Date'], 'state' : state}
            mailbox_list.append(mailbox_dict)

        Queue.put(mailbox_list)
        print("Clear FETCH thread")
    def add_email(self, master, data):
        user_email = data["email"]
        user_password = data["password"]

        responses = dict()
        responses["master"] = master
        responses["method"] = "responses_add_email"
        responses["data"] = user_email

        try:
            server = self._server_login(user_email, user_password)

            try:
                if mydb.email_exist(master, user_email) == False:
                    mydb.add_email(master, user_email, user_password)
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
        email_details = mydb.get_email_details(master)[user_email]
        added_folder_list = email_details["folder"]
        responses , responses["data"] = ({} for i in range(2))
        responses["master"] = master
        responses["method"] = "responses_click_email"
        responses["data"] = { "email" : user_email, "folder" : mydb.email_folder(user_email),
                              "added_folder_list" : added_folder_list,
                              "total_folder_list" : self.get_email_folder(master, user_email) }
        responses["success"] = True

        self.io.emit("to-master", responses)

    def add_email_folder(self, master, data):
        user_email = data["email"]
        added_folder = data["add_folder"]

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
        user_password = mydb.get_email_details(master)[user_email]["password"]

        try:
            server = self._server_login(user_email, user_password)
            result = server.list_folders()
            folder_list = []
            for folder in result:
                folder_list.append(folder[2])
            return folder_list

        except Exception as e:
            print(e)

        #soon update

    def get_email_box(self, master, data):
        print("Start 'get_email_box'")
        user_email = data["email"]
        user_password = mydb.get_email_details(master)[user_email]["password"]
        email_folder = data["folder"]

        responses, responses["data"] = ({} for i in range(2))
        responses["master"] = master
        responses["method"] = "responses_get_email_box"
        responses["data"]["email"] = user_email

        try:
            server = self._server_login(user_email, user_password)
            server.select_folder(email_folder)

            not_delete_list = server.search("NOT DELETED")
            not_delete_list.sort(reverse = True)
            mailbox_index = not_delete_list[:]
            unseen_list = server.search("UNSEEN")

            if unseen_list:
                for item in unseen_list:
                    index = not_delete_list.index(item)
                    not_delete_list[index] = (item, "unseen")

            # 4 thread do 'fetch'.
            thread_list = []
            Queue = queue.Queue()
            length = len(not_delete_list)
            count = 4
            for i in range(0,count):
                start = i * int((length/count))
                if i != count-1:
                    end = (i+1) * int((length/count))
                else :
                    end = length

                thread_server = self._server_login(user_email, user_password)
                thread_server.select_folder(email_folder)
                thread_fetch = threading.Thread(target= self._thread_email_fetch,
                                                args = (thread_server, start, end,
                                                        not_delete_list, Queue))
                thread_list.append(thread_fetch)

            for thread_fetch in thread_list:
                thread_fetch.start()

            for thread_fetch in thread_list:
                thread_fetch.join()

            mailbox = []
            while not Queue.empty():
                mailbox.extend(Queue.get_nowait())

            mailbox = sorted(mailbox, key = lambda k : k['index'], reverse = True)

            responses["data"]["folder"] = { email_folder :
                                          { "mailbox" : mailbox,
                                            "mailbox_index" : mailbox_index } }
            responses["success"] = True

        except Exception as e:
            print(e)
            responses["data"] = None
            responses["success"] = False
            mailbox = None;

        self.io.emit("to-master", responses)

        folder = {}
        folder[email_folder] = { 'mailbox' : mailbox, 'mailbox_index' : mailbox_index }
        mydb.add_email_box(master, user_email, folder)
        print("End 'get_email_box'")

    def get_email_content(self, master, data):
        print("Start 'get_email_content'")
        user_email = data["email"]
        user_password = mydb.get_email_details(master)[user_email]["password"]
        email_folder = data["folder"]
        email_index = data["index"]

        responses , responses["data"] = ({} for i in range(2))
        responses["master"] = master
        responses["method"] = "responses_get_email_content"
        responses["data"]["folder"] = email_folder

        try:
            server = self._server_login(user_email, user_password)
            server.select_folder(email_folder)

            message = server.fetch([email_index],('RFC822'))
            msg = email.message_from_bytes(message[email_index][b'RFC822'])

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
        print("End 'get_email_content'")
