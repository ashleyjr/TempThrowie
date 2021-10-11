//-----------------------------------------------------------------------------
// Includes
//-----------------------------------------------------------------------------

#include "SI_C8051F850_Register_Enums.h"
#include "SI_C8051F850_Defs.h"

//-----------------------------------------------------------------------------
// Defines
//-----------------------------------------------------------------------------

SBIT(MOD,  SFR_P0, 7);  
SBIT(LED,  SFR_P1, 1);  

//-----------------------------------------------------------------------------
// Global Variables
//-----------------------------------------------------------------------------

volatile U16 ptr;
volatile U8  payload[10];
//-----------------------------------------------------------------------------
// Prototypes
//-----------------------------------------------------------------------------

void uartTx(U8 tx);
void sleep(void);

//-----------------------------------------------------------------------------
// Main Routine
//-----------------------------------------------------------------------------

void main (void){     
   
   payload[0] = 'A';
   payload[1] = 'A';
   payload[2] = 'A';
   payload[3] = 'A';


   while(1){
      ptr = 0;
      sleep();
      LED = 1;
      uartTx('A'); 
      while(ptr < (8*4));
      LED = 0; 
   };
}
 
//-----------------------------------------------------------------------------
// Interrupt Vectors
//-----------------------------------------------------------------------------

INTERRUPT (TIMER0_ISR, TIMER0_IRQn){
   IE = 0;
}

INTERRUPT (TIMER2_ISR, TIMER2_IRQn){           
   U8 bit_ptr;
   U8 byte_ptr;
   bit_ptr  = ptr & 0x7;
   byte_ptr = ptr >> 3;
   MOD = 0x01 & (payload[byte_ptr] >> bit_ptr); 
   ptr++;
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
   P0MDOUT  = P0MDOUT_B4__PUSH_PULL|
              P0MDOUT_B7__PUSH_PULL;
   P1SKIP   = P1SKIP_B1__SKIPPED; 
   P1MDOUT  = P1MDOUT_B1__PUSH_PULL;
   XBR0     = XBR0_URT0E__ENABLED;
   XBR2     = XBR2_WEAKPUD__PULL_UPS_DISABLED | 
              XBR2_XBARE__ENABLED;

   // Setup Timers
   CKCON    = CKCON_T1M__SYSCLK;  
	TMOD     = TMOD_T1M__MODE2;
	TCON     = TCON_TR1__RUN; 
   TH1      = 0x96;  // Magic values from datasheet for 115200
	TL1      = 0x96;
  
   // Timer 2: Counter 10KHz
	TMR2CN   = TMR2CN_TR2__RUN;
   TMR2L    = 0xD7;
   TMR2H    = 0xFF;
   TMR2RLL  = 0xD7;
   TMR2RLH  = 0xFF;
   
   // Interrupts
   IE = IE_EA__ENABLED | 
        IE_ET2__ENABLED;
}


