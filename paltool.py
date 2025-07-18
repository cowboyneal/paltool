import json
import os
import requests
import subprocess

from flask import Flask, render_template
app = Flask(__name__)
app.config.from_object('config')


def url2dict(url):
    if url is None:
        return None

    r = None

    try:
        r = requests.get(url, headers={'Authorization': 'Basic ' +
                                        app.config['LOGIN_TOKEN']})
    except: Exception

    if r != None and r.status_code == 200:
        return r.json()
    else:
        return None


def get_palworld_status():
    return os.path.isfile(app.config['PID_FILE'])


def get_headers():
    return {
        'Authorization': 'Basic ' + app.config['LOGIN_TOKEN'],
        'Content-Type': 'application/json',
    }


@app.route('/')
def paltool():
    server_status = get_palworld_status()

    server_info = url2dict(app.config['BASE_URL'] + 'info')
    player_list = url2dict(app.config['BASE_URL'] + 'players')

    return render_template('index.html',
                           server_status=server_status,
                           server_info=server_info,
                           player_list=player_list)


@app.route('/message/<string:message>')
def send_message(message):
    url = app.config['BASE_URL'] + 'announce'
    
    payload = json.dumps({
        'message': message
    })

    try:
        response = requests.request("POST", url, headers=get_headers(),
                                    data=payload)
    except: Exception

    return '200'


@app.route('/start-server')
def start_server():
    home_dir = os.path.expanduser('~' + app.config['PALWORLD_USER'])
    if home_dir:
        subprocess.Popen(['/usr/bin/sudo', '-u', app.config['PALWORLD_USER'],
                          home_dir + '/bin/palstart'])
    return '200'


@app.route('/stop-server')
def stop_server():
    url = app.config['BASE_URL'] + 'shutdown'

    payload = json.dumps({
        'waittime': 30,
        'message': 'The server will shut down in 30 seconds. Please log out in a safe spot.'
    })

    try:
        response = requests.request("POST", url, headers=get_headers(),
                                    data=payload)
    except: Exception

    subprocess.Popen(['/usr/bin/sudo', '-u', app.config['PALWORLD_USER'],
                      '/bin/rm', app.config['PID_FILE']])

    return '200'


@app.route('/force-stop-server')
def force_stop_server():
    url = app.config['BASE_URL'] + 'stop'

    try:
        response = requests.request("POST", url, headers=get_headers())
    except: Exception

    subprocess.Popen(['/usr/bin/sudo', '-u', app.config['PALWORLD_USER'],
                      '/bin/rm', app.config['PID_FILE']])

    return '200'
