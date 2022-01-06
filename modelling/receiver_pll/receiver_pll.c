#define TIMESTEP_S   (float)1e-4
#define SCALE_PWR    20
#define SCALE        (long)((long)1 << (SCALE_PWR)) 
#define TIMESTEP     (long)(TIMESTEP_S * SCALE)
#define CUT_OFF_HZ   (float)20
#define RC           (1 / (2 * 3.1415 * CUT_OFF_HZ))
#define ALPHA        (float)(TIMESTEP_S / (RC + TIMESTEP_S))
#define BETA         (float)(1 - ALPHA)
#define ALPHA_SCALE  (long)(ALPHA * SCALE)
#define BETA_SCALE   (long)(BETA * SCALE) 
#define TGT_HZ       1000
#define PERIOD_S     (short)(SCALE / TGT_HZ)
#define PERIOD_S_2   (short)(PERIOD_S / 2)

// DATA TYPES
// -  SDCC 
//    - short  - 16 bits
//    - int    - 16 bits
//    - long   - 32 bits
// - GCC
//    - short  - 16 bits
//    - int    - 32 bits
//    - long   - 32 bits

static unsigned long cycle;

static char p1_ref;
static char p0_vco;
static char p1_vco;
static char up;
static char dn;

static long p0_lpf; 
static long p1_lpf;
static long lpf;

static long pid_y;

void receiver_pll_init(void) { 
   cycle    = 0;       
   p1_ref   = 0; 
   p1_vco   = 0;
   up       = 0;
   dn       = 0;  
   p0_lpf   = 0; 
   p1_lpf   = 0;       
   pid_y    = 0;   
   p0_vco   = 0;
}

char receiver_pll(char p0_ref) {
   
   // Phase Detector
   if((p0_ref == 1) &&
      (p1_ref == 0)){
      up = 1;         
   }
   if((p0_vco == 1) &&
      (p1_vco == 0)){
      dn = 1;         
   }
   if((up == 1) && 
      (dn == 1)){
      up = 0;
      dn = 0;
   }
   p1_ref = p0_ref;
   p1_vco = p0_vco;

   // Low Pass Filter 
   //    - Phase output is in [-1, 0, 1]
   //      so simplfy out multiply
   
   // Phase = 0
   p0_lpf = (BETA * p1_lpf);
   if(up != dn){
      if(up == 1){
         // Phase = 1
         p0_lpf += ALPHA_SCALE;
      }else{
         // Phase = -1
         p0_lpf -= ALPHA_SCALE;
      }
   } 
   p1_lpf = p0_lpf;
   
   // PID Control 
   pid_y = p0_lpf >> 13;  
    
   // Update the PCO 
   cycle += pid_y;
   cycle += TIMESTEP;
   if(cycle > PERIOD_S){
      cycle = 0;
   }
   if(cycle > PERIOD_S_2){
      p0_vco = 1;
   }else{
      p0_vco = 0;
   }  
   return p0_vco;
}
