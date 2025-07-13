## Solar Workbench
Workbench to configure sun position and its path animation

### Worbench Icon
![Solar Workbench Icon](./icons//SolarIcon.svg)

### Features
#### Configure the sun position

* Manually set the sun position with the location data (latitude, longitude, date and time).
* Automatically set the sun position with location data with epw files.
* Enable the display of the sun representation and the direction of illumination to aid in analysis.
* Activate the display of the solar diagram with representation of months, hours, equinoxes and solstices.
* Save images of the results obtained.

#### Visualize the sun path animations

* Ability to Play the sun path animations in real time prior to recording.

#### Record and Play (with Movie and Render Workbenchs)

* Create frames from the FreeCAD 3D view or the rendered ones.   
* Create videos from them.  
* Check the results playing the videos you have created.

### Tutorials

##### Using sun configuration

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

* If you want to use the rendered frames, you must install the Render Workbench, prepare rendering projects and test them preventively to make sure everything is working correctly (see information in [FreeCAD-Render](https://github.com/FreeCAD/FreeCAD-render)). It is also recommended to take advantage and use some cameras from this workbench that better show the animation.
* If you want to use the play and record rendered animation frames, you must install the Movie Workbench [FreeCAD-Movie](https://github.com/Francisco-Rosa/FreeCAD-Movie/tree/master).


### Usage

##### Sun configuration dialog 

The toolbar above is the Movie Cameras and Objects 

<img src=./Docs/Sun_dialog.jpg height=600>

### Documentation
Documentation will be available as soon as possible.

  ### Feedback 
For discussion, please use the [Solar Workbench thread](https://forum.freecadweb.org/) in the FreeCAD forum.

#### License 
LGPL-2.1 [LICENCE](./LICENCE)

#### Author
Francisco Rosa, 2025.
