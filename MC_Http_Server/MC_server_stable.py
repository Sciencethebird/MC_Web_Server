from flask import Flask, render_template, redirect, url_for, Response, jsonify
import pandas as pd
import numpy as np
import subprocess
from subprocess import *
from io import StringIO
import time
from datetime import datetime
import threading

app = Flask(__name__)


# chech if server is rinnig ising tasklist
def check_running(process):
    #global window, status, switch
    result = subprocess.run(['start','/B','tasklist.exe'], stdout=subprocess.PIPE, shell= True).stdout
    result = result[158:].decode("utf-8")

    info = []
    lines  = StringIO(result).readlines()
    for line in lines:
        seg = line.split()
        temp = [' '.join(seg[:-5]),seg[-5],seg[-4],seg[-3], seg[-2]]
        info.append(temp)

    df = pd.DataFrame(np.array(info),
                   columns=['Process', 'PID', 'Session Name', 'Session', 'RAM'])
    df = df.set_index('Process')

    try: 
   
        RAM = df['RAM'][process]
        #print(RAM)
        RAM = int(RAM.replace(',', ''))
        if RAM> 1000000 and RAM < 5000000:
            "[Server Status]: Online"
            return True
    except: 
        print("[Server Status]: Offline")
        return False
        #pid = df['PID'][process] #use iloc if you have multiple instance
 
# for streaming
def stream_template(template_name, **context):
    # http://flask.pocoo.org/docs/patterns/streaming/#streaming-from-templates
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    # uncomment if you don't need immediate reaction
    ##rv.enable_buffering(5)
    return rv
        


class message_center():
    def __init__(self):
        pass

class server_console():
    def __init__(self):

        # status variable
        self.server_status = False
        self.launching = False

        # pipe to server.exe
        self.server = None
        self.t = None # std thread

        # message history
        self.message_count = 4
        self.history = ""
        self.msg = ""
        self.player_list = {}
        self.player_list_msg = "<li>None</li>"
            
        
    # server message thread, comunicate with server.exe
    def running(self):
        while True:
            #print(self.server.pid)
            try:
                resp = self.server.stdout.readline().decode('UTF-8',"ignore") # ignore if there are chinese character         
            except Exception as e:
                print(e)
                print("error")
                self.msg = ""
                return

            #print("servvvvv", resp)
            resp = resp.replace('"', ' ')
            #if there are "\r\n" or '""' in the string the html will fail
            resp = resp[:-2] # remove newline character
            
            self.history = self.history+ resp +"<br>"
            self.msg = resp.split(" ")
            self.message_count +=1

            try:
                self.msg[4]
            except:
                print("message too short")
                continue

            if self.msg[4] == "joined":
                    self.player_list[self.msg[3]] = 1
            elif self.msg[4] == "left":
                    self.player_list[self.msg[3]] = 0         
                          
            self.player_list_msg = ""
            for k, v in self.player_list.items():
                if v == 1:
                    self.player_list_msg += ("<li>"+k+"</li>")
            if self.player_list_msg == "":
                self.player_list_msg = "<li>None</li>"
        
    def start(self):
        if self.server_status or self.launching:
            return
        self.launching = True
        self.server = Popen("cd C:/Users/Sciencethebird/MC_Server&&java -d64 -Xms4G -Xmx4G -jar server.jar --port 69", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        print("starting server...")
        self.t = threading.Thread(target = self.running)
        self.t.start()

    def stop(self):
        print("stopping server")
        #if check_running("java.exe"):
        if self.running:
            try:
                time.sleep(2)
                self.server.stdout.flush()       
                self.server.stdin.write(bytes("stop\n", "ascii"))
                self.server.stdin.flush()
                while self.msg[-1] != "saved":
                    print("turning off",self.msg[-1])
                    pass
               
                #while True:
                    #if not check_running("java.exe"):
                self.server_status = False
                self.server = None
                self.history = ""
                self.message_count = 4
                self.player_list = {}
                self.player_list_msg = "<li>None</li>"
                self.msg = ""            
                        #break
            except Exception as e:
                print(e)
    
    def onoff_message(self):
        #print(self.server_status, self.launching )
        if self.server_status == False and self.launching == False:
            print("Server Offline")
            yield '#CD5C5C',"Offline", ">\tPress Start !", "0%", "Server is Currently Offline...", "<li>None</li>"
            return

        first = True
        while True:
            time.sleep(0.5)

            out = ">_\t"+" ".join(self.msg[3:])
            #print(out)
            #print(self.msg)
            progress = str(self.message_count*100 //30)+"%"
            if self.launching:
                # yield status_color, status_text, launching_message, prograss_bar_variable, message_board, player_list
                if first:
                    yield '#CD5C5C',"Launching....", ">  Allocating Memory.....", "10%", "Launching server.exe", "<li>None</li>"
                    first = False
                    while self.msg == "":
                        pass
                elif self.msg[3] =="Done":
                    self.server_status = True
                    self.launching = False
                    yield '#4CAF50',"Online"," ".join(self.msg[3:5]), "100%" , self.history, "<li>None</li>"
                    #return
                else:
                    yield '#CD5C5C',"Launching....", out, progress, out,"<li>None</li>"
            elif self.server_status:   
                #print(self.history)
                yield '#4CAF50',"Online", out, "100%", self.history, self.player_list_msg

            else:
                yield '#CD5C5C',"Offline", ">\tPress Start !", "0%", "Server is Currently Offline...", "<li>None</li>"
                return
          

MCS = server_console()

@app.route('/',methods= ['GET'])
def main_page():
    global server_status
    print("\n[Request]: Main Page, {}\n".format(datetime.now()) )
    return Response(stream_template('main.txt', data=MCS.onoff_message()))
    
@app.route('/start/')
def start_page():
    print("\n[Request]: Start, {}\n".format(datetime.now()) )
    MCS.start()
    return redirect(url_for('main_page'))

@app.route('/end/')
def stop_server():
    print("\n[Request]: Stop, {}\n".format(datetime.now()) )
    MCS.stop()
    return redirect(url_for('main_page'))

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='192.168.50.142', port=420)
