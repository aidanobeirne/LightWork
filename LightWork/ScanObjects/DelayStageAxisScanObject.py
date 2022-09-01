import newportESP as newportESP


class DelayStageScanObject(newportESP.Axis):
    def __init__(self, scan_values, esp_controller, axis, home=False, name='delay_stage_axis_1', scan_nest_index=0):
        super().__init__(esp_controller, axis)
        self.scan_values = list(scan_values)
        self.scan_nest_index = scan_nest_index
        self.scan_instrument_name = name
        self.axis = axis
        self.esp_controller = esp_controller
        self.on()
        if home:
            self.home_search()
        self.meta_data = {}
        
    def set_scan_value(self, value):
        self.move_to(value, wait=True)

    def get_scan_value(self):
        return 'position_mm [nm]', self.position
	
    def get_save_data(self, value):
        data = {'position_mm [nm]': self.position}
        return data
	
    def close(self):
        pass

		
		