# AU - Skema to iCal

*This is not an official repo*



Since AU added a login page to get course information it has not been possible to export the course information to your own calendar. This is now possible using this script on your own computer without sending any login information to me. You just download the html page yourself a use the `skema.py` to get a `skema.ics` file which can be used in your favorite kalendar program such as Google Calendar.



I have only tested the script on Google Calendar and thus I don't know whether it works on other Calendar programs such as iCal on MacOS



## How to use the script

**Step 1:**

Goto: https://timetable.scitech.au.dk/apps/skema/VaelgElevskema.asp?webnavn=skema&sprog=da

![step1](img/step1.png)

and login with your AU credentials



**Step 2:** 

Download the HTML page by pressing Ctrl+S

![step2](img/step2.png)

**Step 3:**

Save the HTML page in the same folder as this repo

![step3](img/step3.png)



**Step 4:**

Run the following command in the terminal to get the dependencies for the script

```bash
pip3 install -r requirements.txt
```



**Step 5:**

Run

```
python3 skema.py
```



**Step 6:**

Success you now have a skema.ics file which you can use in your favorite calendar program
