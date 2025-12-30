# KPSC_Automation
KPSC vacancy reporting, advise details are notified easily
save check.py script in a webserver folder "psc"
create a cron job in webserver for hourly execution of python script and cron command is /usr/bin/python3 /home/usrname/public_html/psc/check.py >> /home/usrname/public_html/psc/check_script.log 2>&1
enable pyton on webserver - here am using name cheap webserver, goto python web application in tools section, create a new application as follows:
Python version  - 3
Application root - psc
Application URL - psc
Application startup file - check.py
then save it.
Jobe done !!!

Code:
payload = {
    'k': '690/2022', #code for post
    'dist': '00' #district code, default its zero
    }

  for  value in data:
            #if not key.isdigit():   # skip numeric keys
                print(value["sl_no"],value["vcy_type"],value["vcy_dt"])
                if int(value["sl_no"]) >= 4:
                #here 4 is last reported vacancy number. if 5th vacancy reported, it triggers an email to us.

