import socket
import os
import boto3
import time



POS = "POS"
NEG = "NEG"
target_bucket = None
board_Col_name = "{:^7} {:^20} {:^20}".format("Index", "Name", "Moderator")
post_Col_name = "{:^7} {:^20} {:^20} {:^9}".format("ID", "Title", "Author", "Date")
mail_Col_name = "{:^7} {:^20} {:^20} {:^9}".format("ID", "Subject", "From", "Date")


s3 = boto3.resource('s3')

def MKDIR():
    Pdata = "./.data"
    Ppost = "./.data/post"
    Pcomment = "./.data/comment"
    Pmail = "./.data/mail"
    try:
      os.makedirs(Pdata)
      os.makedirs(Ppost)
      os.makedirs(Pcomment)
      os.makedirs(Pmail)
    except FileExistsError:
      return

def RECEIVE():
    while True:
        try:
            msg_in = s.recv(1024).decode('utf-8')
            return msg_in
        except:
            pass    

def SEND(CMD):
    while True:
        try:
            s.send(CMD.encode('utf-8'))
            break
        except:
            pass



def INT_handling(int_msg):
    response = -1
    if int_msg.startswith("SUC"):
    	int_msg = int_msg.replace("SUC ", "", 1)
    	response = 0
    elif int_msg.startswith("ERR"):
    	int_msg = int_msg.replace("ERR ", "", 1)
    	response = 1
    elif int_msg.startswith("USAGE"):
    	int_msg = int_msg.replace("USAGE ", "", 1)
    	response = 2
    elif int_msg.startswith("POS"):
    	return 3, int_msg
    elif int_msg.startswith("NEG"):
    	return 4, int_msg
    elif int_msg.startswith("DATA"):
        int_msg = int_msg.replace("DATA ", "", 1)
        response  = 5
    elif int_msg.startswith("TROBLE"):
        int_msg = int_msg.replace("TROBLE ", "", 1)
        return 6, int_msg

    print(int_msg)
    return response, int_msg

    


def CmdLine():
    cmd = input("% ")
    test = cmd.replace(' ', '')
    while test == "":
        cmd = input("% ")
        test = cmd.replace(' ', '')
    SEND(CMD = cmd)
    return cmd



def CBucketName():
    ti = str(time.time())
    BucketName = "netprolab3qsefthuk" + ti
    return BucketName


def REG(CMD):
    get = RECEIVE()
    response, trash = INT_handling(int_msg = get)
    if response == 3:
        BucketName = CBucketName()
        s3.create_bucket(Bucket = BucketName)
        SEND(CMD = BucketName)
        get = RECEIVE()
        INT_handling(int_msg = get)  
    else:
        pass
   



def LOGIN(CMD):
    get = RECEIVE()	
    response, BWN = INT_handling(int_msg = get)
    if response == 6:
        LoginHandling(BWN = BWN)

def LoginHandling(BWN):
    BN_WEL = BWN.split("# #") 
    BucketName = BN_WEL[0]
    WelcomeName = BN_WEL[1]
    print(WelcomeName)
    global target_bucket
    target_bucket = s3.Bucket(BucketName)
    return BucketName



def WHOAMI(CMD):
    get = RECEIVE()
    INT_handling(int_msg = get)


def LOGOUT(CMD):
    get = RECEIVE()
    INT_handling(int_msg = get)
    global target_bucket
    target_bucket = None


def CBOARD(CMD):
    get = RECEIVE()
    INT_handling(int_msg = get)


def LBOARD(CMD):
    get = RECEIVE()
    if get.startswith("DATA") or get.startswith("NEG"):
        print(board_Col_name)
    INT_handling(int_msg = get)

def LPOST(CMD):
    get = RECEIVE()
    if get.startswith("DATA") or get.startswith("NEG"):
        print(post_Col_name)
    INT_handling(int_msg = get)


def Get_BTC(CMD):
    CMD = CMD.replace("create-post ", "", 1) 
    BoardTitle = CMD.split(" --title ")                   
    TitleContent = BoardTitle[1].split(" --content ")
    Board = BoardTitle[0]
    Title = TitleContent[0]
    Content = TitleContent[1]
    return Board, Title, Content


def CPOST(CMD):
    get = RECEIVE()
    response, PidSMsg = INT_handling(int_msg = get)
    
    if response == 6:
        PidSMsg = PidSMsg.split("# #")
        PID = PidSMsg[0]
        print(PidSMsg[1])
        Board, Title, Content = Get_BTC(CMD = CMD)
        cnt = Content.split("<br>")
        for iter_cnt in cnt:
            # print(iter_cnt)
            os.system("echo {} >> ./.data/post/P{}".format(iter_cnt, PID))
        os.system("echo "" >> ./.data/comment/C{}".format(PID))
        target_bucket.upload_file("./.data/post/P{}".format(PID), "P{}".format(PID))
        target_bucket.upload_file("./.data/comment/C{}".format(PID), "C{}".format(PID))



