#!/usr/bin/env python3

"""
This is a NodeServer for SmartBlinds written by automationgeek (Jean-Francois Tremblay)
based on the NodeServer template for Polyglot v2 written in Python2/3 by Einstein.42 (James Milne) milne.james@gmail.com
"""

import polyinterface
import hashlib
import time
import json
import sys
from copy import deepcopy
from smartblinds_client import SmartBlindsClient

LOGGER = polyinterface.LOGGER
SERVERDATA = json.load(open('server.json'))
VERSION = SERVERDATA['credits'][0]['version']

def get_profile_info(logger):
    pvf = 'profile/version.txt'
    try:
        with open(pvf) as f:
            pv = f.read().replace('\n', '')
    except Exception as err:
        logger.error('get_profile_info: failed to read  file {0}: {1}'.format(pvf,err), exc_info=True)
        pv = 0
    f.close()
    return { 'version': pv }

class Controller(polyinterface.Controller):

    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'Blinds'
        self.queryON = False
        self.email = ""
        self.password = ""
        self.hb = 0
        self.client  = None

    def start(self):
        LOGGER.info('Started Blinds for v2 NodeServer version %s', str(VERSION))
        self.setDriver('ST', 0)
        try:
            if 'email' in self.polyConfig['customParams']:
                self.email = self.polyConfig['customParams']['email']
            else:
                self.email = ""
                
            if 'password' in self.polyConfig['customParams']:
                self.password = self.polyConfig['customParams']['password']
            else:
                self.password = ""
            
            if self.email == "" or self.password == "" :
                LOGGER.error('Blinds requires email, password, parameters to be specified in custom configuration.')
                return False
            else:
                self.check_profile()
                self.discover()

        except Exception as ex:
            LOGGER.error('Error starting Blinds NodeServer: %s', str(ex))
    
    def query(self):
        for node in self.nodes:
            self.nodes[node].reportDrivers()
    
    def shortPoll(self):
        self.setDriver('ST', 1)
        for node in self.nodes:
            if self.nodes[node].queryON == True :
                self.nodes[node].update()

    def longPoll(self):
        self.heartbeat()
        try:
            self.client.login()
        except Exception as ex : # Alot of timeout error is expected with the bridge, retrying at next query
            LOGGER.warning('Query: %s', str(ex))

    def heartbeat(self):
        LOGGER.debug('heartbeat: hb={}'.format(self.hb))
        if self.hb == 0:
            self.reportCmd("DON",2)
            self.hb = 1
        else:
            self.reportCmd("DOF",2)
            self.hb = 0

    def discover(self, *args, **kwargs):      
        self.client = SmartBlindsClient(self.email,self.password)
        self.client.login()
        blinds, rooms = self.client.get_blinds_and_rooms()
        
        count = 1
        for blind in blinds:
            myhash =  str(int(hashlib.md5(blind.name.encode('utf8')).hexdigest(), 16) % (10 ** 8))   
            myBlind = []
            myBlind.append(blind)
            self.addNode(Blind(self,self.address,myhash,  "blind_" + str(count), self.client, myBlind ))
            count = count + 1
        
    def delete(self):
        LOGGER.info('Deleting Blinds')

    def check_profile(self):
        self.profile_info = get_profile_info(LOGGER)
        # Set Default profile version if not Found
        cdata = deepcopy(self.polyConfig['customData'])
        LOGGER.info('check_profile: profile_info={0} customData={1}'.format(self.profile_info,cdata))
        if not 'profile_info' in cdata:
            cdata['profile_info'] = { 'version': 0 }
        if self.profile_info['version'] == cdata['profile_info']['version']:
            self.update_profile = False
        else:
            self.update_profile = True
            self.poly.installprofile()
        LOGGER.info('check_profile: update_profile={}'.format(self.update_profile))
        cdata['profile_info'] = self.profile_info
        self.saveCustomData(cdata)

    def install_profile(self,command):
        LOGGER.info("install_profile:")
        self.poly.installprofile()

    id = 'controller'
    commands = {
        'QUERY': query,
        'DISCOVER': discover,
        'INSTALL_PROFILE': install_profile,
    }
    drivers = [{'driver': 'ST', 'value': 1, 'uom': 2}]

class Blind(polyinterface.Node):

    def __init__(self, controller, primary, address, name, client, blind):

        super(Blind, self).__init__(controller, primary, address, name)
        self.queryON = True
        self.client = client
        self.blind = blind

    def start(self):
        self.setDriver('ST', 101,True)

    def setOn(self, command):
        try :
            self.client.set_blinds_position(self.blind, 100)
            self.setDriver('ST', 100,True)
        except Exception as ex : # Alot of timeout error is expected with the bridge, retrying at next query
            LOGGER.warning('setOn: %s', str(ex))
        
    def setOff(self, command):
        try :
            self.client.set_blinds_position(self.blind, 0)
            self.setDriver('ST', 0,True)
        except Exception as ex : # Alot of timeout error is expected with the bridge, retrying at next query
            LOGGER.warning('setOff: %s', str(ex))
    
    def query(self):
        self.reportDrivers()
    
    def update(self):
        try :
            states = self.client.get_blinds_state(self.blind)
            open = states[self.blind[0].encoded_mac].position

            if open > 1 :
                self.setDriver('ST', 100,True) 
            else :
                self.setDriver('ST', 0,True) 
        except Exception as ex : # Alot of timeout error is expected with the bridge, retrying at next query
             LOGGER.warning('Query: %s', str(ex))
                
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 79}]

    id = 'SMART_BLINDS'
    commands = {
                    'CLOSE': setOn,
                    'OPEN': setOff
                }

if __name__ == "__main__":
    try:
        polyglot = polyinterface.Interface('BlindsNodeServer')
        polyglot.start()
        control = Controller(polyglot)
        control.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
