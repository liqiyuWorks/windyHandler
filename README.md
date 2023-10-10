# windyHandler
A python library that can access and process the data from www.windy.com


## Description
windyHandler is a library including helper functions which can request and analyze the weather forecast data from www.windy.com


## How to install
```
pip3 install windyHandler
```
if you have a "permission" denied error, please try:
```
sudo pip3 install windyHandler
```


## Class
```
class windyWeather()
```
- org (string): 'EC' or 'GFS' (one of the world weather models)
- lon (float): longitude of the location
- lat (float): latitude of the location
- date (array, optional): 
    Array of length 4, stating (year, month, day, hour (UTC)) of rocket launch. Must be given if a Forecast, Reanalysis or Ensemble, will be set as an atmospheric model.
- timezone (string, optional)
    Name of the time zone. To see all time zones, import pytz and run print(pytz.all_timezones). Default time zone is "UTC".