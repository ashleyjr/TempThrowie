#define TIMESTEP_S   1e-5
#define CUT_OFF_HZ   20
#define RC           (1 / (2 * 3.1415 * CUT_OFF_HZ))
#define ALPHA        (float)(TIMESTEP_S / (RC + TIMESTEP_S))
#define BETA         (float)(1 - ALPHA)
#define PID_P        4000
#define PID_I        3

static float cycle;

static char p1_ref;
static char p1_vco;
static char up;
static char dn;

static float p0_lpf; 
static float p1_lpf;

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
   float period_s;
   float phase; 

   // Update the VCO first 
   period_s = (1/(1+pid_y)); 
   cycle += TIMESTEP_S;
   if(cycle > period_s){
      cycle = 0;
   }
   if(cycle > (period_s/2)){
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
   if(up == dn){
      phase = 0;
   } else {
      if(up == 1){
         phase = 1;
      }else{
         phase = -1;
      }
   } 
   p1_ref = p0_ref;
   p1_vco = p0_vco;

   // Low Pass Filter 
   p0_lpf = (ALPHA * phase) + (BETA * p1_lpf);
   p1_lpf = p0_lpf;
 
   // PID Control
   integral += ((p0_lpf + p1_pid_x) / 2); 
   pid_y = (p0_lpf *  PID_P) + (integral * PID_I);
   p1_pid_x = p0_lpf;
     
   return p0_vco;
}
