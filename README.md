# Python script to query US Visa website and find early appointments

The script is tested on Mac OS 13.6 with Python 3.9. I uses selenium to auto-launch a browswer to log-in and call APIs to see if there are available appointments.


## Notes
* It queries against Canadian embassies only. To query against other embassy, change the `LOCATION_MAP` accordingly.
* By default, when an apponitment is found, a message describing the appointment will be read out aloud using Mac's `say` command. One can use the notification() method to change it to other ways of alerting like pushover API.

## Instructions to run
1. `pip install -r requirements.txt`
1. Go to `https://ais.usvisa-info.com/` and login manually
1. Find out schedule number by monitoring the network traffic CURL request sent from your browswer
1. Ran the script with the necessary arguments in an always-open terminal. Example:
python visa.py -u '<your_username>' -p '<your_password>' -s <8-digit-schedule-number>
