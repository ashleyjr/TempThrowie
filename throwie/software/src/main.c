//-----------------------------------------------------------------------------
// Includes
//-----------------------------------------------------------------------------

#include "SI_C8051F850_Register_Enums.h"
#include "SI_C8051F850_Defs.h"

//-----------------------------------------------------------------------------
// Defines
//-----------------------------------------------------------------------------

// #define DBG_LED
#define DBG_UART
// #define ID              0 // Defined in makefile
#define ID_IDX             0
#define TEMP_IDX           1
#define BATT_IDX           2
#define XOR_IDX            3
#define PAY_SIZE_BYTES     4
#define PAY_SIZE_BITS      (8*PAY_SIZE_BYTES)
#define PRE_SIZE_BYTES     4
#define PRE_SIZE_BITS      (8*PRE_SIZE_BYTES)
#define SRT_SIZE_BYTES     1
#define SRT_SIZE_BITS      (8*SRT_SIZE_BYTES)
#define PRE_SRT_SIZE_BITS  (PRE_SIZE_BITS+SRT_SIZE_BITS)
#define PKT_SIZE_BITS      (PRE_SIZE_BITS+SRT_SIZE_BITS+PAY_SIZE_BITS)
#define SRT_CODE           0xAA

////////////////////////////////////////////
// These are the setting for a Rev C device
//
//  64 * 1023 = 65472 = 1.65V
//  (ADC does 64 reads and accumlates)
//
//  757mV @ 0C
//  2.85mV/C
// 
//  -12C = 722.8mV = 65472*(0.7228/1.65) = 28681 
//   51C = 902.4mV = 65472*(0.9024/1.65) = 35807
//
//   Scale = (35807-28681)/256 = 27.835

#define TEMP_LO 28681 
#define TEMP_HI 35807
#define TEMP_SC 28

SBIT(MOD,  SFR_P0, 7);  
#ifdef DBG_LED
SBIT(LED,  SFR_P1, 1);  
#endif // DBG_LED

//-----------------------------------------------------------------------------
// Global Variables
//-----------------------------------------------------------------------------

volatile U8 clk;
volatile U16 ptr;
volatile U8 payload[PAY_SIZE_BYTES];

//-----------------------------------------------------------------------------
// Prototypes
//-----------------------------------------------------------------------------

#ifdef DBG_UART
void uartTx(U8 tx);
void uartHex(U8 tx);
void uartNum(U16 n);
#endif // DBG_UART
void sleep(void);

//-----------------------------------------------------------------------------
// Main Routine
//-----------------------------------------------------------------------------