def READPOST(CMD):
    get = RECEIVE()
    response, Info = INT_handling(int_msg = get)
    ## print author done
    if response == 6:
        RPid = CMD.split(" ")
        Pid = RPid[1]
        BNameInfo = Info.split("# #")
        BucketName = BNameInfo[0]
        INFO = BNameInfo[1]
        print(INFO)
        READtarget_bucket = s3.Bucket(BucketName)
        target_object1 = READtarget_bucket.Object("P{}".format(Pid)) 
        object_content = target_object1.get()["Body"].read().decode()
        target_object2 = READtarget_bucket.Object("C{}".format(Pid)) 
        object_comment = target_object2.get()["Body"].read().decode()
        print(object_content)
        print("--\n\r", object_comment)



def COMMENT(CMD):
    get = RECEIVE()
    response, BucketSucMsg = INT_handling(int_msg = get)
    if response == 6:
        msg_split = CMD.split(" ")
        PID = msg_split[1]
        starts = "comment " + PID + " "
        Ccomment = CMD.replace(starts, "", 1)

        BucketSucMsg = BucketSucMsg.split("# #")
        Ctarget_bucket = BucketSucMsg[0]
        Cname = BucketSucMsg[1]
        print(BucketSucMsg[2])

        os.system("echo {:<20} : {:<20} >> ./.data/comment/C{}".format(Cname, Ccomment, PID))
        POSTtarget_bucket = s3.Bucket(Ctarget_bucket)
        POSTtarget_bucket.upload_file("./.data/comment/C{}".format(PID), "C{}".format(PID))



def UPDATE(CMD):
    get = RECEIVE()
    response, BucketSucMsg = INT_handling(int_msg = get)
    if response == 0:
        msg_split = CMD.split(" ")
        PID = msg_split[1]
        if msg_split[2] == "--content":
        
            UContent = CMD.split(" --content ") 
            cnt = UContent[1].split("<br>")
            os.system("rm ./.data/post/P{}".format(PID))
            for iter_cnt in cnt:
                os.system("echo {} >> ./.data/post/P{}".format(iter_cnt, PID))
            target_bucket.upload_file("./.data/post/P{}".format(PID), "P{}".format(PID))



def MailTo(CMD):
    get = RECEIVE()
    response, MidRbucket = INT_handling(int_msg = get)
    if response == 6:
        MidRbucket = MidRbucket.split("# #")
        MID = MidRbucket[0]
        RBucket = MidRbucket[1]

        UNameSub = CMD.split(" --subject ")
        SubContent = UNameSub[1].split(" --content ")
        Subject = SubContent[0]
        

        Content = SubContent[1]
        cnt = Content.split("<br>")
        for iter_cnt in cnt:
            os.system("echo {} >> ./.data/mail/M{}".format(iter_cnt, MID))
        MailTarget_Bucket = s3.Bucket(RBucket)
        MailTarget_Bucket.upload_file("./.data/mail/M{}".format(MID), "M{}".format(MID))

        print(MidRbucket[2])


def LMAIL(CMD):
    get = RECEIVE()
    if get.startswith("DATA") or get.startswith("NEG"):
        print(mail_Col_name)
    INT_handling(int_msg = get)



def RPOST(CMD):
    get = RECEIVE()
    response, MidMsg = INT_handling(int_msg = get)
    if response == 6:
        MidMsg = MidMsg.split("# #")
        Mid = MidMsg[0]
        Msg = MidMsg[1]
        print(Msg)
        target_object = target_bucket.Object("M{}".format(Mid)) 
        object_content = target_object.get()["Body"].read().decode()
        print(object_content)





HOST = "3.92.193.75"
PORT = 1031

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.setblocking(0)
MKDIR()


welcome = RECEIVE()
print (welcome)



get = "" ## get is return msg from server
while True:
    cmd = CmdLine()


    if cmd == "exit":
    	break
    elif cmd.startswith("register"):
        REG(CMD = cmd)
    elif cmd.startswith("login"):
        LOGIN(CMD = cmd)
    elif cmd.startswith("whoami"):
        WHOAMI(CMD = cmd)
    elif cmd.startswith("logout"):
        LOGOUT(CMD = cmd)
    elif cmd.startswith("create-board"):
        CBOARD(CMD = cmd)
    elif cmd.startswith("list-board"):
        LBOARD(CMD = cmd)
    elif cmd.startswith("create-post"):
        CPOST(CMD = cmd)
    elif cmd.startswith("list-post"):
        LPOST(CMD = cmd)
    elif cmd.startswith("read"):
        READPOST(CMD = cmd)
    elif cmd.startswith("comment"):
        COMMENT(CMD = cmd)
    elif cmd.startswith("update-post"):
        UPDATE(CMD = cmd)
    elif cmd.startswith("mail-to"):
        MailTo(CMD = cmd)
    elif cmd == "list-mail":
        LMAIL(CMD = cmd)
    elif cmd.startswith("retr-mail"):
        RPOST(CMD = cmd)
    else:
        get = RECEIVE()
        INT_handling(int_msg = get)

























