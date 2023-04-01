# @Author Jack Lindsey-Noble
# Created Sat April 1st 2023
# Happy April fools!
# This is a program used to tell me when my bus will arrive at my house, and when it will arrive at my school.
# I am scraping the data from an RIT website, so if that website changes, this code may not work.

#!/usr/bin/env python3
import sys
import requests
from datetime import datetime
from datetime import date
import time
import re

# current dateTime
now = datetime.now()
todays_date = date.today()

# convert to time String
current_time = now.strftime("%H:%M")

#Scraping from the RIT bus schedule website.
URL = "https://www.rit.edu/parking/5-province"
page = requests.get(URL)
pageText = page.text

#This is a little confusing, but I am just trimming all the data down to what I need
trimmed_info = pageText[pageText.find('<tbody>'):][:pageText[pageText.find('<tbody>'):].find('</tbody>')]
#Empty array to be filled with slightly parsed times.
string_times = []
#Here I use regex to find all the times
pattern = r'<td>(.*?)</td>'
string_times = re.findall(pattern, trimmed_info)

#I need to make the times readable to the datetime library.
for i in range(len(string_times)):
    new_string = string_times[i]

    #This is a case for bus breaks they are formatted like "2:10 PM/2:20 PM" so I need to shorten them
    if len(string_times[i]) > 9:
        new_string = string_times[i][0:7]
    
    if("pm" in string_times[i]):
        string_times[i] = new_string[0:4] + ":00PM"
    else:
        string_times[i] = new_string[0:4] + ":00AM"

#This function is used to get rid of the NTID row, because I really dont need to know when those times are.
def separate_times(times):
    province_times = []
    f_lot_times = []
    count = 0;
    for i in range(len(times)):
        if count == 0:
            province_times.append(times[i])
        if count == 2:
            f_lot_times.append(times[i])
        count += 1;
        if count == 3:
            count = 0
    return province_times,f_lot_times

#Here I am converting the string times list in a list of actual datetime.time objects.
time_objects = []
for times in string_times:
    time_objects.append(datetime.strptime(times, '%I:%M:%S%p').time())

#Set a datetime.time object for the CURRENT time when we run the program, we just have to initialize it.
current_time_object = datetime.strptime(current_time, "%H:%M").time()

#Using separate times, we can grab the two lists of bus arrival times that we actually need.
province_times,f_lot_times = separate_times(time_objects)

#This function sifts through a given list of times, and returns the next one
#if there isn't a next one it returns tomorrow morning time.
def get_next_time(bus_times, next_time):
    for times in bus_times:
        if times > next_time:
            return times
        else:
            return bus_times[0]

#This function will count down to a specific time, and display that time to the user.
def countdown(stop, place):
    while True:
        #Grab the current time object again so it is updated.
        current_time_object = update_time()

        #Calculate the difference between current time and the time of the buses current destination.
        difference = datetime.combine(todays_date, stop)- datetime.combine(todays_date, current_time_object)
        count_hours, rem = divmod(difference.seconds, 3600)
        count_minutes, count_seconds = divmod(rem, 60)

        #For when the bus arrives.
        if difference.days == 0 and count_hours == 0 and count_minutes == 0 and count_seconds == 0:
            print("\n")
            print("The bus has arrived")
            break
        
        #Here I am printing to the user the current status of the bus.
        print('[+] Bus is on its way to ' + place + ', leaving in: '
              + str(count_minutes) + " minute(s) "
              + str(count_seconds) + " second(s) ", end=("\r")
              )
        time.sleep(1)

#Used above and below to reset the current time of the program.
def update_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return datetime.strptime(current_time, "%H:%M:%S").time()

#Main method
def main():
    while True:
        #Grab the current time object again so it is updated.
        current_time_object = update_time()

        #Calculate the next time that the bus will arrive at F_Lot and Province.
        time_to_province = get_next_time(province_times, current_time_object)
        time_to_f_lot = get_next_time(f_lot_times, current_time_object)

        #Print those times.
        print("Next bus times: " + "\n")
        print("Province: " + time_to_province.strftime("%I:%M %p"))
        print("F Lot: " + time_to_f_lot.strftime("%I:%M %p"))
        print("\n")

        #Depending on where the bus is currently heading, we display a count down to that location.
        if time_to_province < time_to_f_lot:
            countdown(time_to_province, "Province")
        else:
            countdown(time_to_f_lot, "F Lot")

#Finally, run the program :)
main()

