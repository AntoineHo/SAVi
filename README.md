# SAVi
## Simple Alignment Viewer
Author:  
Antoine Houtain

SAVi is used to visualize alignments from minimap2 .paf files, it comes with a GUI in python for convenience. It reads the .paf file and generates a SQLITE3 database which is then used to create interactive SVGs.

## Dependencies
cmake  
sqlite3  
wxpython

## Installation
```
chmod +x install.sh  
./install.sh
```
## Use
```
cd python  
python SAVi.py
```

### License

Copyright (c) 2018 Antoine Houtain

SAVi is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

SAVi is distributed WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the file LICENSE for more details.

You should have received a copy of the GNU General Public License
along with the source code.  If not, see <http://www.gnu.org/licenses/>.
