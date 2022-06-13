from setuptools import setup

setup(
   name='SimpleScan',
   version='1.0',
   description='Generalized code to run high-dimensional data scans using optics instrumentation',
   author='Aidan OBeirne',
   author_email='aidanobeirne@me.com',
   url='https://github.com/aidanobeirne/SimpleScan.git',
   packages=['SimpleScan'],  #same as name
   install_requires=['PyMeasure', 'socket', 'PyVISA', 'signal'], #external packages as dependencies
   include_package_data=True,
   scripts=[
            'scripts/cool',
            'scripts/skype',
           ]
)