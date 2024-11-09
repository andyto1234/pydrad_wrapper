// ****
// *
// * #defines for configuring the hydrostatic model
// *
// * (c) Dr. Stephen J. Bradshaw
// *
// * Source code generated by HYDRAD_GUI on 07-04-2023 14:42:35
// *
// ****

// Boundary Conditions //
// End of Boundary Conditions //

// **** Output ****
// **** End of Output ****

// **** Physics ****
// Radiation //
#include "../../Radiation_Model/source/config.h"
// End of Radiation //
// Flux Tube //
// End of Flux Tube //
// **** End of Physics ****

// **** Solver ****
#define EPSILON 0.01
// **** End of Solver ****

// **** Grid ****
#define ADAPT
#define MIN_CELLS 60
#define MAX_CELLS 30000
#define MAX_REFINEMENT_LEVEL 10
#define INITIAL_REFINEMENT_LEVEL 10
#define MIN_DS 1e0
#define MAX_VARIATION 1.10
// **** End of Grid ****
