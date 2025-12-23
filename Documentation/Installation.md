
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

### Flatpak

If you are using the Flatpak version of FreeCAD  
you have to also give it access to the Radiance  
files, the easiest way is to use **[Flatseal]**.

In Flatseal find the FreeCAD entry and scroll to  
the section named `Filesystem`, there you can  
give FreeCAD access to additional directories.

Add a directory called `/usr/local/radiance`

<img width = '300' src = '../Resources/Media/Installation/Flatpak-FileSystem.webp' />

### Snap

Similar to Flatpak, Snaps don't have access to  
files outside by default, however I couldn't find  
a proper way to change this.

Let us know if you know how to configure it!

<br/>

## 3. Integrations

If you want to use the integrations into the  
`Render` & `Movie` addons, simply install  
those via the addon manager.


[FlatSeal]: https://flathub.org/en/apps/com.github.tchx84.Flatseal
[Releases]: https://github.com/LBNL-ETA/Radiance/releases
[Radiance]: https://www.radiance-online.org/