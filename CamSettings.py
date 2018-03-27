#!/usr/bin/python
import requests
import time
# 		no leading slash after folder name
DATABASE_FILE = '/frames.db'
#SAVE_PATH = '/run/user/1000/gvfs/sftp:host=192.168.0.112,user=pi/home/pi/usb/Juan/Media/sec.cam'
# 
SAVE_PATH = '/home/pi/usb/Juan/Media/sec.cam'

CAM_ADDRESSES = {'lg':'192.168.0.147:8080'}


def get_status(url):
    websession = requests.session()
    status = '/status.json?show_avail=1'
    status = websession.get(url+status).json()

    for stat in status:
        print('{} {}\n'.format(stat, status[stat]))
        time.sleep(.05)
    websession = requests.session()
    status = '/status.json?show_avail=1'
    status = websession.get(url+status).json()

    print(status.keys())
    curvals = status['curvals']
    print(curvals)

def get_sensors(url):
    websession = requests.session()
    sensors = '/sensors.json'
    sensors = websession.get(url+sensors).text
    print(sensors)

def setSett(url, setting, value):
    websession = requests.session()
    path = '/settings/{}?set={}'.format(setting, value)

    if setting == 'zoom':
        # pass value from 0 - 100 (percent)
        path = '/ptz?zoom=' + value

    websession.get(url + path)

def statFor(key):
    websession = requests.session()
    status = '/status.json?show_avail=1'
    status = websession.get(url+status).json()

    #print(status.keys())
    curvals = status['curvals'][key]
    print("{} {}".format(key, curvals))


if __name__ == "__main__":
    url = 'http://192.168.0.147:8080'
    #get_status(url)
    #get_sensors('http://192.168.0.147:8080')
    #setSett(url, 'zoom','2')
    #setSett(url, 'quality', '15')
    #setSett(url, 'night_vision', 'on')
    quality = 49
    setSett(url, 'quality', str(quality))
    zoom = 1
    while zoom < 100:
        print(zoom)
        setSett(url, 'zoom', str(zoom))
        zoom += 1
        time.sleep(.5)
    while zoom > 1:
        print(zoom)
        setSett(url, 'zoom', str(zoom))
        zoom -= 1
        time.sleep(.5)




