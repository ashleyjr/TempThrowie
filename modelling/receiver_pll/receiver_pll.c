#define TIMESTEP_S   1e-4
#define SCALE        1e6 
#define TIMESTEP     TIMESTEP_S * SCALE
#define CUT_OFF_HZ   10
#define RC           (1 / (2 * 3.1415 * CUT_OFF_HZ))
#define ALPHA        (float)(TIMESTEP_S / (RC + TIMESTEP_S))
#define BETA         (float)(1 - ALPHA)
#define ALPHA_SCALE  (int)(ALPHA * SCALE)
#define BETA_SCALE   (int)(BETA * SCALE) 
#define PID_P        5000
#define PID_I        50

static int cycle;

static char p1_ref;
static char p1_vco;
static char up;
static char dn;

static int p0_lpf; 
static int p1_lpf;
static float lpf;

static float p0_pid_x; 
static float p1_pid_x;
static float integral;
static float pid_y;

void receiver_pll_init(void) { 
   cycle    = 0;       
   p1_ref   = 0; 
   p1_vco   = 0;
   up       = 0;
   dn       = 0;  
   p0_lpf   = 0; 
   p1_lpf   = 0;      
   p0_pid_x = 0; 
   p1_pid_x = 0;
   integral = 0;
   pid_y    = 0;    
}

int receiver_pll(char p0_ref) {
   char  p0_vco;
   int period_s; 

   // Update the VCO first 
   period_s = (SCALE/(1+pid_y)); 
   cycle += TIMESTEP;
   if(cycle > period_s){
      cycle = 0;
   }
   if(cycle > (period_s >> 1)){
      p0_vco = 1;
   }else{
      p0_vco = 0;
   }

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
   lpf = (float)p0_lpf / (float)SCALE;
   
   // PID Control
   integral += ((lpf + p1_pid_x) / 2); 
   pid_y = (lpf *  PID_P) + (integral * PID_I);
   p1_pid_x = lpf;
     
   return p0_vco;
}
