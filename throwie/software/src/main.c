//-----------------------------------------------------------------------------
// Includes
//-----------------------------------------------------------------------------

#include "SI_C8051F850_Register_Enums.h"
#include "SI_C8051F850_Defs.h"

//-----------------------------------------------------------------------------
// Defines
//-----------------------------------------------------------------------------

SBIT(LED,  SFR_P1, 1);  

//-----------------------------------------------------------------------------
// Prototypes
//-----------------------------------------------------------------------------

void uartTx(U8 tx);
void sleep(void);

//-----------------------------------------------------------------------------
// Main Routine
//-----------------------------------------------------------------------------

void main (void){     
   while(1){
      sleep();
      LED = 1;
      uartTx('A');
      sleep();
      LED = 0;
      uartTx('A');
   };
}
 
//-----------------------------------------------------------------------------
// Interrupt Vectors
//-----------------------------------------------------------------------------

INTERRUPT (TIMER0_ISR, TIMER0_IRQn){
   IE = 0;
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
   P0MDOUT  = P0MDOUT_B4__PUSH_PULL;
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
  
   // Interrupts
   IE = IE_EA__ENABLED;
}


