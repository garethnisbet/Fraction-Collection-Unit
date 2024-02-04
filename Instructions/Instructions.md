## Instructions For Fraction Collection Unit

1. Build the Creality Ender 5 S1 3D Printer according to the supplied instructions.

![Creality Ender 5 S1](https://github.com/garethnisbet/Fraction-Collection-Unit/blob/main/Instructions/CREALITY_Ender_5_S1.svg)


2. Download the [CAD Files](../CAD).
3. Download [Cura](https://ultimaker.com/software/ultimaker-cura/) to slice the stl files and generate the G-code for printing.


![Printable Parts List](https://github.com/garethnisbet/Fraction-Collection-Unit/blob/main/Instructions/PrintObjects.svg)

💡 **Note:** Once printing is complete, the print head is going to be removed from the printer so you might want to print a few spare sets before taking this step.

Assemble the Capillary Bracket.

![Capillary Bracket Assembly](https://github.com/garethnisbet/Fraction-Collection-Unit/blob/main/Instructions/Assembly_P1.svg)

Remove the print head hotplate and wiring (everything unplugs so no cutting is required).

![Remove print head and hotplate](https://github.com/garethnisbet/Fraction-Collection-Unit/blob/main/Instructions/Assembly_P2.svg)

Bolt the capillary bracket to print head plate.

![Bolt the capillary bracket to prin thead plate](https://github.com/garethnisbet/Fraction-Collection-Unit/blob/main/Instructions/Assembly_P3.svg)

Bolt the base plate to the build platform.

![Bolt the capillary bracket to prin thead plate](https://github.com/garethnisbet/Fraction-Collection-Unit/blob/main/Instructions/Assembly_P4.svg)

---
[Install Software](../Python/) - Copy python files into a folder on the Raspberry Pi and run GUI.py.

![Screen 1](https://github.com/garethnisbet/Fraction-Collection-Unit/blob/main/Instructions/S1.png)

* The home button homes the motors of the unit
* The dottted grid is used to select the well type. Each type will only fit in the unit one way
* The arrow buttons allow the stages to be jogged
* The stop button is to cancel a motion
* The play button will start the programmed sequence
* The trigger button will start the programmed sequence once a TTL pulse is received
* The save button will save the current position as the origin of the well unit (Note the depth will be relative to this origin)
* The gear button will take you to the settings page

![Screen 2](https://github.com/garethnisbet/Fraction-Collection-Unit/blob/main/Instructions/S2.png)

* Pitch is the distance between the centre of two wells
* Depth sets the depth the capillary will travel relative to the origin
* Dwell Time is the time the unit will hold the capillary in the well
* Dwell Time (Sweep) is the time the unit will hold between iterations
* Speed sets the general travel speed of the unit

![Screen 3](https://github.com/garethnisbet/Fraction-Collection-Unit/blob/main/Instructions/S3.png)
* Starting Well allows the user to choose a starting well other than the first well
* Number of Wells allows the user to limit the number of wells in the sequence
* Number of Iterations is the number of times the sequence is repeated 

## Usage:
1. Run the GUI.py file
2. Press the home button before running the fraction collection sequence.


💡 **Note:** It is worth creating a desktop launcher for GUI.py. This will allow the machine to be controlled completely through the touchscreen. 
