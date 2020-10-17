from flask import Flask, request

app = Flask(__name__)

@app.route('/login', methods=['GET', 'POST']) 
def login():
    if request.method == 'POST': 
        return 'Hello ' + request.values['username'] 

    return "<form method='post' action='/login'><input type='text' name='username' />" \
            "</br>" \
           "<button type='submit'>Submit</button></form>"

if __name__ == '__main__':
    app.debug = True
    app.run()   