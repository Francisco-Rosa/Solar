## Solar Workbench
Workbench to manage solar analysis and configurations

### Workbench Icon
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

#### Record and Play (with Movie and Render Workbenches)

* Create frames from the FreeCAD 3D view or the rendered ones.   
* Create videos from them.  
* Check the results playing the videos you have created.

### Tutorials

##### Sun path shadows study

* BW 3D view option

<img src=./Docs/Artigas_house_bw.jpg width=800>

* Color 3D view option

<img src=./Docs/Artigas_house_color.jpg width=800>

* Render 3D view option

<img src=./Docs/Artigas_house_render.jpg width=800>

##### Setting the sun path and its animatation

##### Video with object animation by Sketches

(Watch the [sample video](https://youtu.be/nT1_mGFQwXE?si=TemWHlLiOsnyXDa8))

##### Sky domes analysis

<img src=./Docs/Skydomes_Barcelona_Sao_Paulo_New_York_011.jpg width=800>

<img src=./Docs/Skydomes_Barcelona_Sao_Paulo_New_York_021.jpg width=800>

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

* To use this workbench, you must have the two ladybug Python packages installed (the pysolar package is optional). There are two basic ways to do this:

  If your operating system's Python version is the same as FreeCAD's, simply open a terminal and type:
  
      pip install ladybug-core ladybug-radiance pysolar

  If the versions are different, you'll need to use Python venv. To do this, go to the Solar Workbench folder (see the address above) or open FreeCAD and type the following expression in the Python console to find the Mod that Solar is in:

      import FreeCAD
      import os
      user_mod_path = os.path.join(FreeCAD.getUserAppDataDir(), "Mod")
      print(user_mod_path)

  Create the virtual environment inside the Solar WB folder, to do this, open the terminal system with that path and type:
  
      python3 -m venv AdditionalPythonPackages # for Python 3, or
      python -m venv AdditionalPythonPackages
  
  Activate the virtual environment (you must use AdditionalPythonPackages as the name):
  
      source AdditionalPythonPackages/bin/activate # Linux/macOS
      AdditionalPythonPackages\Scripts\activate # Windows
  
  Install packages within the environment (pysolar is optional):
  
      pip install ladybug-core ladybug-radiance pysolar
      
  Deactivate the virtual environment when finished:
  
      deactivate
      
* To use Sky Domes, you will also need to install Radiance on your computer (https://www.radiance-online.org/).
* Download and license: https://www.radiance-online.org/download-install

* If you want to use the rendered frames, you must install the Render Workbench (via Addon Manager), prepare rendering projects and test them preventively to make sure everything is working correctly (see information in [FreeCAD-Render](https://github.com/FreeCAD/FreeCAD-render)).
* If you want to use the play and record rendered animation frames, you must install the Movie Workbench (via Addon Manager, and see information in [FreeCAD-Movie](https://github.com/Francisco-Rosa/FreeCAD-Movie/tree/master).


### Usage

##### Sun configuration dialog  

<img src=./Docs/Sun_dialog.jpg width=600>

##### Sky domes configuration dialog

<img src=./Docs/SD_dialog.jpg width=600>

To create a SkyDomes, click "Create SkyDomes" button and configure them in the dialog window. To modify a SkyDomes, click "Modify SkyDomes" button with the respective SkyDomes already selected. To delete SkyDomes, select them and click "Delete SkyDomes" button.

Important: Once Skydomes are created, do not modify their structure of the groups in the FreeCAD object tree, as this will prevent future modifications.

### Documentation
Documentation will be available as soon as possible.

  ### Feedback 
For discussion, please use the [Solar Workbench thread](https://forum.freecad.org/viewtopic.php?p=836631#p836631) in the FreeCAD forum.

#### License 
LGPL-2.1 [LICENSE](./LICENSE)

#### Author
Francisco Rosa, 2025.
