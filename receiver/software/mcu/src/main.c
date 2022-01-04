//-----------------------------------------------------------------------------
// Includes
//-----------------------------------------------------------------------------

#include "SI_C8051F850_Register_Enums.h"
#include "SI_C8051F850_Defs.h"

//-----------------------------------------------------------------------------
// Defines
//-----------------------------------------------------------------------------

#define DBG_SAMPLE

SBIT(RX,       SFR_P0,  7);  
//#ifdef DBG_SAMPLE
SBIT(SAMPLE,   SFR_P1,  4);  
//#endif

//-----------------------------------------------------------------------------
// Global Variables
//-----------------------------------------------------------------------------

volatile U8 sample;

//-----------------------------------------------------------------------------
// Prototypes
//-----------------------------------------------------------------------------

char receiver_pll(char i);
void uartTx(U8 tx);
void setup(void);

//-----------------------------------------------------------------------------
// Main Routine
//-----------------------------------------------------------------------------

void main (void){        
   sample=0;
   setup();
   for(;;);
}
 
//-----------------------------------------------------------------------------
// Interrupt Vectors
//-----------------------------------------------------------------------------

INTERRUPT (TIMER2_ISR, TIMER2_IRQn){            
   // Disable all interrupts
   IE = 0;   

   #ifdef DBG_SAMPLE
   // Start the sample 
   SAMPLE = 1; 
   #endif

   // Call the lock function 
   SAMPLE = receiver_pll(RX);

   // Enable the interrupts
   TMR2CN &= ~TMR2CN_TF2H__SET;
   IE = IE_EA__ENABLED | 
        IE_ET2__ENABLED; 
   
   #ifdef DBG_SAMPLE
   // End the sample 
   SAMPLE = 0; 
   #endif 
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
   CKCON    = CKCON_T1M__PRESCALE| 
              CKCON_T2ML__SYSCLK|
              CKCON_T2MH__SYSCLK;

   // Tiemr 1: UART 
   TMOD     = TMOD_T1M__MODE2;
	TCON     = TCON_TR1__RUN; 
   TH1      = 0x96;           // Magic values from datasheet for 115200
	TL1      = 0x96; 

   // Timer 2: 
   //    - Runs as fast as possible
   //    - 3.33KHz 
	TMR2CN   = TMR2CN_TR2__RUN; 
   TMR2L    = 0x90;
   TMR2H    = 0xF1;
   TMR2RLL  = 0x90;
   TMR2RLH  = 0xF1;
   
   // Interrupts
   IE = IE_EA__ENABLED | 
        IE_ET2__ENABLED;
}


