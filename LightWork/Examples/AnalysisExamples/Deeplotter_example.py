

# Fix script once i hear back from NTT
import LightWork.utility.helper_functions as h
from utility.deeplotter.Deeplotter_v02 import Deeplotter
import pickle

# %%
h.add_ref_or_dark_to_measurement(
    r"G:\My Drive\BP\Samples\Box 2\Sample LO\data\2022-08-19\LO_RC_1L_matrix.pkl")
# %%
with open(r"G:\My Drive\BP\Samples\Box 2\Sample LO\data\2022-08-19\LO_RC_1L_matrix.pkl", 'rb') as f:
    data = pickle.load(f)
args = h.generate_deeplotter_input(measurement=data, x_key_list=['keithley_TG', 'voltage [V]'],  y_key_list=[
                                   'keithley_BG', 'voltage [V]'], swap_domain_units=False)
# %% Plot in Deeplotter
# set deeplotter options
opt = {}
# opt['xlabel'] = '{} [{}]'.format(x.name, 'x')
# opt['ylabel'] = '{} [{}]'.format(y.name, 'y')
# opt['zlabel'] = '{} [{}]'.format(veclambda.name, 'px')
opt['ilabel'] = 'Reflection'
opt['title'] = 'Keithley scan map'
opt['mapequal'] = True
#opt['mapclim'] = (0, 25)
opt['invert_yaxis'] = False
# opt['arrow_xrange'] = [1392.688, 1392.688]
# opt['arrow_yrange'] = [ 33.0, 114.16591928]
opt['cmap'] = 'viridis'
# opt['mapclim'] = [0.7, 1]

# create Deeplotter object
# dp = Deeplotter(x=Vbg, y=Vtg, z=veclambda, data=data/data[0,0,:], **opt) # /data[0,-1,:]
# dp2 = Deeplotter(x=xvalues, y=yvalues, z=energies, data=data, **opt)
dp2 = Deeplotter(**args, **opt)

# # set some options and then redraw (can be done within an interactive session)
# dp.draw_all(
#     # fwindow = [750, 752],
#     logscale = 1,
#     mapequal = 0,
# )
# # put focus on arrow such that we can nagivate with left/right
# dp._mk_active = dp._mk_arrow
# dp.draw_map(markers=True)
