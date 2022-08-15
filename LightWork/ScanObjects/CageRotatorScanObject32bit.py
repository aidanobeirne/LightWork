import thorlabs_apt as apt
import time


class CageRotatorScanObject():
    def __init__(self, scan_values, SN_motor='55164594', name='Cage Rotator', scan_nest_index=0):
        """
    
        Parameters
        ----------
        scan_values : LIST OR ARRAY
            ANGLES TO SCAN CAGE ROTATOR OVER. 
        SN_motor : STR, optional
            SERIAL NUMBER OF THE THORLABS CAGE ROTATOR. The default is '55164244'.
        name : STR, optional
            UNIQUE NAME FOR THIS CAGE ROTATOR. The default is 'analyzer'.
        scan_nest_index : INT, optional
           THE INDEX OF THIS INSTRUMENT IN THE scan PROCEDURE. 0 CORRESPONDS TO AN INSTRUMENT WHOSE VALUES ARE CHANGED ONLY ONCE, 1 CORRESPONDS
           TO AN INSTRUMENT WHOSE VALUES ARE CHANGED TWICE, ETC. The default is 0.

        Returns
        -------
        None.

        """
        self.motor = apt.Motor(SN_motor)
        self.motor.enable()
        # self.motor.set_velocity_parameters(8,10,10)
        self.meta_data = {'name':name}
        self.scan_values = list(scan_values)
        self.scan_nest_index = scan_nest_index
        self.scan_instrument_name = name
        
    def set_scan_value(self, value):
        self.motor.move_to(value, blocking=True)
        # moving = self.motor.is_in_motion
        # while moving ==True:
        #     moving = self.motor.is_in_motion
        #     time.sleep(0.01)

    def get_scan_value(self):
        return 'degrees', self.motor.position
	
    def get_save_data(self, value):
        return {'angle [degrees]': value}
	
    def close(self):
        pass
#        self.close()
		