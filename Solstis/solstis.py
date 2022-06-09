import time
import socket
import json


#Global variables for use within module
next_data = '' #Extra TCP socket data to carry forward for next read statement
          
#Exception class for Solstis specific errors
class SolstisError(Exception):
  """Exception raised when the Solstis response indicates an error

  Attributes:
    message ~ explanation of the error
  """
  def __init__(self,message):
    self.message = message

class Solstis():
    def __init__(self, address='192.168.1.222', port=39900):
          self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          self.sock.connect((address, port))
          self.sock.settimeout(10)
          self.start_link()
          
          
    def send_msg(self, transmission_id=99, op='start_link', params=None, debug=False):
      """
      Function to carry out the most basic communication send function
      s ~ Socket
      transmission_id ~ Arbitrary(?) integer
      op ~ String containing operating command
      params ~ dict containing Solstis Key/Value pairs as necessary
      """
      if params is not None:
        message = {"transmission_id": [transmission_id],
                   "op": op,
                   "parameters": params}
      else:
        message = {"transmission_id": [transmission_id],
                   "op": op}

      command = {"message": message}
      send_message = json.dumps(command).encode('utf8')
      if debug:
        print(send_message)
      self.sock.sendall(send_message)


    def recv_msg(self, timeout=10.):
      global next_data
      i = 0 #Index
      open_brc_count = 1 #Open Brace Count
      close_brc_count = 0 #Closing brace count
      #Initialize data
      data = next_data

      #Check For existing data and if so, parse it
      if len(data) > 0:
        if data[0] != "{":
          raise SolstisError("Stored data from previous TCP/IP is invalid.")
      
        #Check if existing data contains complete message
        for i in range(1,len(data)):
          if data[i] == "{":
            open_brc_count += 1
          elif data[i] == "}":
            close_brc_count += 1
            if close_brc_count == open_brc_count:
              next_data = data[i+1:len(data)]
              data = data[0:i+1]
              return json.loads(data)
      
      #There is NOT a complete message cached so we must continue to read TCP/IP

      #Start timing in case of timeout
      init_time = time.perf_counter()
      #Loop reading TCP/IP until there is some data
      while len(data) == 0:
        data += self.sock.recv(1024).decode('utf8')
        if time.perf_counter() - init_time > timeout:
          raise TimeoutError()

      #Check (if not already done so) that the message starts with a '{'
      if i == 0:
        if data[0] != "{":
          raise SolstisError("Received data from TCP/IP is invalid.")

      #Loop checking for complete message and receiving new data
      while True:
        if len(data) > i+1:
          for i in range(i+1,len(data)):
            if data[i] == "{":
              open_brc_count += 1
            elif data[i] == "}":
              close_brc_count += 1
              if close_brc_count == open_brc_count:
                next_data = data[i+1:len(data)]
                data = data[0:i+1]
                return json.loads(data)
        data += self.sock.recv(1024).decode('utf8')
        if time.perf_counter() - init_time > timeout:
          raise TimeoutError()

    def verify_msg(self, msg, op=None,transmission_id=None):
      msgID = msg["message"]["transmission_id"][0]
      msgOP = msg["message"]["op"]
      if transmission_id is not None:
        if msgID != transmission_id:
          err_msg = "Message with ID"+str(msgID)+" did not match expected ID of: "+\
                str(transmission_id)
          raise SolstisError(err_msg)
      if msgOP == "parse_fail":
        err_msg = "Mesage with ID "+str(msgID)+" failed to parse."
        err_msg += '\n\n'+str(msg)
        raise SolstisError(err_msg)
      if op is not None:
        if msgOP != op:
          msg = "Message with ID"+str(msgID)+"with operation command of '"+msgOP+\
                "' did not match expected operation command of: "+op
          raise SolstisError(msg)

    def start_link(self, transmission_id=99, ip_address='192.168.1.100'):
      self.send_msg(transmission_id,'start_link',{'ip_address': ip_address})
      val = self.recv_msg()
      self.verify_msg(val,transmission_id=transmission_id,op='start_link_reply')
      if val["message"]["parameters"]["status"] == "ok":
        return
      elif val["message"]["parameters"]["status"] == "failed":
        raise SolstisError("Link could not be formed")
      else:
        raise SolstisError("Unknown error: Could not determine link status")

    def set_wave_m(self, wavelength, transmission_id = 1, timeout=20.0):
      """Sets wavelength given that a wavelength meter is configured

      Parameters:
        sock ~ Socket object to use
        wavelength ~ (float) wavelength to tune to in nanometers
        transmission_id ~ (int) Arbitrary integer
      Returns:
        The wavelength of the most recent measurement made by the wavelength meter
      """
      wavelength = float(wavelength)
      self.send_msg(transmission_id,"set_wave_m",{"wavelength": [wavelength]})
      val = self.recv_msg(timeout=timeout)
      self.verify_msg(val,transmission_id=transmission_id,op="set_wave_m_reply")
      status = val["message"]["parameters"]["status"]
      if status == 1:
        raise SolstisError("No (wavelength) meter found.")
      elif status == 2:
        raise SolstisError("Wavelength Out of Range.")
      return val["message"]["parameters"]["wavelength"][0]

    #Same as above but requests a final report as well
    def set_wave_m_f_r(self, wavelength, transmission_id = 1, timeout = 20.0):
      """Sets wavelength given that a wavelength meter is configured

      Parameters:
        sock ~ Socket object to use
        wavelength ~ (float) wavelength to tune to in nanometers
        transmission_id ~ (int) Arbitrary integer
      Returns:
        The wavelength of the most recent measurement made by the wavelength meter
      """
      wavelength = float(wavelength)
      self.send_msg(transmission_id,"set_wave_m",{"wavelength": [wavelength],
                                                  "report": "finished"})
      val = self.recv_msg(timeout=timeout)
      self.verify_msg(val,transmission_id=transmission_id,op="set_wave_m_reply")
      status = val["message"]["parameters"]["status"]
      if status == 1:
        raise SolstisError("No (wavelength) meter found.")
      elif status == 2:
        raise SolstisError("Wavelength Out of Range.")
      #Final Report
      val = self.recv_msg(timeout=timeout)
      self.verify_msg(val,op="set_wave_m_f_r")
      #TODO: Check other variables
      return val["message"]["parameters"]["wavelength"][0]

    def poll_wave_m(self,transmission_id=1, timeout = 10.0):
      """Gets the latest Wavemeter reading and current wavelength tuning status

      Parameters:
        sock ~ socket object to use
        transmission_id ~ (int) Arbitrary integer to use for communications
      Returns:
        Tuple containing (in increasing index order):
          -floating point value for current wavelength
          -Boolean stating whether tuning is done/inactive (True = Not tuning)
      """

      self.send_msg(transmission_id,"poll_wave_m")
      val = self.recv_msg()
      self.verify_msg(val,transmission_id=transmission_id,op="poll_wave_m_reply")
      status = val["message"]["parameters"]["status"][0]
      if status == 1:
        raise SolstisError("No (wavelength) meter found.")
      elif status == 0 or status == 3:
        status = True #Not tuning
      else:
        status = False #Still Tuning
      return val["message"]["parameters"]["current_wavelength"][0], status
  
    def stop_wave_m(self, transmission_id=1):
      """Stop the currently active wavelength tuning operation.
    
      Parameters:
        sock ~ socket object to use
        transmission_id ~ (int) Arbitrary integer for communications
      Returns:
        Nothing
      """

      self.send_msg(transmission_id,"stop_wave_m")
      val = self.recv_msg()
      self.verify_msg(val,transmission_id=transmission_id,op="stop_wave_m_reply")
      status = val["message"]["parameters"]["status"][0]
      if status == 0:
        return
      elif status == 1:
        raise SolstisError("stop_wave_m: Failed, is your wavemeter configured?")

    def etalon_lock(self,lock,transmission_id=1):
      """Either locks or unlocks the etalon
    
      Parameters:
        sock ~ Socket object to use for communications
        lock ~ (Boolean) True to lock the etalon, False to unlock it 
        transmission_id ~ (int) arbitrary integer for use in communications
      Returns:
        Nothing on success
      Raises:
        SolstisError on failure
      """
    
      if lock == True:
        lock = "on"
      else:
        lock = "off"
    
      self.send_msg(transmission_id,"etalon_lock",{"operation": lock})
      val = self.recv_msg()
      self.verify_msg(val,op="etalon_lock_reply",transmission_id=transmission_id)
      status = val["message"]["parameters"]["status"][0]
      if status == 0:
        return
      else:
        raise SolstisError("etalon_lock Failed; Reason Unknown")
    
    
    def close(self):
        self.sock.close()
    
if __name__=='__main__':
    import numpy as np
    solstis = Solstis()
#    solstis.etalon_lock(False)
#    solstis.move_wave_t(780)
    solstis.set_wave_m_f_r(870)
#    scan_wavelengths = np.arange(750.0, 930.0, 10)
#    solstis.set_wave_m_f_r(wavelength=scan_wavelengths[0], timeout=30)
#    for wl in scan_wavelengths:
#        value = solstis.set_wave_m_f_r(wl)
#        if value == 0:
#            value = solstis.set_wave_m_f_r(wl)
#        print(value)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    