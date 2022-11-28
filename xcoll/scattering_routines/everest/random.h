#include <stdlib.h>
#include <math.h>
#include <time.h>


/*
=========================================
========  Main Random Generator  ========
=========================================
*/

unsigned int this_seed;
unsigned int n_sampled = 0;

static void set_random_seed(unsigned int seed){
    /* Intializes random number generator */
    if (seed == 0) {
        time_t t;
        this_seed = (unsigned) time(&t);
    } else {
        this_seed = seed;
    }
    srand(this_seed);
}

// TODO: This is wrong if not manually set first: it will return 0, but not sure what the default seed is..
static unsigned int get_random_seed(void){
    return this_seed;
}

static unsigned int get_n_sampled(void){
    return n_sampled;
}

// Generate a random uniform value in [0,1]
// Note that Ranlux (in old K2) generated randoms in ]0,1[
static double get_random(void){
  n_sampled = n_sampled + 1;
  double x = (double)rand()/RAND_MAX;
  return x;
}



/*
=========================================
======  Gaussian Random Generator  ======
=========================================
*/

// Generate a random value weighted within the normal (Gaussian) distribution
static double get_random_gauss(void){
  double x = get_random(),
         y = get_random(),
         z = sqrt(-2 * log(x)) * cos(2 * M_PI * y);
  return z;
}



/*
=========================================
=====  Rutherford Random Generator  =====
=========================================
*/

/*
    Iterations for Newton's method
*/
unsigned int n_iter = 25;    // good precision
//unsigned int n_iter = 7;   // bad precision but 4 times faster

static void set_rutherford_iterations(unsigned int n){
    n_iter = n;
}
static unsigned int get_rutherford_iterations(void){
    return n_iter;
}


/*
    Rutherford parameters
*/
float ruth_lower_val = 0.0009982;
float ruth_upper_val;
float ruth_A;
float ruth_B;
static double ruth_CDF(float t);
static double ruth_PDF(float t);

static void set_rutherford_parameters(float z, float emr, float upper_val){
    double c = 0.8561e3;
//     double N = 2.607e-5;
    ruth_A = pow(z,2);
    ruth_B = c*pow(emr,2);
    ruth_upper_val = upper_val;

    // Normalise PDF
    double N = ruth_CDF(ruth_upper_val);
    ruth_A = pow(z,2) / N;
}


// PDF of Rutherford distribution
static double ruth_PDF(float t){
    return (ruth_A/pow(t,2))*(exp(-ruth_B*t));
}

// CDF of Rutherford distribution
static double ruth_CDF(float t){
    return - ruth_A*ruth_B*Exponential_Integral_Ei(-ruth_B*t) - t*ruth_PDF(t)
           + ruth_A*ruth_B*Exponential_Integral_Ei(-ruth_B*ruth_lower_val) + ruth_lower_val*ruth_PDF(ruth_lower_val);
        
}

// Generate a random value weighted with a Rutherford distribution
static double get_random_ruth(void){

    // corresponding range in uniform
    // double lower_uni = 0;
//     double upper_uni = ruth_CDF(ruth_upper_val);

    // sample a random uniform
//     double t = upper_uni * get_random() ;
    double t = get_random();
    
    // initial estimate the lower border
    double x = ruth_lower_val;

    // solve CDF(x) == t for x
    unsigned short i = 1;
    while(i <= n_iter) {
        x = x - (ruth_CDF(x)-t)/ruth_PDF(x);
        i++;
    }

    return x;
}

