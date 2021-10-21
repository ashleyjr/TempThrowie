# TempThrowie

## Throwie

### Transmitter

#### Physical

   - Amplitude Modulated (AM) 
   - On Off Keying (OOK) 
   - 433MHz carrier
   - Asynchronous 1K bits per second (pbs) bit stream 

#### Packet

   - A packet is formed of 5 bytes
   - Each byte is sent least signifiant bit first in the following order
     with no spaces

      - Byte0: The preamble 0xD5/0b11010101
      - Byte1: The throwie identity (ID)
      - Byte2: The temperature reading
      - Byte3: The battery reading
      - Byte4: XOR (Byte3 ^ (Byte2 ^ Byte1))  

#### Collisions

   - Within a collection of throwwies the transmit intervals are asynchronous
   
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











   

## Basestation


