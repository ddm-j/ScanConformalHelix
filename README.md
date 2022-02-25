# ScanConformalHelix

**Creates a Conformal Helices around a 3D Scan of a Leg
**

**Installation**

1. Best to install the Anaconda Distribution of Python
2. Create a new python 3.6 virtual environment for the project from Anaconda Prompt Command Line: `conda create -n ConformalHelix python=3.6`
3. Activate the new environment: `conda activate ConformalHelix`
4. Move to the directory you want to install the project: `cd <your_directory>`
5. Clone this repository: `git clone <repository_url>`
6. Move into the git repo: `cd ScanConformalHelix`
7. Install the project dependencies: `pip install -r requirements.txt`


**Useage**

1. This is a command line tool. The main file is `conformal_spirals.py` which takes a `meshfile` argument and a `skelfile` argument. The mesh file must be an STL of the 3D scan. The skeleton file is the corresponding medial axis mean flow curvature skeleton of the scan. It has extension .cg
2. Example of execution using the provided files: `python conformal_spirals.py LegTrimmed.stl LegSkeleton.cg`
3. This repo is under development. It has ability to export conformal helix as XYZ files for input to CAD software. But that line of code is not parameterized using command line arguments yet, and must be un-commented for use.
