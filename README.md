# sr860-python

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/SQLim/sr860-python/blob/main/LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/SQLim/sr860-python.svg?style=social&label=Star&maxAge=3600)](https://github.com/SQLim/sr860-python)


## Abstract

**sr860-python** is a pure Python package to facilitate the use of [Stanford Research Systems](https://thinksrs.com) [SR860 DSP lock-in amplifier](https://thinksrs.com/products/sr860.html) instrument.

**sr860-python** requires Python 3.

**sr860-python** communicates with the instrument using the VISA API interface (pyVISA package). 

**sr860-python** is MIT licensed.


## Installation

### Using `pip`:
```text
python -m pip install git+https://github.com/SQLim/sr860-python.git
```

### Using `setup.py`:
```text
git clone https://github.com/SQLim/sr860-python.git
cd sr860-python/
python setup.py install
```


## Example

```python
from srs import SR860

lia = SR860('USB0::0xB506::0x2000::003921::INSTR') # Windows USB 
lia.init()

# Set modulation frequency and amplitude
lia.frequency = 173.31   # float [Hz]
lia.amplitude = 1.0      # float [Vrms]

# Enable sync filter
lia.sync_filter_enable = True

# Set sensitivity
lia.sensitivity = 500e-6 # float [Vrms]

# Get filter time constant
lia.time_constant        # returns float [e.g., 0.1] [s]

# Auto phase function
lia.auto_phase()

# Read X channel
lia.X_output()

# Read XYRP channels simultaneously
lia.XYRP_outputs()

# Check if advance filter is enabled
lia.adv_filter_enable     # returns bool [e.g., False]
```


## License
sr860-python is covered under the MIT license.
