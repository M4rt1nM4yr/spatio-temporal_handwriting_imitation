// Always include <pybind11/pybind11.h> in the very first line of all header files and module.c
// In general, make sure that you include pybind11.h BEFORE all other header files.
#include <pybind11/pybind11.h>
namespace py = pybind11;


// Function includes, add new headers for the functions you write
#include "deblur_skeleton.h"

// Add your exposed functions here
PYBIND11_MODULE(__lib, m) {

    m.def("deblur_skeleton", &deblur_skeleton);

}
