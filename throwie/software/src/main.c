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

void  sleep(void);
void  setup(void);

//-----------------------------------------------------------------------------
// Main Routine
//-----------------------------------------------------------------------------

void main (void){    
   sleep();
   while(1){
      LED = 0;
      sleep();
      LED = 1;
      sleep();
   };
}
 
//-----------------------------------------------------------------------------
// Interrupt Vectors
//-----------------------------------------------------------------------------

INTERRUPT (TIMER1_ISR, TIMER1_IRQn){
   IE = 0;
}

//-----------------------------------------------------------------------------
// Setup micro
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
		    IE_ET1__ENABLED;
   

   // Configure T1
   CKCON  = CKCON_T1M__PRESCALE|
            CKCON_SCA__SYSCLK_DIV_48;  
	TMOD   = TMOD_T1M__MODE1;	 
   TL1    = 0xF0;
   TH1    = 0xFF;
   

   // Main clock is the Low Frequency Clock 
    while(1){
      if(OSCLCN & OSCLCN_OSCLRDY__SET){
         break;
      }
   }
   CLKSEL = CLKSEL_CLKSL__LFOSC|
            CLKSEL_CLKDIV__SYSCLK_DIV_128 ;
   
   // Start T1
   TCON   = TCON_TR1__RUN;     


   // Go to sleep
   PCON = PCON_IDLE__IDLE ;
   PCON = PCON;


   // !!! Get woken up by timer
   

   // Clock
	CLKSEL   = CLKSEL_CLKSL__HFOSC |			     
              CLKSEL_CLKDIV__SYSCLK_DIV_1;

 
                                                // Enable IOs
   P1SKIP   = P1SKIP_B1__SKIPPED;
   P1MDOUT  = P1MDOUT_B1__PUSH_PULL;
   XBR2     = XBR2_WEAKPUD__PULL_UPS_DISABLED | 
              XBR2_XBARE__ENABLED;					  
}

//-----------------------------------------------------------------------------
// Setup micro
//-----------------------------------------------------------------------------

void setup(void){
   // Disabled watchdog
   WDTCN    = 0xDE;
   WDTCN    = 0xAD;
   // Clock
	CLKSEL   = CLKSEL_CLKSL__HFOSC 	      |     // Use 24.5MHz interal clock
			     CLKSEL_CLKDIV__SYSCLK_DIV_1;      // Do not divide     
   // Setup XBAR       
   P0MDOUT  = P0MDOUT_B4__PUSH_PULL;
   P1SKIP   = P1SKIP_B0__SKIPPED|
              P1SKIP_B1__SKIPPED;
   P1MDOUT  = P1MDOUT_B0__PUSH_PULL|            // LED            
              P1MDOUT_B1__PUSH_PULL;            // LED 
   XBR0     = XBR0_SMB0E__ENABLED| 
              XBR0_URT0E__ENABLED;              // Route out UART P0.4 
   XBR2     = XBR2_WEAKPUD__PULL_UPS_DISABLED | 
              XBR2_XBARE__ENABLED;					  
   // Timer control
	CKCON    = CKCON_T0M__SYSCLK|
              CKCON_SCA__SYSCLK_DIV_12;  
   // SMBus
   SMB0CF   = SMB0CF_INH__SLAVE_DISABLED|
              SMB0CF_SMBCS__TIMER0|
              SMB0CF_SMBFTE__FREE_TO_ENABLED| 
              SMB0CF_ENSMB__ENABLED; 
   // I2C clock on timer 0
   // BAUD gen 115200 on timer 1
	CKCON    |= CKCON_T1M__SYSCLK;
	TMOD     |= TMOD_T0M__MODE2 |
               TMOD_T1M__MODE2;
	TCON     |= TCON_TR0__RUN |
               TCON_TR1__RUN; 
   TH0      = 0xFE;  // I2C SCL - 333KHz (above 100KHz max for drivers datasheet)
   TL0      = 0x00;
   TH1      = 0x96;  // Magic values from datasheet for 115200
	TL1      = 0x96;
   // UART
	SCON0    |= SCON0_REN__RECEIVE_ENABLED; 
   // Timer 2
	TMR2CN   = TMR2CN_TR2__RUN;   // ~10KHz 
   TMR2L    = 0x00;
   TMR2H    = 0xFF;
   TMR2RLL  = 0x00;
   TMR2RLH  = 0xFF;
   // Timer 3
	TMR3CN   = TMR3CN_TR3__RUN;   // ~44 KHz
   TMR3L    = 0x50;
   TMR3H    = 0xFF;
   TMR3RLL  = 0x50;
   TMR3RLH  = 0xFF;
   // ADC
   ADC0MX   = ADC0MX_ADC0MX__ADC0P3;
   ADC0CF   = ADC0CF_ADGN__GAIN_1 |       // ADC gain set to 1
              ADC0CF_ADTM__TRACK_NORMAL;  // Immediate covert
   REF0CN   = REF0CN_REFSL__VDD_PIN;      // Ref to VDD
   ADC0CN0 &= ~ADC0CN0_ADCM__FMASK;
   ADC0CN0 |= ADC0CN0_ADEN__ENABLED |
              ADC0CN0_ADCM__ADBUSY; 
   // Interrupts
	IE   = IE_EA__ENABLED | 
		    IE_ET0__ENABLED|
          IE_ET1__ENABLED|
          IE_ET2__ENABLED;
   EIE1 = EIE1_ESMB0__ENABLED|
          EIE1_ET3__ENABLED;
   IP   = IP_PT2__HIGH;    
}






