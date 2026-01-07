
# Installation

How to install and setup the Solar addon.

<br/>

## 1. Addon

Install this addon via the addon manager.

<br/>

## 2. Radiance

To use the Sky Domes functionality, you also  
need to install the **[Radiance]** project which  
currently has to be done using their installers.

Head over to their **[Releases]** page, download  
the installer for your system and go through it.

### Windows and macOS

Use the corresponding installers.

### Linux

Since the Linux version does not have an installer, 
it must be done manually.

Unzip the "Radiance_xx_Linux.zip" file, then the 
.tar.gz file. Go to the "radiance" folder inside the
"radiance-xxx-Linux" (radiance-xxx-Linux/user/local/radiance).

Run FreeCAD and open the Solar Workbench so that 
the ladybug libraries are executed. This will 
create a folder called "ladybug_tools",
this is where the radiance should be placed. 
But, its location may vary, to find its path, 
run the following commands 
in the FreeCAD Python console:

```Python
from ladybug.config import folders
print(f'{ folders.ladybug_tools_folder }')
```
Insert the radiance folder into the path indicated by the mentioned commands. Restart FreeCAD to use the new features.

Obs.: If you are using different FreeCAD packages (especially Snaps), 
the procedure must be performed for each one.
<br/>

## 3. Integrations

If you want to use the integrations into the  
`Render` & `Movie` addons, simply install  
those via the addon manager.


[FlatSeal]: https://flathub.org/en/apps/com.github.tchx84.Flatseal
[Releases]: https://github.com/LBNL-ETA/Radiance/releases
[Radiance]: https://www.radiance-online.org/
