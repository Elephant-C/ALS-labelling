# Labelling forest airborne laser scanning point clouds with terrestrial Laser Scanning reference
 [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) [![PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)
 
## Project Overview ##
The repository is developed by [Yujie Cao](https://github.com/Elephant-C), in close collaborations with [Tobias. D Jackson](https://github.com/TobyDJackson), [James G.C. Ball](https://github.com/PatBall1), during his visiting at Forest Conservation Group led by professor [David A. Coomes](https://scholar.google.com/citations?user=CXkjEhIAAAAJ&hl=en&oi=ao). The group is part of the University of Cambridge [Conservation Research Institute](https://www.conservation.cam.ac.uk/).

This repository is used to create two robust international ALS benchmark data sets: Wythams Woods (temperate broadleaves) in the UK and Sepilok Forest (tropical rainforest) in the Sabah, Malaysia. The two benchmarks serve as the data source for inter-comparison for airborne LiDAR individual tree segmentation algorithms (project repository: [2D Tree crown polygon-based assessment for airborne LiDAR-based individual tree segmentation methods
](https://github.com/Elephant-C/tree-crown-based-assessment)). For more information about the whole work, please refer to my paper: *__Tree segmentation in airborne laser scanning
data is only accurate for canopy trees.__* 

__If you use this code in your work, please cite the following paper in a proper way:__

*Yujie Cao, James G C Ball, David A. Coomes, Leon Steinmeier, Nikolai Knapp, Phil Wilkes, Kim Calders, Andrew Burt, Mathias Disney, Yi Lin, and Tobias D. Jackson. Tree segmentation in airborne laser scanning
data is only accurate for canopy trees.*(*__Pre-print DOI__* :https://doi.org/10.1101/2022.11.29.518407).

## Why this work? ##


## Requirements ##
+ Python $\geqslant$ 3.7.12
+ [Open3d](http://www.open3d.org/) $\geqslant$ 0.15.1. Note 0.16.0 would lead to menmory leak issue like zsh: segmentation fault.
+ [Laspy](https://laspy.readthedocs.io/en/latest/index.html)
+ Numpy
+ Pandas
+ tqdm
+ pickle


## Project Organization ##
```
├── Figures                            <- Figures used in reporting.
├── src                      
|   ├── preprocess.py                  <- Find the rough range for further airborne lidar point clouds labelling.
|   ├── color_mapping.py               <- Create mapping for random RGBs and IDs.
|   ├── ALS_Labelling.py               <- Label airborne lidar point clouds with referenced terrestrial point clouds.
|   ├── Post-process.py                <- Conduct core area fitting, cropping and terrain normalization
├── README.md               
├── LICENSE
└── requirements.txt
```

## Workflow ##
<p align="center">
<img width="500" align="center" alt="predictions" src=./Figures/labelling_workflow.png>
</p>
Our labelling strategy 

+ Automatic ALS-TLS point clouds registraion (In Development)

Automatic ALS-TLS point clouds registration method is in development and will soon be updated to this repository. Our current results were achieved by manually aligning ALS and TLS data (Refer to our paper for more information).

+ Confidence Score Rating System

The rating system was used to assess the data quality for individual tree point clouds from labelled ALS benchmark.

| Confidence Score      | Confidence Score |
| :----:   |    :----:   |
| 7    |Enough ALS point clouds to fit tree crown polygon, and the individual tree feature representation is accurate|
| 6    |Enough ALS point clouds to fit tree crown polygon, and the bias for individual tree feature representation is small|
| 5    |Enough ALS point cloud to fit tree crown polygons, but the bias for individual tree feature representation is larger|
| 4    |Enough ALS point clouds to fit tree crown polygons, but the number of points are not enough to represent a tree|
| 3    |ALS data is available, but too few point clouds (less 3 points) to form tree crown polygons|
| 2    |No ALS data available|
| 1    |Tree has fallen down|

## Result Visualization (Take Wytham Woods as example) ##

__The whole plot__
<p align="center">
<img src=./Figures/wytham.gif width="200" align="center">
</p>

__Individual tree visualization__

+ Confidence Score = 7
<p align="center">
<img width="500" align="center" alt="predictions" src=./Figures/wytham_confidence_score_1.png>
</p>

+ Confidence Score = 6
<p align="center">
<img width="500" align="center" alt="predictions" src=./Figures/wytham_confidence_score_2.png>
</p>

+ Confidence Score = 5
<p align="center">
<img width="500" align="center" alt="predictions" src=./Figures/wytham_confidence_score_3.png>
</p>

+ Confidence Score = 4
<p align="center">
<img width="500" align="center" alt="predictions" src=./Figures/wytham_confidence_score_4.png>
</p>

+ Confidecne Score = 3
<p align="center">
<img width="500" align="center" alt="predictions" src=./Figures/wytham_confidence_score_5.png>
</p>

+ Confidence Score = 2
<p align="center">
<img width="500" align="center" alt="predictions" src=./Figures/wytham_confidence_score_6.png>
</p>

+ Confidence Score = 1

No Fallen tree was found in Wytham Woods case

## USPS ##
Automatic ALS-TLS point cloud data registration method will soon be updated to the repository.

## Other ##
Please refer to our paper mentioned above for detailed information about the method and ALS benchmark.
