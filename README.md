# TempThrowie: Install

## MCUs

   - SDCC : mcs51/z80/z180/r2k/r3ka/gbz80/tlcs90/ds390/TININative/ds400/hc08/s08/stm8 3.5.0
   - SimplicityStudio_v4 flash8051
   - Silicon Labs 8-Bit USB Debug Adapter

## Basestation (Raspberry Pi)

   - Basestation is a Raspberry Pi Model B Plus Rev 1.2
   - Fresh install of Raspbian GNU/Linux 11 (bullseye)
   - pip install matplotlib
   - sudo apt-get install libatlas-base-dev
   - pip install numpy --upgrade
   - sudo apt install apache2 -y
   - sudo apt-get install php libapache2-mod-php 
   - Config:

```
(21:10 pi@raspberrypi ~) > crontab -l | tail -n 1
*/20 * * * * cd /home/pi/TempThrowie/receiver/software/base/; python throwieAnalysis.py --stats --log stats.log; python throwieAnalysis.py --plotbatttoday --out ../webpage/batttoday.png --log batttoday.log; python throwieAnalysis.py --plottemptoday --out ../webpage/temptoday.png --log temptoday.log; python throwieAnalysis.py --plotbattweek --out ../webpage/battweek.png --log battweek.log; python throwieAnalysis.py --plottempweek --out ../webpage/tempweek.png --log tempweek.log
(21:10 pi@raspberrypi ~) > tail -n 5 /etc/rc.local 
# Run TempThrowie UART monitor
rm /home/pi/TempThrowie/receiver/software/base/throwie.db
cd /home/pi/TempThrowie/receiver/software/base; python throwieLogging.py &

exit 0
(21:10 pi@raspberrypi ~) > cat /etc/apache2/sites-available/000-default.conf | grep DocumentRoot
	DocumentRoot /home/pi/TempThrowie/receiver/software/webpage/
(21:10 pi@raspberrypi ~) > cat /etc/apache2/apache2.conf | grep TempThrowie -A4
<Directory /home/pi/TempThrowie/receiver/software/webpage/>
	Options Indexes FollowSymLinks
	AllowOverride None
	Require all granted
</Directory>
(21:10 pi@raspberrypi ~) > 
```

## Basestation (Laptop)

   - MacBook Pro 2019
   - Virtual Box Virtual Machine
   - Ubuntu 20.04.4 LTS
   - sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 10
   - sudo apt-get install python3-pip
   - python -m pip install pyserial 
   - python -m pip install matplotlib
   - sudo apt install imagemagick-6.q16

# TempThrowie: Spec

## Throwie

### Transmitter

#### Physical

   - Amplitude Modulated (AM) 
   - On Off Keying (OOK) 
   - 433MHz carrier
   - Asynchronous 1K bits per second (pbs) bit stream 

#### Packet

   - A packet is formed of 64 bytes
   - Each byte is sent least signifiant bit first in the following order
     with no spaces

      - Byte0:  The preamble code 0xAA/0x10101010
         ...
      - Byte58: The preamble code 0xAA/0x10101010
      - Byte59: The start code 0x6A/0b01101010
      - Byte60: The throwie identity (ID)
      - Byte61: The temperature reading
      - Byte62: The battery reading
      - Byte63: XOR (Byte3 ^ (Byte2 ^ Byte1))  

#### Collisions

   - Within a collection of throwies the transmit intervals are asynchronous
   
   - A packet is transmitted every 10 minutes
   
   - The 40 bits in each packet takes 40ms to transmit

   - Probability of a collision

      - x = ((n-1) * d) / t

      - n = Number of thowies in collection

      - d = Duration of tranmissions (seconds) = 0.04

      - t = Transmit interval (seconds) = 600

   - Probability of failure when n is

      - 2:     x = 0,04 / 600          = 6.6 * 10^-5
      - 10:    x = (9 * 0,04) / 600    = 6   * 10^-4
      - 256:   x = (255 * 0,04) / 600  = 1.7 * 10^-2
   
   - Mean time between failure at 144 transmissions a day when n is
      
      - 2:     105 days 
      - 10:    12 days    
      - 256:   0.41 days

   - **This does not include failures caused by interference from other devices**

### Measurements

#### Temperature

   - Range between -10C and 50C
   - In the transmitted byte encoding each increment is worth 0.234C ((50 - (-10))/256) 
   - The offset is not calibrated

#### Battery

   - Range between 3.3V and 7V
   - In the transmitted byte encoding each increment is worth 0.014V ((7 - 3.3)/256) 
   - The offset is calibrated and 0 represent the lower voltage


## Receiver

### The serial port 
   
   - Has a baud rate of 115200
   - Transmits 1 start bit 
   - Transmits 8 bit data frame most significant bit first 
   
### Hardware

   - TODO: Spec RF receiver

   - The microcontroller is continually monitoring the output of the receiver 
   - The sample rate is 2KHz 
   - There is a pattern detector searching for the following 8 bytes

      - Byte0: 0b?1?0?1?0
         ...
      - Bytes6: 0b?1?0?1?0
      - Bytes7: 0b?0?1?1?0

   - When the code is detected the next 8 bytes are placed in to a buffer
     and immediately transmitted over the serial port
   - When the last byte is transmitted the microcontroller goes back to 
     pattern detection

### Computer

   - The receiver hardware is connected to a host computer using a serial port   
   - There are two scripts running on the computer

      - The *Logging Script* is continuously running and writing data 
      - The *Analysis Script* may be envoked at anytime and reads the data
       
#### Logging Script

   - The script is called *throwieLogging.py*
   - The serial port is continuously monitored 
   
      - When a frame is received a timeout window opens 
      - The window closes when no frame is recieved for 2 seconds
      - While the window is open all frames received are placed in to a buffer
      - The depth of the buffer is 500 Bytes

         - As the sample rate of the microcontroller is 2KHz it is impossible to 
           overflow this buffer

   - When the timeout window closes 
      
      - A string is created by draining the buffer
      - Each byte is converted to a two character hexadecimal string   
      - More bytes are added to the right hand side of the string 
      - When the buffer is fully drained the left hand side contains the first byte
        recieved and right hand side contained the last byte recieved

   - The string is written to a log file

      - The file is called **throwie_YYYYMMDD_HHSS.log**

         - Y = Year
         - M = Month
         - D = Day
         - H = Hour (24h)
         - M = Minute

      - The file is located in the same directory as the script  

#### Analysis Script

   - The script is called *throwieAnalysis.py*
   - The setup phase

      - Will open every log file in chronological order
      - Create a list of transmissions containing 

         - The date
         - The time
         - The 

      - If the log file contains 8 bytes of data it will analyse 



