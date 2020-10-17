
from flask import Flask, render_template, redirect, url_for
import pandas as pd
import numpy as np
import subprocess
from subprocess import *
from io import StringIO
import time
from datetime import datetime
server_status = False
app = Flask(__name__)
server = None
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
    #q.config(command = lambda:quit())
    #print( df['RAM']["chrome.exe"] )

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
   
        


@app.route('/')
def main_page():
    global server_status
    print("\n[Request]: Main Page, {}\n".format(datetime.now()) )
    if check_running("java.exe"):
        return render_template('main.txt', variable='Online', fcolor='#4CAF50')
    else:
        return render_template('main.txt', variable='Offline',fcolor='#CD5C5C')

@app.route('/start/')
def start_server():
    global server_status, server
    print("\n[Request]: Start, {}\n".format(datetime.now()) )
    if check_running("java.exe") == False:
        
        server_status = True;
        #java -d64 -Xms4G -Xmx4G -jar server.jar --port 69 --nogui
        #pipe = subprocess.Popen(['C:/Users/Sciencethebird/MC_Server/lauch.bat'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        server = Popen("cd C:/Users/Sciencethebird/MC_Server&&java -d64 -Xms4G -Xmx4G -jar server.jar --port 69", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        print("starting server...")
        while True:
            resp = server.stdout.readline().decode()
            resp = resp.split(" ")
            print(resp[3])
            if resp[3] =="Done":
                break;
            #render_template('main.txt', variable='Launching...',fcolor='#CD5C5C'
    #check if server launch successfully
    for i in range(2000):
        time.sleep(0.5)
        if check_running("java.exe"):
            server_status = True;
            break
    
    return redirect(url_for('main_page'))

@app.route('/end/')
def stop_server():
    global server_status, server
    
    print("\n[Request]: Stop, {}\n".format(datetime.now()) )
    #server.stdout.flush()
    #server.stdin.flush()
    if check_running("java.exe"):
        try:
            #while True:
            time.sleep(2)
            #print(server.stdout.readline())
            server.stdout.flush()
                #command = input("> ")
                
            server.stdin.write(bytes("stop\n", "ascii"))
            server.stdin.flush()
            while True:
                resp = server.stdout.readline().decode()
                print(resp)
                if not check_running("java.exe"):
                    server_status = False
                    server = None
                    break
        except Exception as e:

            print(e)
    return redirect(url_for('main_page'))

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='192.168.50.142', port=420)
    while True:
        pass