void main (void){        
   payload[ID_IDX] = ID; 
   for(;;){ 
       
      sleep(); 
       
      #ifdef DBG_LED
      LED = 1; 
      #endif // DBG_LED
   
      // Read Battery ADC 
      ADC0CN0  = ADC0CN0_ADEN__ENABLED | 
                 ADC0CN0_ADBUSY__SET;
      ADC0MX   = ADC0MX_ADC0MX__ADC0P2;    
      REF0CN   = REF0CN_REFSL__VDD_PIN; 
      ADC0CF   = ADC0CF_ADTM__TRACK_DELAYED | 
                 ADC0CF_ADGN__GAIN_1;          
      ADC0CN1  = ADC0CN1_ADCMBE__CM_BUFFER_ENABLED;
      ADC0AC   = ADC0AC_AD12BE__12_BIT_ENABLED|
                 ADC0AC_ADAE__ACC_ENABLED|
                 ADC0AC_ADRPT__ACC_4;
      ADC0PWR  = (0 << ADC0PWR_ADPWR__SHIFT) | 
                 ADC0PWR_ADLPM__LP_BUFFER_DISABLED | 
                 ADC0PWR_ADMXLP__LP_MUX_VREF_DISABLED | 
                 ADC0PWR_ADBIAS__MODE3; 
      ADC0CN0  = ADC0CN0_ADBMEN__BURST_ENABLED|
                 ADC0CN0_ADEN__ENABLED | 
                 ADC0CN0_ADBUSY__SET;
      while(0 == (ADC0CN0 & ADC0CN0_ADINT__SET)); 
      payload[BATT_IDX] = ADC0 >> 4;  
      
      // Read temperature diode
      ADC0MX   = ADC0MX_ADC0MX__TEMP;    
      REF0CN   = REF0CN_REFSL__INTERNAL_VREF |
                 REF0CN_IREFLVL__1P65 |
                 REF0CN_TEMPE__TEMP_ENABLED; 
      ADC0CF   = ADC0CF_ADTM__TRACK_DELAYED | 
                 ADC0CF_ADGN__GAIN_1;          
      ADC0CN1  = ADC0CN1_ADCMBE__CM_BUFFER_ENABLED;
      ADC0AC   = ADC0AC_AD12BE__12_BIT_ENABLED|
                 ADC0AC_ADAE__ACC_ENABLED|
                 ADC0AC_ADRPT__ACC_64;
      ADC0PWR  = (0 << ADC0PWR_ADPWR__SHIFT) | 
                 ADC0PWR_ADLPM__LP_BUFFER_DISABLED | 
                 ADC0PWR_ADMXLP__LP_MUX_VREF_DISABLED | 
                 ADC0PWR_ADBIAS__MODE3; 
      ADC0CN0  = ADC0CN0_ADBMEN__BURST_ENABLED|
                 ADC0CN0_ADEN__ENABLED | 
                 ADC0CN0_ADBUSY__SET;
      while(0 == (ADC0CN0 & ADC0CN0_ADINT__SET));  
   
      // Scale temp to 8 bits 
      if(ADC0 < TEMP_LO){
         payload[TEMP_IDX] = 0;
      }else{
         if(ADC0 > TEMP_HI){
            payload[TEMP_IDX] = 255;
         }else{
            payload[TEMP_IDX] = (ADC0 - TEMP_LO) / TEMP_SC; 
         }
      } 
     
      // XOR
      payload[XOR_IDX]  = payload[ID_IDX];
      payload[XOR_IDX] ^= payload[TEMP_IDX];
      payload[XOR_IDX] ^= payload[BATT_IDX];

      // Zero pointer and start sending 
      ptr = 0;
      IE |= IE_EA__ENABLED; 
       
      #ifdef DBG_UART
      uartHex(payload[ID_IDX]);
      uartHex(payload[TEMP_IDX]);
      uartHex(payload[BATT_IDX]);
      uartHex(payload[XOR_IDX]);
      uartTx(' ');
      uartTx('(');
      uartTx('T');
      uartTx(':');
      uartNum(payload[TEMP_IDX]);
      uartTx(',');
      uartTx('B');
      uartTx(':');
      uartNum(payload[BATT_IDX]);
      uartTx(')');
      uartTx('\n');
      uartTx('\r');
      #endif  
       
      // Wait until sent
      while(ptr < PKT_SIZE_BITS); 
      
      #ifdef DBG_LED
      LED = 0; 
      #endif // DBG_LED
   };
}
 
//-----------------------------------------------------------------------------
// Interrupt Vectors
//-----------------------------------------------------------------------------

INTERRUPT (TIMER0_ISR, TIMER0_IRQn){
   IE = 0;
}

INTERRUPT (TIMER2_ISR, TIMER2_IRQn){           
   U8 bt; 
   U8 by;
   U8 value;
   
   if(ptr < PRE_SIZE_BITS){
      // PREAMBLE STAGE
      value = 1;
   }else{
      if(ptr < PRE_SRT_SIZE_BITS){
         // START STAGE
         bt  = SRT_CODE >> (ptr -  PRE_SIZE_BITS );
         value = bt & 0x01; 
      }else{
         if (ptr < PKT_SIZE_BITS){
            // PAYLOAD STAGE
            bt  = (ptr - PRE_SRT_SIZE_BITS); 
            by  = bt / 8;
            bt  = bt - (by * 8);
            value = 0x01 & (payload[by] >> bt);  
         }else{
            // STALL
            value = 0;
         }
      }
   }
   // Clock
   clk++;
   clk %= 2;

   // Manchester encoding
   if((ptr <= PKT_SIZE_BITS) && (
         ((clk == 1) && (value == 1))||
         ((clk == 0) && (value == 0)))
      ){ 
      MOD = 1;
   }else{
      MOD = 0;
   }
  
   // Update ready for next phase 
   if(clk == 0){
      ptr++;
   }
  
   TMR2CN &= ~TMR2CN_TF2H__SET;
}


