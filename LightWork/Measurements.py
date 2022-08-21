import os
import numpy as np
import pickle
from itertools import product
import time
import copy
import matplotlib.pyplot as plt
from datetime import date
from twilio.rest import Client


class SimpleScan:
    def __init__(self, measurement_instrument, scan_instruments, save_at_every_step=True, laser_shutter=False, laser_shutter_SN='37005097',
                 savepath=os.getcwd(), savename='data', scan_notes='', save_npz=True,
                 notify_me=False, ACCOUNT_SID='', AUTH_TOKEN='', twilio_to="+12059021472", twilio_from="+16827100017"):
        """
        Parameters
        ----------
        measurement_instrument : MeasurementObject (currently the only options are AndorMeasurementObject or SR830MeasurementObject)
            THE INSTRUMENT YOU WISH TO ACQUIRE DATA WITH -- USUALLY A CAMERA IN A SPECTROMETER.
        scan_instruments : List of ScanObjects
            A LIST OF INSTRUMENTS WHOSE ATTRIBUTES YOU WISH TO SCAN ACROSS, E.G. KEITHLEY2400.
        save_at_every_step : BOOL, optional
            DO YOU WANT TO SAVE A SINGLE MEASUREMENT AT EVERY SCAN STEP? (USEFUL WHEN SCAN INSTRUMENTS ARE UNRELIABLE OR IF YOU ARE DEBUGGING). The default is True.
        laser_shutter : BOOL, optional
            TRUE IF LASER SHUTTER IS CONNECTED, FALSE IF NOT CONNECTED. The default is False.
        savepath : STR, optional
            PATH TO SAVE DATA TO. The default is os.getcwd().
        savename : STR, optional
            BASENAME OF SAVED DATA FILE. The default is 'data'.
        scan_notes: STR, optional
            ADDITIONAL NOTES THAT THE USER WOULD LIKE TO RECORD. The default is ''.
        save_npz : BOOL, optional
            TRUE TO SAVE DATA AS NPZ, FALSE TO PICKLE. The default is True.
        notify_me : BOOL, optional
            TRUE TO SEND A TEXT MESSAGE WHEN THE SCAN IS COMPLETE. The default is False.
        ACCOUNT_SID : STR, optional
            TWILIO ACCOUNT SID. The default is ''.
        AUTH_TOKEN : STR, optional
            TWILIO ACCOUNT TOKEN. The default is ''.
        twilio_to : STR, optional
            PHONE NUMBER TO SEND MESSAGE TO. The default is "+12059021472".
        twilio_from : STR, optional
           PHONE NUMBER TO SEND MESSAGE FROM. The default is "+16827100017".

        Returns
        -------
        None.

        """
        self.measurement_instrument = measurement_instrument
        self.save_at_every_step = save_at_every_step
        self.meta_data = {'scan notes': scan_notes}
        self.save_npz = save_npz
        self.scan_instruments = scan_instruments
        self.scan_instrument_names = [
            inst.scan_instrument_name for inst in self.scan_instruments]
        self.savefile = os.path.join(savepath, savename)
        self.notify_me = notify_me
        self.twilio_to = twilio_to
        self.twilio_from = twilio_from
        self.AUTH_TOKEN = AUTH_TOKEN
        self.ACCOUNT_SID = ACCOUNT_SID
        if not os.path.exists(savepath):
            os.makedirs(savepath)
        if laser_shutter:
            from LightWork.ParentClasses.ThorlabsStages.ThorlabsStages import LaserShutter
            self.shutter = LaserShutter(laser_shutter_SN)
        self.generate_scan_list()

    def generate_scan_list(self):
        """
        This function generates a scan_list attribute which is a list of lists containing the scan values at every scan iteration.
        """
        scan_nest_indices = [
            inst.scan_nest_index for inst in self.scan_instruments]
        # list of sublists where each sublist will eventually be a complete set of scan instrument step values
        self.scan_values = []

        new_instrument_order = []
        for idx in set(np.array(scan_nest_indices) - np.min(scan_nest_indices)):
            instruments_with_same_idx = [
                inst for inst in self.scan_instruments if inst.scan_nest_index == idx]
            for i in instruments_with_same_idx:
                new_instrument_order.append(self.scan_instruments.index(i))
            scan_arrays_to_be_zipped = [
                instrument.scan_values for instrument in instruments_with_same_idx]
            if not all(len(l) == len(scan_arrays_to_be_zipped[0]) for l in scan_arrays_to_be_zipped):
                #                self.close()
                raise ValueError('not all lists in scan nest index = {} have same length, you silly goose!'.format(
                    idx + min(scan_nest_indices)))
            # list(zip(*scan_arrays_to_be_zipped))
            merged_list_to_add = list(
                map(list, zip(*scan_arrays_to_be_zipped)))
            if idx == 0:
                self.scan_values.extend(merged_list_to_add)
            else:
                temp_scan_list = []
                for v1, v2 in product(self.scan_values, merged_list_to_add):
                    new_sublist = []
                    new_sublist.extend(v1)
                    new_sublist.extend(v2)
                    temp_scan_list.append(new_sublist)
                self.scan_values = temp_scan_list

        self.scan_instruments = [self.scan_instruments[i]
                                 for i in new_instrument_order]

    def run_scan(self):
        """
        Runs the scan as defined by the instance of the SimpleScan.
        """
        self.master_data = {}
        # open shutter
        try:
            self.shutter.flipperOn()
        except AttributeError:
            pass

        start_time = time.time()
        print('Scan started')
        for count, values in enumerate(self.scan_values):
            # Generate a unique identifier for the scan step
            # unique_ID = '--'.join(['{}={}'.format(i,j) for i,j in zip(self.scan_instrument_names, values)])
            unique_ID = count
            self.master_data[unique_ID] = {}
            # time calculation
            if count % 5 == 0 and count > 0:
                time_so_far = time.time() - start_time
                percent_complete = count/len(self.scan_values)
                total_time_estimate = time_so_far/percent_complete
                time_remaining = (total_time_estimate-time_so_far)/3600
                print('estimated {} hours and {} minutes remaining'.format(
                    int(np.floor(time_remaining)), int(np.rint(60*(time_remaining % 1)))))
                # print('\r estimated {} hours and {} minutes remaining'.format(int(np.floor(time_remaining)), int(np.rint(60*(time_remaining % 1)))), end='\r', flush=True)
            # set scan values for every scan instrument
            for inst, value in zip(self.scan_instruments, values):
                inst.set_scan_value(value)
                try:
                    self.master_data[unique_ID]['{}'.format(
                        inst.scan_instrument_name)] = inst.get_save_data(value)
                except TypeError:
                    pass

            # acquire data
            data = self.measurement_instrument.measure()

            # Save the data at every step if desired
            if self.save_at_every_step:
                self.save_data_npz(values, data, unique_ID) if self.save_npz else self.save_data_pkl(
                    values, data, unique_ID)

            # Add to the master_data dictionary
            self.master_data[unique_ID]['data'] = data

        scan_time = np.round((time.time()-start_time)/3600, 2)
        print()
        print('Scan took {} hours and {} minutes'.format(
            int(np.floor(scan_time)), int(np.rint(60*(scan_time % 1)))))
        self.meta_data['Scan time'] = '{} hours and {} minutes'.format(
            int(np.floor(scan_time)), int(np.rint(60*(scan_time % 1))))
        self.final_save(self.master_data)

        # close shutter
        try:
            self.shutter.flipperOff()
            self.shutter.close()
        except AttributeError:
            pass

        if self.notify_me:
            client = Client(self.AUTH_TOKEN, self.ACCOUNT_SID)
            client.messages.create(
                to=self.twilio_to,
                from_=self.twilio_from,
                body='Scan took {} hours and {} minutes'.format(
                    int(np.floor(self.scan_time)), int(np.rint(60*(self.scan_time % 1))))
            )

    def save_data_npz(self, scan_values, data, unique_ID):
        """
        This function currently does not save meta data because the npz cannot be a nested dictionary, so unpacking the meta_data dict requires some careful thinking.
        Parameters
        ----------
        scan_values : LIST
            The list of scan values for each instrument at a particular step in the scan (e.g. [1.2, 3, 5] for inst1, inst2, inst3)
        data : LIST or ARRAY
            The data from a single measurement
        unique_ID : STR
            The uniquie identifier string used to save the data

        Returns
        -------
        None.

        """
        saveto = self.savefile + str(unique_ID) + '.npz'
        np.savez(saveto, data=data)

    def save_data_pkl(self, scan_values, data, unique_ID):
        """
        Parameters
        ----------
        scan_values : LIST
            The list of scan values for each instrument at a particular step in the scan (e.g. [1.2, 3, 5] for inst1, inst2, inst3)
        data : LIST or ARRAY
            The data from a single measurement
        unique_ID : STR
            The uniquie identifier string used to save the data

        Returns
        -------
        None.

        """
        save_data = {}
        save_data['data'] = data
        meta_data = copy.deepcopy(self.meta_data)
        for instrument, value in zip(self.scan_instruments, scan_values):
            #            try:
            #                save_data['{}'.format(instrument.scan_instrument_name)] = instrument.get_save_data(value)
            #            except TypeError:
            #                pass
            try:
                meta_data['{}'.format(
                    instrument.scan_instrument_name)] = instrument.meta_data
            except TypeError:
                pass
        meta_data['{}'.format(self.measurement_instrument.scan_instrument_name)
                  ] = self.measurement_instrument.meta_data
        save_data['meta_data'] = meta_data
        saveto = '{}_{}.pkl'.format(self.savefile, unique_ID)
        with open(saveto, "wb") as f:
            pickle.dump(save_data, f)

    def final_save(self, data):
        """
        Used to save the dictionary that contains all of the data at the end of the run_scan() method

        Parameters
        ----------
        data : DICTIONARY
            The master_data dictionary that is constructed in the run_scan() method.

        Returns
        -------
        None.

        """
        save_data = {}
        save_data['master_data'] = data
        meta_data = copy.deepcopy(self.meta_data)
        for instrument in self.scan_instruments:
            try:
                meta_data['{}'.format(
                    instrument.scan_instrument_name)] = instrument.meta_data
            except TypeError:
                pass
        meta_data['{}'.format(self.measurement_instrument.scan_instrument_name)
                  ] = self.measurement_instrument.meta_data
        save_data['meta_data'] = meta_data
        saveto = self.savefile + '.pkl'
        with open(saveto, "wb") as f:
            pickle.dump(save_data, f)

    def close(self):
        for instrument in self.scan_instruments:
            instrument.close()

        self.measurement_instrument.close()


