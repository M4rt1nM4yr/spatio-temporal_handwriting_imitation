// In all C++ files, include its corresponding header file in the very first line.
// No need to include <pybind11.h> as we did that already in the header file.
// Just make sure that <pybind11.h> is included BEFORE any other header file.
#include "deblur_skeleton.h"

#include <iostream>

#include "impl/Deblurrer.h"


py::array_t<float> deblur_skeleton(const py::array_t<float> &img, const py::array_t<float> &filter){

    Deblurrer deblurrer(img, filter);
    deblurrer.run();
    return deblurrer.takeResult();

}
