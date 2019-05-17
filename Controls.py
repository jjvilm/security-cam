#!/usr/bin/python
import requests
import time
import random

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
    url = 'http://192.168.1.229:8080'
    #get_status(url)
    #get_sensors('http://192.168.0.147:8080')
    #setSett(url, 'zoom','2')
    #setSett(url, 'quality', '15')
    #setSett(url, 'night_vision', 'on')
    quality = 75
    sleep = .3
    counts = 100 

    setSett(url, 'quality', str(quality))
    #exit(0)
    zoom = 0
    setSett(url, 'zoom', str(zoom))
#    while counts >= 1:
#        while zoom <= 25:
#            print(zoom)
#            setSett(url, 'zoom', str(zoom))
#            zoom += 1
#            time.sleep(sleep)
#
#        #setSett(url, 'quality', str(99))
#        time.sleep(random.randrange(2,7))
#
#        while zoom >= 1:
#            print(zoom)
#            setSett(url, 'zoom', str(zoom))
#            zoom -= 1
#            time.sleep(sleep)
#
#        #setSett(url, 'quality', str(quality))
#        time.sleep(3)
#        counts -= 1
#
#
#
#
#
