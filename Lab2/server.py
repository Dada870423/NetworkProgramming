import socket
import _thread
import sys
import time
import sqlite3
import os
from sqlite3 import Error

def Client_Work(ClientSocket, addr):
    ## print welcome msg
    msg = ""
    msg =  "*************************************************************************************************************************************\r\n" + \
           "__        __   _                            _          _   _             ____  ____ ____                                             \r\n" + \
           "\ \      / /__| | ___ ___  _ __ ___   ___  | |_ ___   | |_| |__   ___   | __ )| __ ) ___|                                            \r\n" + \
           " \ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \ | __/ _ \  | __| '_ \ / _ \  |  _ \|  _ \___ \   / __|/ _ \ '__\ \ / / _ \ '__|           \r\n" + \
           "  \ V  V /  __/ | (_| (_) | | | | | |  __/ | || (_) | | |_| | | |  __/  | |_) | |_) |__) |  \__ \  __/ |   \ V /  __/ |              \r\n" + \
           "   \_/\_/ \___|_|\___\___/|_| |_| |_|\___|  \__\___/   \__|_| |_|\___|  |____/|____/____/   |___/\___|_|    \_/ \___|_|          \r\n\r\n" + \
           "*************************************************************************************************************************************\r\n"
    ClientSocket.send(msg.encode('utf-8'))

    # ClientSocket.recv(1024) # there is no trash in cmd 
    
    # Initialize
    login = -1 ## check login or not and whoami
    msg_suc = ""
    msg_err = ""
    msg_Usage = ""
    msg_output = ""
    hashtag = "##"
    TITLE = " --title "
    CONTENT = " --content "
    conn = sqlite3.connect('BBS.db')
    print("opened databases successfully")
    c = conn.cursor()
    while True:
        msg = "% "
        ClientSocket.send(msg.encode('utf-8'))
        msg_input = ClientSocket.recv(1024).decode('utf-8')
        msg_input = msg_input.replace('\n', '').replace('\r', '')
        msg_split = msg_input.split()
        print("msg : ", msg_input, "  len: ", len(msg_split))
        
        ## register
        if msg_input.startswith("register "):
            if len(msg_split) == 4:
                try:
                    cursor = c.execute('INSERT INTO USERS ("Username", "Email", "Password") VALUES (?, ?, ?)', (msg_split[1], msg_split[2], msg_split[3]))
                    conn.commit()
                    print("USER insertion is success")
                    msg_suc = "Register successfully.\r\n"
                except Error:
                    print("Username is already used")
                    msg_err = "Username is already used.\r\n"
        ## login
        if msg_input.startswith("login "):
            if login > -1:
                    msg_err = "Please logout first.\r\n"
            elif len(msg_split) == 3:
                cursor = c.execute('SELECT * FROM USERS WHERE Username = ?', (msg_split[1],)).fetchone()
                if cursor != None and cursor[3] == msg_split[2]: #person is exist
                    print("She is ", cursor[0], cursor[1])
                    login = cursor[0]
                    msg_suc = "Welcome, " + cursor[1] + "\r\n"
                else:   # no such person or password is incorrect
                    msg_err = "Login failed." + "\r\n"
        ## whoami
        if msg_input == "whoami":
            if login > -1:
                cursor = c.execute('SELECT * FROM USERS WHERE UID = ?', (login,)).fetchone()
                print("I am ", cursor[0])
                msg_suc = cursor[1] + "\r\n"
            else:
                msg_err = "Please login first.\r\n"
                print("He didn't login")
        ## logout
        if msg_input == "logout":
            if login > -1:
                cursor = c.execute('SELECT * FROM USERS WHERE UID = ?', (login,)).fetchone()
                login = -1
                print("Bye from ", cursor[0], "\r\n")
                msg_suc = "Bye, " + cursor[1] + "\r\n"
            else:
                msg_err = "Please login first.\r\n"
        ## exit
        if msg_input == "exit":
            print("the client ", login," want to bye")
            ClientSocket.close()
            break
