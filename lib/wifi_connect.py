import network
import time


def do_connect(ssid, password, ip=None, subnet='255.255.255.0', gateway='192.168.86.1', dns='192.168.86.1'):
    wlan_sta = network.WLAN(network.STA_IF)
    wlan_sta.active(True)
    if wlan_sta.isconnected():
        return None
    if (ip != None):
        # Set the address so it is always the same.
        wlan_sta.ifconfig((ip, subnet, gateway, dns))

    print('Trying to connect to %s...' % ssid)
    wlan_sta.connect(ssid, password)
    for retry in range(100):
        connected = wlan_sta.isconnected()
        if connected:
            break
        time.sleep(0.1)
        print('.', end='')
    if connected:
        print('\nConnected. Network config: ', wlan_sta.ifconfig())
    else:
        print('\nFailed. Not Connected to: ' + ssid)
    return connected
