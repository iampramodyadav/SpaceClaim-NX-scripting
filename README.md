# spcaceclaim-nx-scripts
Spaceclaim and NX automation scripts

## Overview

This Python script automates the extraction of midsurfaces from solid bodies within an Ansys SpaceClaim design. It offers two extraction methods:

 * By Body: Extracts a midsurface from each solid body based on a specified thickness range (inclusive).
 * By Surface: Creates a midsurface by selecting two opposing largest faces from a single solid body.
The script also renames extracted midsurfaces based on a pattern derived from the component name.
Usage
 * Modify the min_thickness and max_thickness variables according to your desired thickness range (in mm).
 * Set methode_by_body to True to use the "By Body" method, or False to use the "By Surface" method.
 * Run the script.
Note:
 * This script requires the clr and System.Windows.Forms libraries to be imported.
 * The script uses the Midsurface and MidsurfaceOptions

 classes from the Ansys SpaceClaim API.
'''py
Example
min_thickness = 2
max_thickness = 5
methode_by_body = True

main()
'''

This example will extract midsurfaces from all solid bodies in the Ansys SpaceClaim design with a thickness between 2 and 5 mm using the "By Body" method. The extracted midsurfaces will be renamed based on the component name.
