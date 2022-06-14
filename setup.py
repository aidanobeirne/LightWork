from setuptools import setup, find_packages

setup(
   name='LightWork',
   version='1.0',
   description='Generalized code to run high-dimensional data scans using optics instrumentation',
   author='Aidan OBeirne',
   author_email='aidanobeirne@me.com',
   url='https://github.com/aidanobeirne/LightWork.git',
   packages=find_packages(),  #same as name
   include_package_data=True,
   package_data={'dlls': ['ParentClasses/Andor/*.dll'], 'examples' : ['ExperimentExamples/*.py']},
   install_requires=['PyMeasure', 'PyVISA'], #external packages as dependencies
)