# ------------- Lab1 done
        ## create-board
        if msg_input.startswith("create-board "):
            if login == -1:
                msg_err = "Please login first.\r\n"
            else:
                BName = msg_input.replace("create-board ", "", 1)
                try:
                    cursor = c.execute('INSERT INTO BOARDS ("BName", "Uid") VALUES (?, ?) ', (BName, login))
                    conn.commit()
                    print("Board insertion is success")
                    msg_suc = "Create board successfully.\r\n"
                except Error:
                    print("Board is already exist")
                    msg_err = "Board is already exist\r\n"
        ## To list the board
        if msg_input.startswith("list-board"): 
            HBName = msg_input.replace("list-board", "", 1)
            if msg_input == "list-board": ## without keyword
                cursor = c.execute("SELECT * FROM BOARDS").fetchone()
                msg_output = "{:^7} {:^20} {:^20} \r\n\r\n".format("Index", "Name", "Moderator")
                ClientSocket.send(msg_output.encode('utf-8'))
                if cursor == None:
                    print(cursor)
                    # msg_err = "There is not any board yet.\r\n"
                else:
                    for row in c.execute("SELECT BOARDS.BID, BOARDS.BName, USERS.Username FROM BOARDS INNER JOIN USERS ON BOARDS.UID=USERS.UID"):
                        print("{:>5} {:^20} {:^20}".format(row[0], row[1], row[2]))
                        msg_output = "{:>7} {:^20} {:^20}\r\n\r\n".format(row[0], row[1], row[2])
                        ClientSocket.send(msg_output.encode('utf-8'))   
                continue
            elif hashtag in HBName: ## with keyword
                BName = HBName.replace(" ##", "", 1)
                BName = "%" + BName + "%"
                cursor = c.execute("SELECT BOARDS.BID, BOARDS.BName, USERS.Username FROM BOARDS INNER JOIN USERS ON BOARDS.UID=USERS.UID WHERE BOARDS.BName LIKE ?", (BName, )).fetchone()
                msg_output = "{:^7} {:^20} {:^20} \r\n\r\n".format("Index", "Name", "Moderator")
                ClientSocket.send(msg_output.encode('utf-8'))
                if cursor == None:
                    print(cursor)	
                    # msg_err = "No keyword board yet.\r\n"
                else:
                    for row in c.execute("SELECT BOARDS.BID, BOARDS.BName, USERS.Username FROM BOARDS INNER JOIN USERS ON BOARDS.UID=USERS.UID WHERE BOARDS.BName LIKE ?", (BName, )):
                        print("{:>5} {:^20} {:^20}".format(row[0], row[1], row[2]))
                        msg_output = "{:>7} {:^20} {:^20}\r\n\r\n".format(row[0], row[1], row[2])
                        ClientSocket.send(msg_output.encode('utf-8'))
                continue
        ## create the post & file of comment
        if msg_input.startswith("create-post "):                             
            if login == -1:
                msg_err = "Please login first.\r\n"
            elif len(msg_split) > 5 and TITLE in msg_input and CONTENT in msg_input:                                        
                no_create = msg_input.replace("create-post ", "", 1)           ## Bname = BoardTitle[0]
                if msg_split[1] == "--title":                                  ## Title = TitleContent[0]
                    print("He did not choose the board")                       ## Content = TitleContent[1]
                elif msg_split[3] == "--content":
                    print("He did not name the title")
                else:
                    BoardTitle = no_create.split(" --title ")                   
                    TitleContent = BoardTitle[1].split(" --content ")           
                    print("Board name is : ", BoardTitle[0], "Title is : ", TitleContent[0], "Content is : ", TitleContent[1])
                    cursor = c.execute('SELECT * FROM BOARDS WHERE BName = ?', (BoardTitle[0],)).fetchone()
                    if cursor == None: #Board is not exist
                        print("Board is not exist")
                        msg_err = "Board is not exist.\r\n"
                    else:
                        print("Board exist")
                        NowTime = time.strftime("%m/%d", time.localtime()) ## is a string
                        cursor = c.execute('INSERT INTO POSTS ("TITLE", "BName", "UID", "DT") VALUES (?, ?, ?, ?)', (TitleContent[0], BoardTitle[0], login, NowTime))
                        conn.commit()
                        print(NowTime, type(NowTime), "POST insertion is success")
                        msg_suc = "Create post successfully.\r\n"
                        DIR = 'data/post'
                        P_num = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))]) 
                        cnt = TitleContent[1].split("<br>")
                        os.system("echo "" >> data/comment/{}".format(P_num+1))
                        for iter_cnt in cnt:
                            print(iter_cnt)
                            os.system("echo {} >> data/post/{}".format(iter_cnt, P_num+1))
        ## list the post with ## or not
        if msg_input.startswith("list-post "): 
            BName = msg_input.replace("list-post ", "", 1)
            ## with keyword
            if hashtag in BName: 
                if msg_split[1].startswith("##"):
                    print("He did not choose the board")
                else:
                    BNameKey = BName.split(" ##")
                    BName = BNameKey[0]
                    keyword = "%" + BNameKey[1] + "%"
                    print("Bname is :", BName, "keyword is :", keyword)
                    cursor = c.execute('SELECT * FROM BOARDS WHERE BName = ?', (BName,)).fetchone()
                    if cursor == None:                        ## Board is not exist
                        print("Board is not exist")
                        msg_err = "Board is not exist.\r\n"
                    else:
                        print("Board is exist")
                        cursor = c.execute("SELECT POSTS.PID, POSTS.TITLE, USERS.Username, POSTS.DT FROM POSTS INNER JOIN USERS ON POSTS.UID=USERS.UID WHERE POSTS.BName=? and POSTS.TITLE LIKE ?", (BName, keyword)).fetchone()
                        msg_output = "{:^7} {:^20} {:^20} {:^9}\r\n\r\n".format("ID", "Title", "Author", "Date")
                        ClientSocket.send(msg_output.encode('utf-8'))
                        if cursor == None:  ## there is not any post in this board 
                            print(cursor)
                            # msg_err = "There is not any post in this board yet.\r\n"
                        else:
                            for row in c.execute("SELECT POSTS.PID, POSTS.TITLE, USERS.Username, POSTS.DT FROM POSTS INNER JOIN USERS ON POSTS.UID=USERS.UID WHERE POSTS.BName=? and POSTS.TITLE LIKE ?", (BName, keyword)):
                                print("{:>5} {:^20} {:^20} {:^9}".format(row[0], row[1], row[2], row[3]))
                                msg_output = "{:>7} {:^20} {:^20} {:^9}\r\n\r\n".format(row[0], row[1], row[2], row[3])
                                ClientSocket.send(msg_output.encode('utf-8'))
                        continue
            ## without keyword
            else:  
                print("Want to search in ", BName, " Board")
                cursor = c.execute('SELECT * FROM BOARDS WHERE BName = ?', (BName,)).fetchone()
                if cursor == None:                        ## Board is not exist
                    print("Board is not exist")
                    msg_err = "Board is not exist.\r\n"
                else:
                    print("Board is exist")
                    cursor = c.execute("SELECT POSTS.PID, POSTS.TITLE, USERS.Username, POSTS.DT FROM POSTS INNER JOIN USERS ON POSTS.UID=USERS.UID WHERE POSTS.BName=?", (BName, )).fetchone()
                    msg_output = "{:^7} {:^20} {:^20} {:^9}\r\n\r\n".format("ID", "Title", "Author", "Date")
                    ClientSocket.send(msg_output.encode('utf-8'))
                    if cursor == None:  ## there is not any post in this board 
                        print(cursor)
                        # msg_err = "There is not any post in this board yet.\r\n"
                    else:
                        for row in c.execute("SELECT POSTS.PID, POSTS.TITLE, USERS.Username, POSTS.DT FROM POSTS INNER JOIN USERS ON POSTS.UID=USERS.UID WHERE POSTS.BName=?", (BName, )):
                            print("{:>5} {:^20} {:^20} {:^9}".format(row[0], row[1], row[2], row[3]))
                            msg_output = "{:>7} {:^20} {:^20} {:^9}\r\n\r\n".format(row[0], row[1], row[2], row[3])
                            ClientSocket.send(msg_output.encode('utf-8'))
                    continue
        ## read post and read comment
        if len(msg_split) == 2 and msg_split[0] == "read":
            cursor = c.execute('SELECT * FROM POSTS WHERE PID = ?', (msg_split[1],)).fetchone()
            if cursor == None:
                print(cursor, "Post is not exist.")
                msg_err = "Post is not exist.\r\n"
            else:
                cursor = c.execute("SELECT USERS.Username, POSTS.TITLE, POSTS.DT FROM POSTS INNER JOIN USERS ON POSTS.UID=USERS.UID WHERE POSTS.PID = ?", (msg_split[1], )).fetchone()
                print(cursor[0], cursor[1], cursor[2])
                msg_output = "Author : {:>20} \r\nTitle  : {:>20} \r\nDate   : {:>20}\r\n--\r\n".format(cursor[0], cursor[1], cursor[2])
                ClientSocket.send(msg_output.encode('utf-8'))
                PostPtr = open("data/post/{}".format(msg_split[1]), 'r')
                Rcontent = PostPtr.readlines()
                for i in range(len(Rcontent)):
                    msg_output = Rcontent[i] + "\r"
                    ClientSocket.send(msg_output.encode('utf-8'))
                msg_output = "--"
                ClientSocket.send(msg_output.encode('utf-8'))
                CommentPtr = open("data/comment/{}".format(msg_split[1]), 'r')
                Rcomment = CommentPtr.readlines()
                for i in range(len(Rcomment)):
                    msg_output = Rcomment[i] + "\r"
                    ClientSocket.send(msg_output.encode('utf-8'))
                msg_output = "\r\n"
                ClientSocket.send(msg_output.encode('utf-8'))
                continue
        ## delete the post
        if len(msg_split) == 2 and msg_split[0] == "delete-post":
            if login == -1:
                msg_err = "Please login first.\r\n"
            else:
                cursor = c.execute('SELECT * FROM POSTS WHERE PID = ?', (msg_split[1],)).fetchone()
                if cursor == None:
                    print(cursor, "Post is not exist.")
                    msg_err = "Post is not exist.\r\n"
                elif cursor[3] != login:
                    print("Owner is:",  cursor[3])
                    msg_err = "Not the post owner.\r\n"
                else:
                    cursor = c.execute('DELETE FROM POSTS WHERE PID = ?', (msg_split[1],))
                    conn.commit()
                    print("POST delete is success")
                    msg_suc = "Delete successfully.\r\n"
        ## update the post
        if msg_input.startswith("update-post ") and len(msg_split) > 2:
            if login == -1:
                msg_err = "Please login first.\r\n"
            else:
                cursor = c.execute('SELECT * FROM POSTS WHERE PID = ?', (msg_split[1],)).fetchone()
                if cursor == None:
                    print(cursor, "Post is not exist.")
                    msg_err = "Post is not exist.\r\n"
                elif cursor[3] != login:
                    print("Owner is:",  cursor[3])
                    msg_err = "Not the post owner.\r\n"
                elif msg_split[2] == "--title":
                    UTitle = msg_input.split(" --title ") 
                    print("I want to update the title, and the new title is:", UTitle[1])	
                    cursor = c.execute('UPDATE POSTS SET TITLE = ? WHERE PID = ?', (UTitle[1], msg_split[1]))
                    conn.commit()
                    msg_suc = "Update successfully.\r\n"
                elif msg_split[2] == "--content":
                    UContent = msg_input.split(" --content ") 
                    print("I want to update the content, and the new content is:", UContent[1])
                    cnt = UContent[1].split("<br>")
                    os.system("rm data/post/{}".format(msg_split[1]))
                    for iter_cnt in cnt:
                        print(iter_cnt)
                        os.system("echo {} >> data/post/{}".format(iter_cnt, msg_split[1]))
                    msg_suc = "Update successfully.\r\n"
        ## comment
        if msg_input.startswith("comment ") and len(msg_split) > 1:
            if login == -1:
                msg_err = "Please login first.\r\n"
            else:
                cursor = c.execute('SELECT * FROM POSTS WHERE PID = ?', (msg_split[1],)).fetchone()
                if cursor == None:
                    print(cursor, "Post is not exist.")
                    msg_err = "Post is not exist.\r\n"
                else:
                    cursor = c.execute('SELECT * FROM USERS WHERE UID = ?', (login,)).fetchone()
                    Cname = cursor[1]
                    starts = "comment " + msg_split[1] + " "
                    Ccomment = msg_input.replace(starts, "", 1)
                    print("I am ", Cname, "and i want to comment", Ccomment, "in", msg_split[1])
                    os.system("echo {:<20} : {:<20} >> data/comment/{}".format(Cname, Ccomment, msg_split[1]))
                    msg_suc = "Comment successfully.\r\n"

        ## Command not found
        if msg_input.startswith("register"):
            msg_Usage = "Usage: register <username> <email> <password>\r\n"
        elif msg_input.startswith("login"):
            msg_Usage = "Usage: login <username> <password>\r\n"
        elif msg_input.startswith("whoami"):
            msg_Usage = "Usage: whoami\r\n"
        elif msg_input.startswith("logout"):
            msg_Usage = "Usage: logout\r\n"
        elif msg_input.startswith("exit"):
            msg_Usage = "Usage: exit\r\n"
        elif msg_input.startswith("create-board"):
            msg_Usage = "Usage: create-board <borad-name>\r\n"
        elif msg_input.startswith("list-board"):
            if hashtag in msg_input:
                msg_Usage = "Usage: list-board ##<key>\r\n"
            else:
                msg_Usage = "Usage: list-board\r\n"
        elif msg_input.startswith("create-post"):
            msg_Usage = "Usage: create-post <board-name> --title <title> --content <content>\r\n"
        elif msg_input.startswith("list-post"):
            if hashtag in msg_input:
                msg_Usage = "Usage: list-post <board-name> ##<key>\r\n"
            else:
                msg_Usage = "Usage: list-post <board-name>\r\n"
        elif msg_input.startswith("read"):
            msg_Usage = "Usage: read <post-id>\r\n"
        elif msg_input.startswith("delete-post"):
            msg_Usage = "Usage: delete-post <post-id>\r\n"
        elif msg_input.startswith("update-post"):
            msg_Usage = "Usage: update-post <post-id> --title/content <new>\r\n"        
        elif msg_input.startswith("comment"):
            msg_Usage = "Usage: comment <post-id> <comment>\r\n" 
        elif msg_input != "":
            msg_Usage = "Command not found\r\n"
        ## output to client
        if msg_suc != "":
            ClientSocket.send(msg_suc.encode('utf-8'))
            msg_suc = ""
        elif msg_err != "":
            ClientSocket.send(msg_err.encode('utf-8'))
            msg_err = ""
        else:
            ClientSocket.send(msg_Usage.encode('utf-8'))
            msg_Usage = ""


bind_ip = "0.0.0.0"
bind_port = 1031

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

server.bind((bind_ip,bind_port))

server.listen(17)
print ("[*] Listening on  ", bind_ip,  bind_port)

while True:
    client,addr = server.accept()
    print ("New connection :", addr)
    _thread.start_new_thread(Client_Work, (client, addr))
