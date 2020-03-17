#pragma once


// Always include <pybind11/pybind11.h> in the very first line of all header files and module.cpp
// In general, make sure that you include pybind11.h BEFORE all other header files.
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
namespace py = pybind11;



py::array_t<float> deblur_skeleton(const py::array_t<float> &img, const py::array_t<float> &filter);
