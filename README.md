## Solar Workbench
Workbench for configuring the sun's position and animating its path

### Worbench Icon
![Solar Workbench Icon](./icons//SolarIcon.svg)

### Features
#### Configure the sun position

* Manually set the sun position with the location data (latitude, longitude, date and time).
* Automatically set the sun position with location data from epw file.
* Enable the display of the sun representation and the direction of illumination to aid in analysis.
* Activate the display of the solar diagram with representation of months, hours, equinoxes and solstices.
* Save images of the results obtained.

#### Visualize the sun path animations

* Ability to play the sun path animations in real time prior to recording.

#### Record and Play (with Movie and Render Workbenchs)

* Create frames from the FreeCAD 3D view or the rendered ones.   
* Create videos from them.  
* Check the results playing the videos you have created.

### Tutorials

##### Using sun configuration

<img src=./Docs/Artigas_house_bw.jpg height=300>

<img src=./Docs/Artigas_house_color.jpg height=300>

<img src=./Docs/Artigas_house_render.jpg height=300>

##### Setting the sun path and its animatation

##### Video with object animation by Sketches

(Watch the [sample video](https://youtu.be/nT1_mGFQwXE?si=TemWHlLiOsnyXDa8))


### Prerequisites 
FreeCAD ≥ v1.0 

### Installation

##### Via Addon Manager (Recommended)

Not yet available.

##### Manually install using GitHub

<details><summary>Expand to read manual installation instructions</summary>

- Download the ZIP file (click 'Clone or Download' button above) 
- For Ubuntu and similar OS's, extract it inside */home/username/.local/share/FreeCAD/Mod*   
- For Windows, extract it inside *C: \Users\your_user_name\AppData\Roaming\FreeCAD\Mod*
- On macOS it is usually */Users/username/Library/Preferences/FreeCAD/Mod*
- Launch FreeCAD

</details>

### Preparation

* To use this workbench, you must have the ladybug-core Python package installed. There are two basic ways to do this:

  If your operating system's Python version is the same as FreeCAD's, simply open a terminal and type:
  
      pip install ladybug-core pysolar # pysolar is optional

  If the versions are different, you will need to use Python venv. To do this, go to the Solar workbench folder (see the address above, or open FreeCAD and type in the Python console:

      import FreeCAD
      import os
      user_mod_path = os.path.join(FreeCAD.getUserAppDataDir(), "Solar")
      print(user_mod_path)

  Create the virtual environment using:
  
      python3 -m venv AdditionalPythonPackages # for Python 3, or
      python -m venv AdditionalPythonPackages
  
  Activate the virtual environment (you must use AdditionalPythonPackages as the name):
  
      source AdditionalPythonPackages/bin/activate # Linux/macOS
      AdditionalPythonPackages\Scripts\activate # Windows
  
  Install packages within the environment:
  
      pip install ladybug-core pysolar # pysolar is optional
  Deactivate the virtual environment when finished:
  
      deactivate

* If you want to use the rendered frames, you must install the Render Workbench, prepare rendering projects and test them preventively to make sure everything is working correctly (see information in [FreeCAD-Render](https://github.com/FreeCAD/FreeCAD-render)).
* If you want to use the play and record rendered animation frames, you must install the Movie Workbench [FreeCAD-Movie](https://github.com/Francisco-Rosa/FreeCAD-Movie/tree/master).


### Usage

##### Sun configuration dialog  

<img src=./Docs/Sun_dialog.jpg height=600>

### Documentation
Documentation will be available as soon as possible.

  ### Feedback 
For discussion, please use the [Solar Workbench thread](https://forum.freecadweb.org/) in the FreeCAD forum.

#### License 
LGPL-2.1 [LICENCE](./LICENCE)

#### Author
Francisco Rosa, 2025.
