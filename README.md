# SAVi
## Simple Alignment Viewer

SAVi is used to visualize alignments formatted in .paf files, it comes with a GUI in python. It reads the .paf file and generates interactive SVGs given a target name.

## Dependencies
```
cefpython3
pandas
numpy
```

## Installation (using conda)
```
conda create -n savi python=3.7 pandas numpy pip
conda activate savi
pip install cefpython3=66.0
```
## Use
```
python /path/to/SAVi_v02.py
```

GUI usage steps:
1. Open a .paf file
2. Click on the read button
3. Write the name of the target to draw
4. Click the draw button
5. Save the output in .html or .svg

The image below shows an example of the GUI after a .paf file has been loaded
![alt text](savi_loaded.png "Example GUI")

### License

Copyright (c) 2018 Antoine Houtain

SAVi is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

SAVi is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the file LICENSE for more details.

You should have received a copy of the GNU General Public License
along with the source code.  If not, see <http://www.gnu.org/licenses/>.
