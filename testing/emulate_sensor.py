import urllib2
import time
import datetime
from random import randint

def main():
    # Base URL
    url = 'http://ajrobinson.org/scratch/TempThrowie/TempThrowie.php'

    # Random sensor choice
    choice = randint(0,2)
    device = 'device='
    if 0 == choice:
        device += "Boiler"
    if 1 == choice:
        device += "Bedroom"
    if 2 == choice:
        device += "Lounge"

    # Get the time stamp
    stamp = 'time=' + datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')

    # Random input data
    data = 'data=' + str(randint(0,99))

    # Print the csv file as feedback
    # TODO: This could get quite long
    feedback = 'print'

    # Compile and submit the data
    sub = url + '?' + device + '&' + stamp + '&' + data + '&' + feedback
    response = urllib2.urlopen(sub)
    print sub

    # Print the response
    html = response.read()
    print html

if __name__ == "__main__":
    main()
