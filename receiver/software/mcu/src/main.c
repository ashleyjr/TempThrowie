//-----------------------------------------------------------------------------
// Includes
//-----------------------------------------------------------------------------

#include "SI_C8051F850_Register_Enums.h"
#include "SI_C8051F850_Defs.h"

//-----------------------------------------------------------------------------
// Defines
//-----------------------------------------------------------------------------

#define DBG_SAMPLE
#define SAMPLES_BYTES 14 
#define SAMPLES_BITS (SAMPLES_BYTES*8)
#define PERIOD 10
SBIT(RX,       SFR_P0,  7);  
SBIT(SAMPLE,   SFR_P1,  4);  

//-----------------------------------------------------------------------------
// Global Variables
//-----------------------------------------------------------------------------
volatile U8  sample_ptr;
volatile U8  samples[SAMPLES_BYTES];
volatile U8 period_count;
volatile U8 good_count;

//-----------------------------------------------------------------------------
// Prototypes
//-----------------------------------------------------------------------------

void wrBit(U8 value, U8 pos);
U8 rdBit(U8 pos);
char receiver_pll(char i);
void uartTx(U8 tx);
void setup(void);

//-----------------------------------------------------------------------------
// Main Routine
//-----------------------------------------------------------------------------

void main (void){        
   
   sample_ptr=0;
   setup(); 
   uartTx('0');
   for(;;);
}
 
//-----------------------------------------------------------------------------
// Interrupt Vectors
//-----------------------------------------------------------------------------

INTERRUPT (TIMER2_ISR, TIMER2_IRQn){            
   U16 i;
   U8 scan_ptr_a;
   U8 scan_ptr_b;
   U8 by_a;
   U8 bt_a;
   U8 by_b;
   U8 bt_b;
   U8 edge;
   U8 found;
   // UART tx can be called directly and safely
   // in this function as the UART packet will
   // have been sent before the next timer interrupt

   // Disable all interrupts
   IE = 0;   

   if(RX){
      uartTx('1');
   }else{
      uartTx('0');
   }
   //SAMPLE=1;
   // Store sample in buffer
   //sample_ptr++;
   //sample_ptr %= SAMPLES_BITS; 
   //wrBit((U8)RX, sample_ptr);
 
   //// Scan back in buffer
   //
   //scan_ptr_a=sample_ptr;  
   //found = 1;
   //for(i=0;i<13;i++){ 
   //   if(scan_ptr_a == 0){
   //      scan_ptr_b == SAMPLES_BITS;
   //   }
   //   scan_ptr_b=scan_ptr_a-1;
   // 
   //   
   //   by_a = scan_ptr_a >> 3; // /8
   //   bt_a = scan_ptr_a - (by_a << 3); // *8
   //   by_b = scan_ptr_b >> 3; // /8
   //   bt_b = scan_ptr_b - (by_b << 3); // *8
   // 
   //   by_a = ((samples[by_a] >> bt_a) & 1);
   //   by_b = ((samples[by_b] >> bt_b) & 1);
   //   
   //   edge = by_a ^ by_b;
   //   
   //   if(edge == 0){
   //      found = 0;
   //   }
   //   
   //   if(scan_ptr_a < PERIOD){
   //      scan_ptr_a += SAMPLES_BITS;
   //   }
   //   scan_ptr_a -= PERIOD;
   //   
   //}
   //if(found){
   //   SAMPLE=1;
   //}else{
   //   SAMPLE=0; 
   //}
   //SAMPLE=0;
   


   //SAMPLE=1;

   //// Call the lock function  
   //if(locked == 1){
   //   SBUF0 = RX + '0';
   //   locked_samples++; 
   //   if(locked_samples == SAMPLE_WINDOW){ 
   //      locked_samples = 0;
   //      locked = 0; 
   //   }
   //}else{
   //   // Call the locking function 
   //   if(receiver_pll(RX) == 1){    
   //      sample <<= 1;
   //      sample |= RX; 
   //      if(sample == SAMPLE_PATTERN){  
   //         SBUF0 = '\n'; 
   //         locked = 1;  
   //      }
   //   }
   //}

   //SAMPLE=0;
   // Enable the interrupts
   TMR2CN &= ~TMR2CN_TF2H__SET;
   IE = IE_EA__ENABLED | 
        IE_ET2__ENABLED;  
} 

void wrBit(U8 value, U8 pos){
   U8 by;
   U8 bt;
   by = pos >> 3; // /8
   bt = pos - (by << 3); // *8 
   if(value){
      samples[by] = samples[by] | (1 << bt); 
   }else{
      samples[by] = samples[by] & ~(1 << bt);
   }
}

U8 rdBit(U8 pos){
   U8 by;
   U8 bt;
   by = pos >> 3; // /8
   bt = pos - (by << 3); // *8
   if((samples[by] >> bt) & 1){
      return 1; 
   }else{
      return 0; 
   }
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


