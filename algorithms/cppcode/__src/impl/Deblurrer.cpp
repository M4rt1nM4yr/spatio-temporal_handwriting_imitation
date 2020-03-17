#include "Deblurrer.h"

#include <iostream>
#include <algorithm>


static inline float& at(float* array, ssize_t x, ssize_t y, const ssize_t strideX, const ssize_t strideY){
    uint8_t* arrayPtr = reinterpret_cast<uint8_t*>(array);
    ssize_t offset = x * strideX + y * strideY;
    float* resultPtr = reinterpret_cast<float*>(arrayPtr + offset);
    return *resultPtr;
}

static inline const float& at(const float* array, ssize_t x, ssize_t y, const ssize_t strideX, const ssize_t strideY){
    const uint8_t* arrayPtr = reinterpret_cast<const uint8_t*>(array);
    ssize_t offset = x * strideX + y * strideY;
    const float* resultPtr = reinterpret_cast<const float*>(arrayPtr + offset);
    return *resultPtr;
}

static inline uint8_t& at(uint8_t* array, ssize_t x, ssize_t y, const ssize_t strideX, const ssize_t strideY){
    ssize_t offset = x * strideX + y * strideY;
    uint8_t* resultPtr = array + offset;
    return *resultPtr;
}

static inline const uint8_t& at(const uint8_t* array, ssize_t x, ssize_t y, const ssize_t strideX, const ssize_t strideY){
    ssize_t offset = x * strideX + y * strideY;
    const uint8_t* resultPtr = array + offset;
    return *resultPtr;
}


Deblurrer::Deblurrer(const py::array_t<float> &img, const py::array_t<float> &filterArray)
: blurImgArray({img.shape(0), img.shape(1)}),
  outputImageArray({img.shape(0), img.shape(1)}),
  inputImage(img.data()),
  outputImage(outputImageArray.mutable_data()),
  blurImg(blurImgArray.mutable_data()),
  filter(filterArray.data()),
  sizeX(img.shape(1)),
  sizeY(img.shape(0)),
  inputStrideX(img.strides(1)),
  inputStrideY(img.strides(0)),
  outputStrideX(outputImageArray.strides(1)),
  outputStrideY(outputImageArray.strides(0)),
  blurImgStrideX(blurImgArray.strides(1)),
  blurImgStrideY(blurImgArray.strides(0)),
  filterSizeX(filterArray.shape(1)),
  filterSizeY(filterArray.shape(0)),
  filterStrideX(filterArray.strides(1)),
  filterStrideY(filterArray.strides(0)),
  debugImgArray({img.shape(0), img.shape(1)}),
  debugImg(debugImgArray.mutable_data()),
  debugImgStrideX(debugImgArray.strides(1)),
  debugImgStrideY(debugImgArray.strides(0))
{
    /*std::cout << "Deblurrer()" << std::endl;
    std::cout << sizeX << " " << sizeY << std::endl;
    std::cout << inputStrideX << " " << inputStrideY << std::endl;
    std::cout << outputStrideX << " " << outputStrideY << std::endl;
    std::cout << blurImgStrideX << " " << blurImgStrideY << std::endl;
    std::cout << filterSizeX << " " << filterSizeY << std::endl;
    std::cout << filterStrideX << " " << filterStrideY << std::endl;*/
}

py::array_t<float> Deblurrer::takeResult(){
    return std::move(debugImgArray);
}

// This does the actual filter work.
// It does border checking and calls the 'func' argument for every valid filter position around (x,y).
void Deblurrer::runFilter(ssize_t x, ssize_t y, std::function<void(ssize_t, ssize_t, ssize_t, ssize_t)> func){
    ssize_t filterOffsetX = (filterSizeX-1)/2;
    ssize_t filterOffsetY = (filterSizeY-1)/2;

    ssize_t x_min = x-filterOffsetX;
    ssize_t y_min = y-filterOffsetY;
    ssize_t x_max = x-filterOffsetX + filterSizeX;
    ssize_t y_max = y-filterOffsetY + filterSizeY;

    x_min = std::max(x_min, ssize_t(0));
    y_min = std::max(y_min, ssize_t(0));
    x_max = std::min(x_max, sizeX);
    y_max = std::min(y_max, sizeY);

    for(ssize_t imgY = y_min; imgY < y_max; imgY++){
        ssize_t filterY = imgY - y + filterOffsetY;
        for(ssize_t imgX = x_min; imgX < x_max; imgX++){
            ssize_t filterX = imgX - x + filterOffsetX;
            func(imgX, imgY, filterX, filterY);
        }
    }
}