//-----------------------------------------------------------------------------
// Debug UART
//-----------------------------------------------------------------------------

#ifdef DBG_UART
void uartTx(U8 tx){
   SCON0_TI = 0;
   SBUF0 = tx;
   while(!SCON0_TI); 
}

void uartHex(U8 tx){
   U8 i,j;
   for(i=4;i<5;i-=4){
      j = (tx >> i) & 0xF;
      if(j > 9){
         uartTx(j + 'A' - 10);
      }else{
         uartTx(j + '0');
      }
   }

}
void uartNum(U16 tx){
   U16 n;
   U8 i;
   U8 c [5];
   n = tx; 
   for(i=0;i<5;i++){
      c[4-i] = (n % 10);
      n = n - c[4-i];
      n = n / 10;
      c[4-i] += '0';
   }
   for(i=0;i<5;i++){
      uartTx(c[i]); 
   }
}
#endif // DBG_UART

//-----------------------------------------------------------------------------
// Setup/sleep
//-----------------------------------------------------------------------------

void sleep(void){

   // Disabled watchdog
   WDTCN    = 0xDE;
   WDTCN    = 0xAD;

   // Enabled LFOSC
   //    - Set to 10KHz
   OSCLCN = OSCLCN_OSCLEN__DISABLED;
   OSCLCN = OSCLCN_OSCLEN__ENABLED |
            OSCLCN_OSCLD__DIVIDE_BY_8;
   

   // Enabled T1 interrupt
   IE   = IE_EA__ENABLED | 
		    IE_ET0__ENABLED;
   

   // Configure T0
   CKCON  = CKCON_T0M__PRESCALE|
            CKCON_SCA__SYSCLK_DIV_48;  
	TMOD   = TMOD_T0M__MODE1;	 
   TL0    = 0xFA;
   TH0    = 0xFF;
   

   // Main clock is the Low Frequency Clock 
    while(1){
      if(OSCLCN & OSCLCN_OSCLRDY__SET){
         break;
      }
   }
   CLKSEL = CLKSEL_CLKSL__LFOSC|
            CLKSEL_CLKDIV__SYSCLK_DIV_128 ;
   
   // Start T0
   TCON   = TCON_TR0__RUN;     


   // Go to sleep
   PCON = PCON_IDLE__IDLE ;
   PCON = PCON;


   // !!! Get woken up by timer
   

   // Clock
	CLKSEL   = CLKSEL_CLKSL__HFOSC |			     
              CLKSEL_CLKDIV__SYSCLK_DIV_1; 
   
   // Enable IOs
   #ifdef DBG_UART
   P0MDOUT  = P0MDOUT_B4__PUSH_PULL|
              P0MDOUT_B7__PUSH_PULL;
   #else
   P0MDOUT  = P0MDOUT_B7__PUSH_PULL;
   #endif // DBG_UART
   
   #ifdef DBG_LED
   P1SKIP   = P1SKIP_B1__SKIPPED; 
   P1MDOUT  = P1MDOUT_B1__PUSH_PULL;
   #endif // DBG_LED
   
   #ifdef DBG_UART
   XBR0     = XBR0_URT0E__ENABLED;
   #endif // DBG_UART
   
   XBR2     = XBR2_WEAKPUD__PULL_UPS_DISABLED | 
              XBR2_XBARE__ENABLED;
   
   // Setup Timers
   CKCON    = CKCON_T1M__SYSCLK;  
	
   // Timer 1 
   //    - UART
   #ifdef DBG_UART
   TMOD     = TMOD_T1M__MODE2;
	TCON     = TCON_TR1__RUN; 
   TH1      = 0x96;           // Magic values from datasheet for 115200
	TL1      = 0x96;
   #endif // DBG_UART

   // Timer 2
	//    - Frequency 2KHz
   TMR2CN   = TMR2CN_TR2__RUN;
   TMR2L    = 0x00;
   TMR2H    = 0xFC;
   TMR2RLL  = 0x00;
   TMR2RLH  = 0xFC;
  
   // Set clock phase
   clk = 0;

   // Interrupts
   IE = IE_ET2__ENABLED;
}


