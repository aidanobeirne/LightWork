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
    def __init__(self, address='192.168.1.222', port=39900, timeout_in_s=60):
          self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          self.sock.connect((address, port))
          self.sock.settimeout(timeout_in_s)
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

    def move_wave_t(self, wavelength, transmission_id=1):
      """Sets the wavelength based on wavelength table. Returns an error if the wavemeter TCP connections
      is established
      Parameters:
        sock ~ socket object to use
        wavelength ~ (float) wavelength set point
        transmission_id ~ (int) Arbitrary integer for communications
      Returns:
        Nothing
      """
      self.send_msg(transmission_id,"move_wave_t", {"wavelength": [wavelength]})
      val = self.recv_msg()
      self.verify_msg(val,transmission_id=transmission_id,op="move_wave_t_reply")
      status = val["message"]["parameters"]["status"][0]
      if status == 0:
        return
      elif status == 1:
        raise SolstisError("move_wave_t: Failed, is your wavemeter configured?")
      else:
        raise SolstisError("Wavelength out of range.")

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
    def get_status(self, transmission_id=1):
        """Retrieves the system status information available to the user
        Parameters:
          sock ~ Socket object to use
          transmission_id ~ (int) arbitrary integer to use for communications
        Returns:
          A dictionary containing the following key/value pairs:
            "status" ~ 0 on a succesful call, and 1 otherwise 
            "wavelength" ~ The current wavelength in nm
            "temperature" ~ Current temperature in degrees Celcius
            "temperature_status" ~ "on" or "off"
            "etalon_lock" ~ "on","off","debug","error","search" or "low". See Manual.
            "etalon_voltage" ~ Reading in Volts
            "cavity_lock" ~ "on","off","debug","error","search" or "low"
            "resonator_voltage" ~ Reading in Volts
            "ecd_lock" ~ "not_fitted","on","off","debug","error","search" or "low"
            "ecd_voltage" ~ Reading in Volts
            "output_monitor" ~ Reading in Volts
            "etalon_pd_dc" ~ Reading in Volts
            "dither" ~ "on" or "off"
        Raises:
          SolstisError on operation failure
        """
    
        self.send_msg(transmission_id,"get_status")
        val = self.recv_msg()
        self.verify_msg(val,op="get_status_reply",transmission_id=transmission_id)
        status = val["message"]["parameters"]["status"][0]
        if status == 1:
          raise SolstisError("get_status failed: reason unknown")
        params = val["message"]["parameters"]
        return_val = {"status": 0}
        return_val["wavelength"] = params["wavelength"][0]
        return_val["temperature"] = params["temperature"][0]
        return_val["temperature_status"] = params["temperature_status"]
        return_val["etalon_lock"] = params["etalon_lock"]
        return_val["etalon_voltage"] = params["etalon_voltage"][0]
        return_val["cavity_lock"] = params["cavity_lock"]
        return_val["resonator_voltage"] = params["resonator_voltage"][0]
        return_val["ecd_lock"] = params["ecd_lock"]
        if params["ecd_voltage"] == "not_fitted":
          return_val["ecd_voltage"] = -float('inf')
        else:
          return_val["ecd_voltage"] = params["ecd_voltage"][0]
        return_val["output_monitor"] = params["output_monitor"][0]
        return_val["etalon_pd_dc"] = params["etalon_pd_dc"][0]
        return_val["dither"] = params["dither"]

        return return_val

    def set_wave_tolerance_m(self,tolerance=1.0,transmission_id=1):
        """Sets the tolerance for the sending of the set_wave_m final report
        Parameters:
          sock ~ Socket object to use for communications
          tolerance ~ (float) New tolerance value
          transmission_id ~ (int) Arbitrary integer for use in communications
        Returns:
          Nothing on successful execution
        Raises:
          SolstisError on failed execution
        """
        self.send_msg(transmission_id,"set_wave_tolerance_m",{"tolerance": tolerance})
        val = self.recv_msg()
        self.verify_msg(val,
                   transmission_id=transmission_id,
                   op="set_wave_tolerance_m_reply")
        status = val["message"]["parameters"]["status"][0]
        if status == 0:
          return
        elif status == 1:
          raise SolstisError("Could not set tolerance; No wavemeter connected")
        else:
          raise SolstisError("Could not set tolerance; Tolerance Value Out of Range")
    
    
    def close(self):
        self.sock.close()
    
if __name__=='__main__':
    import numpy as np
    solstis = Solstis()
#    solstis.etalon_lock(False)
#    solstis.move_wave_t(780)
    # solstis.set_wave_m_f_r(870)
#    scan_wavelengths = np.arange(750.0, 930.0, 10)
#    solstis.set_wave_m_f_r(wavelength=scan_wavelengths[0], timeout=30)
#    for wl in scan_wavelengths:
#        value = solstis.set_wave_m_f_r(wl)
#        if value == 0:
#            value = solstis.set_wave_m_f_r(wl)
#        print(value)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    