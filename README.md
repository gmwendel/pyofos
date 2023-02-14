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

#to get images
images=data.get_all_images()
```



