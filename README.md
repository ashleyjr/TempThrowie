# TempThrowie

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

### Hardware

   - TODO: Spec RF receiver

   - The microcontroller is continually monitoring the output of the receiver 
   - The sample rate is 2KHz
   - Every bit is placed in to a ring buffer 
   - There is a pattern detector searching for the code

      - Byte0: 0x?1?0?1?0
         ...
      - Bytes7: 0x?1?0?1?0
      - Bytes8: 0x?1?1?0?0

### Computer

   - The receiver hardware is connected to a host computer using a serial port
   - The serial port 
   
      - Has a baud rate of 115200
      - Transmits 1 start bit 
      - Transmits 8 bit data frame most significant bit first 
   
   - There are two scripts running on the computer

      - The *Logging Script* is continuously running and writing data
      - The *Analysis Script* may be envoked at anytime and reads the data
       
#### Logging Script

   - The script is called *base.py*
   - The serial port is continuously monitored 
   
      - When a frame is received a timeout window opens 
      - The window closes when no frame is recieved for 1 second
      - While the window is open all frames received are placed in to a buffer
      - The depth of the buffer is 10000 Bytes
      - If more than 10000 Bytes are recieved the entire buffer is discarded and the
        window is closed with an empty buffer

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