void Deblurrer::initialize_outputImage(){
    for(int y = 0; y < sizeY; y++){
        for(int x = 0; x < sizeX; x++){
            //bool isBackground = (at(inputImage, x, y, inputStrideX, inputStrideY) < (90.0f/255.0f));
            //at(outputImage, x, y, outputStrideX, outputStrideY) = isBackground ? 0 : 1;
            at(outputImage, x, y, outputStrideX, outputStrideY) = 0;
        }
    }
}

void Deblurrer::update_blurImg(ssize_t x, ssize_t y){
    float pixelResult = 0.0;
    runFilter(x,y,[this,&pixelResult](ssize_t imgX, ssize_t imgY, ssize_t filterX, ssize_t filterY){
        uint8_t imgValue = at(outputImage, imgX, imgY, outputStrideX, outputStrideY);
        float filterValue = at(filter, filterX, filterY, filterStrideX, filterStrideY);
        pixelResult += imgValue * filterValue;
    });
    at(blurImg, x, y, blurImgStrideX, blurImgStrideY) = pixelResult;
}

void Deblurrer::initialize_blurImage(){
    for(int y = 0; y < sizeY; y++){
        for(int x = 0; x < sizeX; x++){
            update_blurImg(x,y);
        }
    }
}

void Deblurrer::flipPixel(ssize_t x, ssize_t y){
    // Flip
    at(outputImage, x, y, outputStrideX, outputStrideY) = 1 - at(outputImage, x, y, outputStrideX, outputStrideY);

    // Update surrounding pixels in blurImg
    runFilter(x,y,[this](ssize_t imgX, ssize_t imgY, ssize_t, ssize_t){
        update_blurImg(imgX, imgY);
    });
}

float Deblurrer::computeFlipGain(ssize_t x, ssize_t y){

    float resultWithout = 0.0f;
    float resultWith = 0.0f;

    uint8_t currentPixelState = at(outputImage, x, y, outputStrideX, outputStrideY);

    // if we have a pixel at output image, compute what would happen if we remove it.
    // otherwise, compute what would happen if we add one.
    float sign = 1.0f;
    if (currentPixelState != 0)
        sign = -1.0f;

    runFilter(x,y,[this,sign,&resultWith,&resultWithout](ssize_t imgX, ssize_t imgY, ssize_t filterX, ssize_t filterY){
        float inputValue = at(inputImage, imgX, imgY, inputStrideX, inputStrideY);
        float currentValue = at(blurImg, imgX, imgY, blurImgStrideX, blurImgStrideY);
        float newValue = currentValue + sign * at(filter, filterX, filterY, filterStrideX, filterStrideY);
        resultWith += std::abs(newValue-inputValue);
        resultWithout += std::abs(currentValue-inputValue);
    });

    float improvement = resultWithout - resultWith;

    return improvement;
}

void Deblurrer::run(){
    // Initialize the output image to an empty image
    initialize_outputImage();

    // Creates a blurred version of the output image. This is necessary for performance reasons.
    initialize_blurImage();

    ssize_t lastStrongestPixelX = -1;
    ssize_t lastStrongestPixelY = -1;
    while(true){
        ssize_t strongestPixelX = -1;
        ssize_t strongestPixelY = -1;
        float strongestPixel = -1.0f;
        for(int y = 0; y < sizeY; y++){
            for(int x = 0; x < sizeX; x++){

                float improvement = computeFlipGain(x,y);

                if(improvement > 0){
                    at(debugImg, x, y, debugImgStrideX, debugImgStrideY) = improvement;
                    if(improvement > strongestPixel){
                        strongestPixel = improvement;
                        strongestPixelX = x;
                        strongestPixelY = y;
                    }
                } else {
                    at(debugImg, x, y, debugImgStrideX, debugImgStrideY) = 0;
                }
            }
        }

        std::cout << "Strongest pixel: " << strongestPixelX << ", " << strongestPixelY << "   " << strongestPixel << std::endl;
        if(strongestPixelX < 0 || strongestPixelY < 0 || (strongestPixelX == lastStrongestPixelX && strongestPixelY == lastStrongestPixelY))
            break;
        flipPixel(strongestPixelX, strongestPixelY);
        lastStrongestPixelX = strongestPixelX;
        lastStrongestPixelY = strongestPixelY;

    }

    for(int y = 0; y < sizeY; y++){
        for(int x = 0; x < sizeX; x++){
            at(debugImg, x, y, debugImgStrideX, debugImgStrideY) = at(outputImage, x, y, outputStrideX, outputStrideY);
        }
    }

}
