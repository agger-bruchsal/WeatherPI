#!/usr/bin/python2
#    $Revision: 1 $
#    $Author: Lukas Wingerberg $
#    $Date: 2018-06-29 $

"""JSON driver for the weewx weather system"""

from __future__ import with_statement
import backoff
import math
import time
import urllib2
import json
import weewx.units
import weedb
import weeutil.weeutil
import weewx.drivers
import weewx.wxformulas

DRIVER_NAME = 'JsonFeeder'
DRIVER_VERSION = "1.8"

# location of json sensor data
url = ("http://192.168.1.178")

def get_jsonparsed_data(url):
    """
    Receive the content of ``url``, parse it as JSON and return the object.

    Parameters
    ----------
    url : str

    Returns
    -------
    dict
    """
    response = urlopen_with_retry(url)
    data = response.read().decode("utf-8")
    return json.loads(data)

@backoff.on_exception(backoff.expo,
                      urllib2.URLError,
                      max_value=32)
def urlopen_with_retry(url):
    return urllib2.urlopen(url)

def loader(config_dict, engine):
    return JsonFeederDriver(**config_dict[DRIVER_NAME])

def confeditor_loader():
     return JsonFeederConfEditor()

class JsonFeederDriver(weewx.drivers.AbstractDevice):

    def __init__(self, **stn_dict):
        self.loop_interval = float(stn_dict.get('loop_interval',2.5))

    def genLoopPackets(self):
        while True:
            start_time = time.time()
            weatherdata = get_jsonparsed_data(url)['weatherdata']

            solar = int(weatherdata['lux']) * 0.0079

            _packet = {'dateTime': time.time(),
                      'usUnits' : weewx.METRIC,
                      'outTemp' : float(weatherdata['temperature']),
                      'outHumidity' : float(weatherdata['humidity']),
                      'pressure' : float(weatherdata['pressure']),
                      'radiation' : float(solar),
                      'UV' : float(weatherdata['UV_index']),
                          }
            _packet['dewpoint'] = weewx.wxformulas.dewpointC(_packet['outTemp'], _packet['outHumidity'])
            #_packet['barometer'] = weewx.wxformulas.sealevel_pressure_Metric(_packet['pressure'], self.altitude, _packet['outTemp'])
            #_packet['altimeter'] = weewx.wxformulas.altimeter_pressure_Metric(_packet['pressure'], self.altitude)
            _packet['heatdeg'] = weewx.wxformulas.heating_degrees(_packet['outTemp'], 18.333)
            _packet['cooldeg'] = weewx.wxformulas.cooling_degrees(_packet['outTemp'], 18.333)
            _packet['heatindex'] = weewx.wxformulas.heatindexC(_packet['outTemp'], _packet['outHumidity'])

            yield _packet

            sleep_time = (start_time - time.time()) + self.loop_interval
            #sleep_time = self.loop_interval
            if sleep_time > 0:
                  time.sleep(sleep_time)

class JsonFeederConfEditor(weewx.drivers.AbstractConfEditor):
    @property
    def default_stanza(self):
      return
