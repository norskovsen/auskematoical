# AU - Skema to iCal

*This is not an official repo*



Since AU added a login page to get course information. It has not been possible to export the course information to your own calendar using existing third party tools. This is now possible using this script on your own computer without sending any login information to me. You just run the `skema.py` and enter your auID and password to get a `skema.ics` file which can be used in a calendar program such as Google Calendar.



![step1](img/preview.png)



I have only tested the script on Google Calendar and iCal on MacOS



If any mistakes are found please report them as issues or make a pull request. It should be easy to understand as it comply with the PEP8 conventions.



## How to use the script

**Step 1:**

Run the following command in the terminal to get the dependencies for the script

```bash
pip3 install -r requirements.txt
```



**Step 2:**

Run

```bash
python3 skema.py
```



**Step 3:**

Enter auID press enter and the your password and press enter

```
Whats your auID? auXXXXXX
Password: 
```



**Step 4:** 

If the auID and password combination is correct the program will proceed to generate the `ics` file otherwise the program will ask for your auID and password again



**Step 5:**

Success you now have a `skema.ics` file which you can use in your favorite calendar program



## Command line arguments

The script can be used with following command line arguments: 

```bash
usage: skema.py [-h] [-i INPUT] [-l] [-n] [-o OUTPUT]

Retrieve AU skema as ics

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        the filename of a local input file ending in .html
  -l, --logging         show the log
  -n, --notacademic     turn off academic starting time
  -o OUTPUT, --output OUTPUT
                        output file name ending in .ics
```

