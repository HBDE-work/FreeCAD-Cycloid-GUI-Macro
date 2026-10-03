# FreeCAD-Cycloid-Macro

## About

 * Small python macro for FreeCAD which generates a sketch for a disk of a cycloidal drive
 * The parametrization of the curve is taken from https://blogs.solidworks.com/teacher/wp-content/uploads/sites/3/Building-a-Cycloidal-Drive-with-SOLIDWORKS.pdf
 * parameters are read from inside the GUI
 
![alt text](https://raw.githubusercontent.com/HBDE-work/FreeCAD-Cycloid-GUI-Macro/main/cycloid_sketch.png)

## Debugging

When setting the debug flag to *True*, the cycloid is also plotted in matplotlib:

![alt text](https://raw.githubusercontent.com/HBDE-work/FreeCAD-Cycloid-GUI-Macro/main/cycloid_plot.png)

## Usage

 1. copy *cycloid.py* to your FreeCAD macro directory, you can lookup the actual path under the Macro Section in FreeCAD
    * it may be something like this: 
        * **Windows**: `%APPDATA%/FreeCAD/Macro`
        * **Linux**: `$HOME/.local/share/FreeCAD/Macro/`
 2. Open a FreeCAD project and run the macro

---
