# Fix script once i hear back from NTT
import sys
sys.path.append(r'/Users/aidan/Desktop/NTT')
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import LightWork.utility.helper_functions as h
from deeplotter.Deeplotter_v02 import Deeplotter
import pickle
# %%
with open(r"deeplotter_example_data.pkl", 'rb') as f:
    data = pickle.load(f)
args = h.generate_deeplotter_input(experiment=data, x_key_list=['x daq', 'voltage'],  y_key_list=[
                                   'y daq', 'voltage'], swap_domain_units=False)
# set deeplotter options
opt = {}
opt['ilabel'] = 'Reflection'
opt['title'] = 'Keithley scan map'
opt['mapequal'] = True
#opt['mapclim'] = (0, 25)
opt['invert_yaxis'] = False
opt['cmap'] = 'viridis'

dp2 = Deeplotter(**args, **opt)


