# msfs_sctc
Throttle configurer for Flight Simulators using SimConnect

Allows manual configuration of throttle axes for any flight simulator that supports SimConnect.  
Primarily meant for MSFS.

Pre-pre-alpha. I take no responsibility if stuff breaks, but it really shouldn't be able to break anything.  
If someone knows a better and simpler way to get joystick data than using Pygame, please let me know.

## Note: Ingame throttle axis should be unbound to avoid conflict. I recommend making a new controls profile for this.

# Known issues:
- Reverser on same axis does not work.

# To run:
Right now you need Python 3, as well as the Python packages mentioned in `requirements.txt`.
After installing Python 3, installing the packages should be as simple as opening a terminal/CMD window in the same folder as the project and running:  
`pip install -r requirements.txt` or `pip3 install -r requirements.txt`  
After this, you can either run the program by double clicking `throttle_ctrl.py`, or by opening a terminal/CMD window in the same folder and running:  
`python throttle_ctrl.py` or `python3 throttle_ctrl.py`
