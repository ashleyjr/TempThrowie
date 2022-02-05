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

//-----------------------------------------------------------------------------
// Prototypes
//-----------------------------------------------------------------------------

void uartTx(U8 tx);
void setup(void);

//-----------------------------------------------------------------------------
// Main Routine
//-----------------------------------------------------------------------------

void main (void){        
   sm = 0; 
   send = SAMPLES;
   setup();  
   for(;;);
}
 
//-----------------------------------------------------------------------------
// Interrupt Vectors
//-----------------------------------------------------------------------------

INTERRUPT (TIMER2_ISR, TIMER2_IRQn){            
   U8 stride;
   
   // Disable all interrupts
   IE = 0;   
   SAMPLE=1;
   
   
   stride = sm % PERIOD;

   // Pattern search state machine
   // x000xx111xx000xx111...
   if(sm < LOCK_SAMPLES){ 
      switch(stride){ 
         case 1:  
         case 2:  
         case 3:  if(RX == 0) sm++;  
                  else        sm=0; 
                  break;  
         case 6:  
         case 7:  
         case 8:  if(RX == 1) sm++;  
                  else        sm=0; 
                  break; 
         default: sm++;             
                  break;
      }
   
   // Take 3 samples and use the median as the sample
   // xABCxxABCxxABCxxABC...
   }else{
      switch(stride){ 
         case 1:  
         case 6:  sample = RX;
                  break;
         case 2:  
         case 7:  sample += RX;
                  break;
         case 3:  
         case 8:  sample += RX;
                  if(sample > 1){
                     sample = 1;
                  }else{
                     sample = 0;
                  }  
                  break; 
         case 9:  sample_last = sample;
                  break;
         case 4:  if((sample_last == 0) && (sample == 1)){
                     uartTx('0');
                  }else{
                     if((sample_last == 1) && (sample == 0)){
                        uartTx('1');
                     }
                  }
                  break; 
      }
      
      
      
      
      sm++;
      if(sm == (SAMPLES+LOCK_SAMPLES)){ 
         uartTx('\n');
      }
      if(sm > (SAMPLES+LOCK_SAMPLES)){ 
         uartTx('\r');
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
   //while(!SCON0_TI); 
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


