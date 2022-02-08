//-----------------------------------------------------------------------------
// Includes
//-----------------------------------------------------------------------------

#include "SI_C8051F850_Register_Enums.h"
#include "SI_C8051F850_Defs.h"

//-----------------------------------------------------------------------------
// Defines
//-----------------------------------------------------------------------------

#define DBG_SAMPLE
#define SAMPLE_BYTES 16
#define SAMPLE_BITS (8*SAMPLE_BYTES)
#define PERIOD 10
#define LOCK_PERIODS 10
#define LOCK_SAMPLES (PERIOD*LOCK_PERIODS)
#define SAMPLES (PERIOD*SAMPLE_BITS)

SBIT(RX,       SFR_P0,  7);  
SBIT(SAMPLE,   SFR_P1,  4);  

//-----------------------------------------------------------------------------
// Global Variables
//-----------------------------------------------------------------------------

volatile U16 sm;
volatile U16 send;
volatile char sample0;
volatile char sample1;
volatile char sample2;
volatile char sample;
volatile char sample_last;
volatile char locking;
volatile U8 start;
volatile U32 data;
volatile U16 finish;
volatile U8 pay[4];

//-----------------------------------------------------------------------------
// Prototypes
//-----------------------------------------------------------------------------

void uartTx(U8 tx);
void setup(void);

//-----------------------------------------------------------------------------
// Main Routine
//-----------------------------------------------------------------------------

void main (void){        
   U8 i;
   U8 j;
   U8 nibble;
   sm = 0; 
   send = 0;
   setup();  
   for(;;){
      if(send){
         // Send the data if it passes the checking
         if(pay[3] == (pay[0] ^ pay[1] ^ pay[2])){ 
            for(i=0;i<4;i++){
               for(j=0;j<8;j+=4){
                  nibble = (pay[i] >> j) & 0xF;
                  if(nibble < 10){
                     uartTx(nibble + '0');
                  }else{
                     uartTx(nibble - 10 + 'A');
                  }
               }
            }
            uartTx('\n');
            uartTx('\r');
         }
         send=0;
      }
   };
}
 
//-----------------------------------------------------------------------------
// Interrupt Vectors
//-----------------------------------------------------------------------------

INTERRUPT (TIMER2_ISR, TIMER2_IRQn){            
   U8 stride;
   char decode;

   // Disable all interrupts
   IE = 0;   
   SAMPLE=1;
   
   
   stride = sm % PERIOD;

   // Pattern search state machine
   // x000xx111xx000xx111...
   if(sm < LOCK_SAMPLES){ 
      locking = 1;
      start = 0;
      switch(stride){ 
         case 0:
         case 1:  
         case 2:  
         case 3:  
         case 4:  if(RX == 0) sm++;  
                  else        sm=0; 
                  break;  
         case 5:
         case 6:  
         case 7:  
         case 8:  
         case 9:  if(RX == 1) sm++;  
                  else        sm=0; 
                  break; 
         default: sm++;             
                  break;
      }
   
   // Take 3 samples and use the median as the sample
   // xABCxxABCxxABCxxABC...
   }else{
      switch(stride){ 
         case 0:  
         case 5:  sample = RX;
                  break;
         case 1: 
         case 2:
         case 3:
         case 6:
         case 7:
         case 8:  sample += RX;  
                  break; 
         case 9:  sample += RX;
                  
                  if(sample > 2){
                     sample_last = 1;
                  }else{
                     sample_last = 0;
                  }
                  break;
         
         case 4:  sample += RX;
                  
                  if(sample > 2){
                     sample = 1;
                  }else{
                     sample = 0;
                  }
                  
                  if((sample_last == 0) && (sample == 1)){
                     decode = 0;
                  }else{
                     if((sample_last == 1) && (sample == 0)){
                        decode = 1; 
                     }
                  }

                  if(locking){
                     start = start >> 1;
                     start |= decode << 7;
                     if(start == 0xAA){
                        locking = 0;
                        data = 0;
                        finish = 0;
                     }
                  }else{
                     if(finish < 32){
                        pay[finish>>3] = pay[finish>>3] >> 1;
                        pay[finish>>3] |= decode << 7;
                        finish++;
                        if(finish == 32){
                           send = 1;
                        }
                     }
                  }


                  break; 
      } 
      sm++;
      if(sm > (SAMPLES+LOCK_SAMPLES)){  
         sm=0;
      }
      SAMPLE=0;  

   }
   

   // Enable the interrupts
   TMR2CN &= ~TMR2CN_TF2H__SET;
   IE = IE_EA__ENABLED | 
        IE_ET2__ENABLED;  
} 

//-----------------------------------------------------------------------------
// UART
//-----------------------------------------------------------------------------

void uartTx(U8 tx){ 
   SCON0_TI = 0;
   SBUF0 = tx;
   while(!SCON0_TI); 
}

//-----------------------------------------------------------------------------
// Setup
//-----------------------------------------------------------------------------

void setup(void){

   // Disabled watchdog
   WDTCN    = 0xDE;
   WDTCN    = 0xAD;

	CLKSEL   = CLKSEL_CLKSL__HFOSC |			     
              CLKSEL_CLKDIV__SYSCLK_DIV_1; 
   
   // Enable IOs 
   P0SKIP   = P0SKIP_B7__SKIPPED; 


   //P0MDIN   = P0MDIN_B7__DIGITAL; 
   //P0SKIP   = P0SKIP_B7__SKIPPED; 
   //P0MDOUT  = P0MDOUT_B4__PUSH_PULL; 
  
   #ifdef DBG_SAMPLE 
   P1MDOUT  = P1MDOUT_B4__PUSH_PULL; 
   #endif

   XBR0     = XBR0_URT0E__ENABLED; 
   XBR2     = XBR2_WEAKPUD__PULL_UPS_DISABLED | 
              XBR2_XBARE__ENABLED;
   
   // Setup Timers
   CKCON    = CKCON_T1M__SYSCLK| 
              CKCON_T2ML__SYSCLK|
              CKCON_T2MH__SYSCLK;

   // Tiemr 1: UART 
   TMOD     = TMOD_T1M__MODE2;
	TCON     = TCON_TR1__RUN; 
   TH1      = 0x96;           // Magic values from datasheet for 115200
	TL1      = 0x96; 

   // Timer 2: 
   //    - Runs as fast as possible
   //    - 10KHz 
	TMR2CN   = TMR2CN_TR2__RUN; 
   TMR2L    = 0x62;
   TMR2H    = 0xF6;
   TMR2RLL  = 0x62;
   TMR2RLH  = 0xF6;
   
   // Interrupts
   IE = IE_EA__ENABLED | 
        IE_ET2__ENABLED;
}


