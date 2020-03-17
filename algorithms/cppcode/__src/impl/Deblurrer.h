#pragma once

// Always include <pybind11/pybind11.h> in the very first line of all header files and module.cpp
// In general, make sure that you include pybind11.h BEFORE all other header files.
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
namespace py = pybind11;

class Deblurrer{

    public:
        Deblurrer(const py::array_t<float> &img, const py::array_t<float> &filterArray);

        void run();
        py::array_t<float> takeResult();

    private:
        void initialize_outputImage();
        void initialize_blurImage();
        void runFilter(ssize_t x, ssize_t y, std::function<void(ssize_t, ssize_t, ssize_t, ssize_t)>);
        void flipPixel(ssize_t x, ssize_t y);
        void update_blurImg(ssize_t x, ssize_t y);
        float computeFlipGain(ssize_t x, ssize_t y);

    private:
        py::array_t<float> blurImgArray;
        py::array_t<uint8_t> outputImageArray;

        // The input image
        const float* inputImage;
        // The binary output image
        uint8_t* outputImage;
        // The blurred verison of the output image, for performance reasons
        float* blurImg;
        // The filter kernel
        const float* filter;

        const ssize_t sizeX, sizeY;
        const ssize_t inputStrideX, inputStrideY;
        const ssize_t outputStrideX, outputStrideY;
        const ssize_t blurImgStrideX, blurImgStrideY;

        const ssize_t filterSizeX, filterSizeY;
        const ssize_t filterStrideX, filterStrideY;

        // TODO remove
        py::array_t<float> debugImgArray;
        float* debugImg;
        const ssize_t debugImgStrideX, debugImgStrideY;
};
