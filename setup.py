from setuptools import setup, find_packages

setup(
    name='LightWork',
    version='1.0',
    description='Generalized code to run high-dimensional data scans using optics instrumentation',
    author='Aidan OBeirne, Jenny Hu',
    author_email='aidanobeirne@me.com',
    url='https://github.com/aidanobeirne/LightWork.git',
    packages=find_packages(),
    include_package_data=True,
    # , 'PyQt5', 'pyqtgraph'], #external packages as dependencies
    install_requires=['PyMeasure', 'PyVISA', 'twilio', 'nidaqmx', 'pythonnet', 'thorlabs_apt', 'NewportESP', 'visa', 'file-io']
)
