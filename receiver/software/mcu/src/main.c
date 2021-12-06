//-----------------------------------------------------------------------------
// Includes
//-----------------------------------------------------------------------------

#include "SI_C8051F850_Register_Enums.h"
#include "SI_C8051F850_Defs.h"

//-----------------------------------------------------------------------------
// Defines
//-----------------------------------------------------------------------------

#define DBG_SAMPLE
#define BUFFER_DEPTH_BYTES  5
#define BUFFER_DEPTH_BITS  (8*BUFFER_DEPTH_BYTES)

#define SM_CODE0   0
#define SM_CODE1   1
#define SM_CODE2   2
#define SM_CODE3   3
#define SM_CODE4   4
#define SM_CODE5   5
#define SM_CODE6   6
#define SM_CODE7   7
#define SM___ZERO  8
#define SM_N_ZERO  9
#define SM___ONE   10
#define SM_N_ONE   11


SBIT(RX,       SFR_P0,  7);  
#ifdef DBG_SAMPLE
SBIT(SAMPLE,   SFR_P1,  4);  
#endif

//-----------------------------------------------------------------------------
// Global Variables
//-----------------------------------------------------------------------------

volatile U8 found;
volatile U8 buffer_head;
volatile U8 buffer_tail;
volatile U8 buffer[BUFFER_DEPTH_BYTES];

//-----------------------------------------------------------------------------
// Prototypes
//-----------------------------------------------------------------------------

void uartTx(U8 tx);
void setup(void);

//-----------------------------------------------------------------------------
// Main Routine
//-----------------------------------------------------------------------------

void main (void){        
   buffer_head = 0;
   buffer_tail = 0;  
   setup();
   SAMPLE      = 0;
   for(;;);
}
 
//-----------------------------------------------------------------------------
// Interrupt Vectors
//-----------------------------------------------------------------------------

INTERRUPT (TIMER2_ISR, TIMER2_IRQn){            
   U8 i;
   U8 ptr;
   U8 by;
   U8 bt;
   U8 state;

   IE = 0;   

   #ifdef DBG_SAMPLE
   // Toggle the sample pin 
   SAMPLE = 1; 
   #endif

   // Access bytes/bits
   by = buffer_head >> 3;
   bt = buffer_head & 0x07;
  
   // Masking
   if(RX){
      buffer[by] |=  (1 << bt);
   }else{
      buffer[by] &= ~(1 << bt);
   }

   // Update pointer
   buffer_head++;
   buffer_head %= BUFFER_DEPTH_BITS;

   found = 1;
   state = SM_CODE0;
   ptr   = buffer_head; 
   do{
      by = ptr >> 3;
      bt = ptr & 0x07;
      bt = 0x01 & (buffer[by] >> bt);
      switch(state){
         case SM_CODE0:    state = SM_CODE1; 
                           break;
         case SM_CODE1:    if(1 == bt) found = 0;
                           state = SM_CODE2;
                           break;
         case SM_CODE2:    state = SM_CODE3; 
                           break;
         case SM_CODE3:    if(0 == bt) found = 0;
                           state = SM_CODE4;
                           break;
         case SM_CODE4:    state = SM_CODE5; 
                           break;
         case SM_CODE5:    if(0 == bt) found = 0;
                           state = SM_CODE6;
                           break;
         case SM_CODE6:    state = SM_CODE7; 
                           break;
         case SM_CODE7:    if(1 == bt) found = 0;
                           state = SM_N_ONE;
                           break;
         case SM_N_ONE:    state = SM___ONE;
                           break; 
         case SM___ONE:    if(0 == bt) found = 0;
                           state = SM_N_ZERO;
                           break;
         case SM_N_ZERO:   state = SM___ZERO;
                           break;
         case SM___ZERO:   if(1 == bt) found = 0;
                           state = SM_N_ONE;
                           break; 
      }
      
      if(ptr == 0){
         ptr = BUFFER_DEPTH_BITS-1;
      }else{
         ptr--;
      } 
   }while(ptr != buffer_head); 

   if(found){
      ptr = buffer_head;
      do{
         by = ptr >> 3;
         bt = ptr & 0x07;
         bt = 0x01 & (buffer[by] >> bt); 
         uartTx(bt + '0');
         if(ptr == 0){
            ptr = BUFFER_DEPTH_BITS-1;
         }else{
            ptr--;
         } 
      }while(ptr != buffer_head);  
      uartTx('\n');
      uartTx('\r');

      // Clear the buffer
      for(i=0;i<BUFFER_DEPTH_BYTES;i++){
         buffer[i] = 0x00;
      }

   }
   // Buffer read to access 
   SAMPLE = 0; 
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
   CKCON    = CKCON_T1M__PRESCALE| 
              CKCON_T2ML__SYSCLK|
              CKCON_T2MH__SYSCLK;

   // Tiemr 1: UART 
   TMOD     = TMOD_T1M__MODE2;
	TCON     = TCON_TR1__RUN; 
   TH1      = 0x96;           // Magic values from datasheet for 115200
	TL1      = 0x96; 

   // Timer 2: Counter 2.68KHz
   // TODO: should be 2KHz
	TMR2CN   = TMR2CN_TR2__RUN; 
   TMR2L    = 0x0F;
   TMR2H    = 0xEE;
   TMR2RLL  = 0x0F;
   TMR2RLH  = 0xEE;
   
   // Interrupts
   IE = IE_EA__ENABLED | 
        IE_ET2__ENABLED;
}