class SingleSpec:
    def __init__(self, measurement_instrument, scan_instruments=None, ref=None, dark=None, laser_shutter=False, laser_shutter_SN='37005097',
                 savepath=os.getcwd(), savename='data', scan_notes=''):
        """ Class used to acquire a single spectrum

        Args:
            measurement_instrument : MeasurementObject 
            scan_instruments : List of ScanObjects
            ref (array, optional): reference spectrum. Defaults to None.
            dark (array, optional): dark spectrum. Defaults to None.
            laser_shutter (bool, optional): whether or not to use thorlabs laser shutter. Defaults to False.
            laser_shutter_SN (str, optional): laser shutter serial number. Defaults to '37005097'.
            savepath (str, optional): directory to save. Defaults to os.getcwd().
            savename (str, optional): filename. Defaults to 'data'.
            scan_notes (str, optional): any notes that you have. Defaults to ''.
        """
        self.measurement_instrument = measurement_instrument
        self.scan_instruments = scan_instruments
        self.meta_data = {'scan notes': scan_notes}
        if scan_instruments is not None:
            self.scan_instrument_names = [
                inst.scan_instrument_name for inst in self.scan_instruments]
        self.savefile = os.path.join(savepath, savename)
        if not os.path.exists(savepath):
            os.makedirs(savepath)
        if laser_shutter:
            from LightWork.ParentClasses.ThorlabsStages.ThorlabsStages import LaserShutter
            self.shutter = LaserShutter(laser_shutter_SN)
        self.acquire(ref=ref, dark=dark)
        self.final_save(self.master_data)

    def acquire(self, ref=None, dark=None):
        """ Used to save a single spectrum 

        Args:
            ref (array or list, optional): reference spectrum in case this is a reflection contrast measurement. Defaults to None.
            dark (array or list, optional): dark spectrum that can be subtracted. Defaults to None.
        """
        self.master_data = {}
        try:
            for inst in self.scan_instruments:
                try:
                    self.master_data['{}'.format(
                        inst.scan_instrument_name)] = inst.get_save_data(inst.get_scan_value())
                except TypeError:
                    pass
        except TypeError:
            pass
        # acquire data
            data = self.measurement_instrument.measure()
        # apply background subtraction etc
            if dark is not None and ref is not None:
                data['spec dark subtracted'] = data['spec'] - np.array(dark)
                data['reflection contrast'] = (
                    data['spec dark subtracted'] - np.array(ref)) / (np.array(ref) - np.array(dark))
            elif dark is not None and ref is None:
                data['spec dark subtracted'] = data['spec'] - np.array(dark)
            elif dark is None and ref is not None:
                data['reflection contrast'] = (
                    data['spec'] - np.array(ref)) / np.array(ref)
        # Add to the master_data dictionary
        self.master_data['data'] = data

    def final_save(self, data):
        """
        Used to save the dictionary that contains all of the data at the end of the acquire() method

        Parameters
        ----------
        data : DICTIONARY
            The master_data dictionary that is constructed in the run_scan() method.

        Returns
        -------
        None.

        """
        save_data = {}
        save_data['master_data'] = data
        meta_data = copy.deepcopy(self.meta_data)

        try:
            for inst in self.scan_instruments:
                try:
                    meta_data['{}'.format(
                        inst.scan_instrument_name)] = inst.meta_data
                except TypeError:
                    pass
        except TypeError:
            pass

        meta_data['{}'.format(self.measurement_instrument.scan_instrument_name)
                  ] = self.measurement_instrument.meta_data
        save_data['meta_data'] = meta_data
        saveto = self.savefile + '.pkl'
        with open(saveto, "wb") as f:
            pickle.dump(save_data, f)


class RTC:
    def __init__(self, measurement_instrument, ref=None, dark=None, swap_domain_units=False):
        # get domain
        energies = np.array(measurement_instrument.measure()['wavelengths'])
        if swap_domain_units:
            energies = 1240/energies
        plt.ion()
        fig = plt.figure(figsize=(20, 10))
        ax = fig.add_subplot(111)
        line1, = ax.plot(energies, np.ones_like(energies))

        capture = True
        while capture:
            spec = np.array(measurement_instrument.measure()['spec'])
            # apply background subtraction etc
            if dark is not None and ref is not None:
                ref = np.array(ref)
                dark = np.array(dark)
                spec = (spec - ref) / (ref - dark)
            elif dark is not None and ref is None:
                dark = np.array(dark)
                spec = spec - dark
            elif dark is None and ref is not None:
                ref = np.array(ref)
                spec = (spec - ref) / ref
            line1.set_ydata(spec)
            ax.set_ylim(bottom=min(spec), top=max(spec))
            fig.canvas.draw()
            fig.canvas.flush_events()
            time.sleep(0.02)
