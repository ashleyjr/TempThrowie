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


