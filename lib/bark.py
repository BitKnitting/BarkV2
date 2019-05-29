from wifi_connect import do_connect
import usocket as socket
from machine import Pin,Timer
CONTENT_PREAMBLE=b"HTTP/1.0 200 OK \n\n   "
OPEN_PIN=4
CLOSE_PIN=5
WLAN_PROFILE='lib/wifi.dat'
class Bark:
 amount_of_movement_ms=22500
 def __init__(self,open_pin=4,close_pin=5):
  self.timer=Timer(-1)
  with open(WLAN_PROFILE)as f:
   line=f.readline()
  self.ssid,self.password=line.strip("\n").split(";")
  print("ssid: {}. password: {}".format(self.ssid,self.password))
 def _send_response(self,conn,specific):
  content=CONTENT_PREAMBLE+bytes(specific,'utf-8')
  conn.sendall(content)
 def _turn_pin_off_just_in_case(self,open_close_pin):
  pin=Pin(open_close_pin,Pin.OUT)
  pin.off()
 def _timer_callback(self,pin):
  print('in timer callback.  pin: {}'.format(pin))
  pin.off()
 def _do_actuator(self,gpio_pin):
  pin=Pin(gpio_pin,Pin.OUT)
  pin.off()
  pin.on()
  self.timer.deinit()
  self.timer.init(period=self.amount_of_movement_ms,mode=Timer.ONE_SHOT,callback=lambda t:self._timer_callback(pin))
 def _setMovementTime(self,strWithTime):
  loc_special_char=strWithTime.find("&")
  if(loc_special_char!=-1):
   self.amount_of_movement_ms=int(strWithTime[loc_special_char+1:loc_special_char+3])
  else:
   self.amount_of_movement_ms=30
  print('amount of ms to move: {}'.format(self.amount_of_movement_ms))
 def listen(self,ip=None,port=8005):
  do_connect(self.ssid,self.password,ip)
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
  s.bind(('',port))
  s.listen(1)
  counter=0
  while True:
   conn,addr=s.accept()
   print('Got connection #{} from {}'.format(counter,addr))
   counter+=1
   request=conn.recv(1024)
   request=str(request)
   open_door=request.find('open')
   close_door=request.find('close')
   exit_listen=request.find('exit')
   hello_listen=request.find('hello')
   stop_listen=request.find('stop')
   if(hello_listen!=-1 and hello_listen<10):
    self._send_response(conn,'hello')
   elif(open_door!=-1 and open_door<10):
    self._setMovementTime(request)
    self._turn_pin_off_just_in_case(CLOSE_PIN)
    self._do_actuator(OPEN_PIN)
    self._send_response(conn,'opening door for '+str(self.amount_of_movement_ms)+' ms')
   elif(close_door!=-1 and close_door<10):
    self._setMovementTime(request)
    self._turn_pin_off_just_in_case(OPEN_PIN)
    self._do_actuator(CLOSE_PIN)
    self._send_response(conn,'closing door for '+str(self.amount_of_movement_ms)+' ms')
   elif(stop_listen!=-1 and stop_listen<10):
    self.timer.deinit()
    self._turn_pin_off_just_in_case(OPEN_PIN)
    self._turn_pin_off_just_in_case(CLOSE_PIN)
    self._send_response(conn,'stopped')
   elif(exit_listen!=-1 and exit_listen<10):
    self.timer.deinit()
    self._turn_pin_off_just_in_case(OPEN_PIN)
    self._turn_pin_off_just_in_case(CLOSE_PIN)
    conn.close()
    print('received a request to exit, buh-bye')
    break
   else:
    self._send_response(conn,'The command received was not valid.')
   conn.close()
  s.close()
# Created by pyminifier (https://github.com/liftoff/pyminifier)
