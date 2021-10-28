## This nodeserver has been converted to run on PG3. The code has been moved to https://github.com/UniversalDevicesInc-PG3/udi-MySmartBlinds-nodeserver

# MySmartBlinds

This Poly provides an interface between MySmartBlinds and Polyglot v2 server. Only support Blind and required a Bridge. Beware the control of blind is not perfect. There connectivity issue between the bridge and blind at time.  
https://www.tiltsmarthome.com/products/smart-hub

## Installation instructions

##### You can install from Polyglot V2 store or manually :

- cd ~/.polyglot/nodeservers
- git clone https://github.com/therealmysteryman/udi-MySmartBlinds-nodeserver.git
- run ./install.sh to install the required dependency.
- Add a custom variable email and password. That would be your account credential used to connect to MySmartBlind app.
- Based on the Node Server Template - https://github.com/Einstein42/udi-poly-template-python
