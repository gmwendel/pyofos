# *pyofos*

Tools used to extract data from simulation of ofos


## Installation

```
git clone https://github.com/gmwendel/pyofos.git
cd pyofos
pip install -e .
```

## Usage

```
from pyofos.roottools import DataExtractor

data=DataExtractor("path/to/file.root")
#to get truth data
mc_truth=data.get_truth_data()

#to get flattened hit data
flat_hits=data.get_obs_data()

#to get images of a 10x10 grid
images=data.get_all_images(side_number=10)
```

## Testing
includes a unit test which plots the distribution of truth data, hit data, and the first image of the file
```commandline
python3 pyofos/unittest.py /path/to/file.root
```
