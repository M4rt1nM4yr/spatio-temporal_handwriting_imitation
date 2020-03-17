#include "compute_accelerated_stroke.h"

#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <numpy/arrayobject.h>

#include <stdio.h>
#include <stdbool.h>
#include <math.h>
#include <float.h>

static inline float computeAcceleration(float x0, float y0, float x1, float y1, float x2, float y2){
    float vx0 = x1 - x0;
    float vy0 = y1 - y0;
    float vx1 = x2 - x1;
    float vy1 = y2 - y1;
    float accX = vx1 - vx0;
    float accY = vy1 - vy0;
    return sqrtf(accX * accX + accY * accY);
}

static inline float distanceToLine(float x, float y, float x1, float y1, float x2, float y2){

  float A = x - x1;
  float B = y - y1;
  float C = x2 - x1;
  float D = y2 - y1;

  float dot = A * C + B * D;
  float len_sq = C * C + D * D;
  float param = -1;
  if (len_sq != 0) //in case of 0 length line
      param = dot / len_sq;

  float xx, yy;

  if (param < 0) {
    xx = x1;
    yy = y1;
  }
  else if (param > 1) {
    xx = x2;
    yy = y2;
  }
  else {
    xx = x1 + param * C;
    yy = y1 + param * D;
  }

  float dx = x - xx;
  float dy = y - yy;
  return sqrtf(dx * dx + dy * dy);
}

static int* run4DDijkstra(int listSize, const float * points,
                          bool * reachabilityMatrix,
                          float maxAcceleration,
                          int* pathFindingResultLen)
{
    *pathFindingResultLen = 0;

    // Special case for list of size 1
    if(listSize < 2){
        int *result = PyMem_RawMalloc(sizeof(int));
        if(result == NULL)
            return (int*)PyErr_NoMemory();
        result[0] = 0;
        *pathFindingResultLen = 1;
        return result;
    }

    //printf("CCode\n");
    // Starting point can reach itself. Important, enables the starting point to be reached twice in the beginning.
    // This makes handling a zero-velocity start easier.
    reachabilityMatrix[0] = true;

    // Path will be represented as a combination of reversed list + distances, like normal dijkstra.
    // Implement memory for both of them:
    int *paths = PyMem_RawCalloc(listSize*listSize, sizeof(int));
    if(paths == NULL)
        return (int*)PyErr_NoMemory();

    int *pathLengths = PyMem_RawCalloc(listSize*listSize, sizeof(int));
    if(pathLengths == NULL){
        PyMem_RawFree(paths);
        return (int*)PyErr_NoMemory();
    }


    // Iterate through all points
    for(int currentId = 0; currentId < listSize; currentId++){
        float currentX = points[2*currentId];
        float currentY = points[2*currentId + 1];

        // For every point, compute the optimal path for all possible outgoing speeds.
        // As 'speed' we consider the vector to the next point
        for(int nextId = currentId+1; nextId < listSize; nextId++){
            // check whether point is reachable
            if(!reachabilityMatrix[currentId * listSize + nextId])
                continue;
            //printf("%d %d\n", currentId, nextId);

            float nextX = points[2*nextId];
            float nextY = points[2*nextId+1];

            // Iterate over all previous points, keep track of what the ideal path to the current point+velocity is
            int bestPreviousId = -1;
            int bestPreviousLength = -1;
            for(int previousId = 0; previousId <= currentId; previousId++){
                // check whether we can be reached from previous point
                if(!reachabilityMatrix[previousId * listSize + currentId])
                    continue;

                float previousX = points[2*previousId];
                float previousY = points[2*previousId + 1];

                float acceleration = computeAcceleration(previousX, previousY, currentX, currentY, nextX, nextY);
                //printf("    %d %f\n", previousId, acceleration);
                if(acceleration > maxAcceleration)
                    continue;

                // We have the current point and velocity and a previous point.
                // We now need to find the optimal solution that leads to the current point and velocity
                int pathLengthToPrevious = pathLengths[previousId * listSize + currentId];
                if(bestPreviousLength < 0 || bestPreviousLength > pathLengthToPrevious){
                    bestPreviousLength = pathLengthToPrevious;
                    bestPreviousId = previousId;
                }
                //printf("    %d %d\n", previousId, pathLengthToPrevious);
            }

            //printf("Best solution: %d %d\n", bestPreviousId, bestPreviousLength);

            if(bestPreviousId < 0){
                // no path to current point + velocity found, mark as unreachable
                reachabilityMatrix[currentId * listSize + nextId] = false;
            } else {
                // Path found!
                // Store information to pathLength and path
                pathLengths[currentId * listSize + nextId] = bestPreviousLength + 1;
                paths[currentId * listSize + nextId] = bestPreviousId;
            }
        }
    }

    // Pathfinding is done!
    // We now know all the paths to the last point.
    // Now iterate over the last point again to filter out the best path that can actually halt at the last point.
    int bestPenultimatePointId = -1;
    int bestPenultimatePointLength = -1;
    int lastPointId = listSize - 1;
    float lastPointX = points[2*lastPointId];
    float lastPointY = points[2*lastPointId + 1];
    for(int pointId = 0; pointId < lastPointId; pointId++){
        if(!reachabilityMatrix[pointId * listSize + lastPointId])
            continue;
        float pointX = points[2*pointId];
        float pointY = points[2*pointId + 1];

        float acceleration = computeAcceleration(pointX, pointY, lastPointX, lastPointY, lastPointX, lastPointY);
        if(acceleration > maxAcceleration)
            continue;

        int pointLength = pathLengths[pointId * listSize + lastPointId];
        if(bestPenultimatePointLength < 0 || bestPenultimatePointLength >= pointLength){
            bestPenultimatePointLength = pointLength;
            bestPenultimatePointId = pointId;
        }
    }

    // No path found. Return empty array.
    if(bestPenultimatePointId < 0){
        PyMem_RawFree(pathLengths);
        PyMem_RawFree(paths);
        return NULL;
    }

    // All done.
    // To get the path, do a reverse iteration through the 'paths' matrix.
    int bestPathLen = bestPenultimatePointLength + 1;
    int *bestPath = PyMem_RawMalloc(bestPathLen * sizeof(int));
    int currentPoint = bestPenultimatePointId;
    int nextPoint = lastPointId;
    //printf("Path: %d %d |", nextPoint, currentPoint);
    bestPath[bestPathLen-1] = lastPointId;
    bestPath[bestPathLen-2] = bestPenultimatePointId;
    for(int i = 2; i < bestPathLen; i++){
        int previousPoint = paths[currentPoint * listSize + nextPoint];
        nextPoint = currentPoint;
        currentPoint = previousPoint;
        //printf(" %d", currentPoint);
        int pos = bestPathLen - i - 1;
        bestPath[pos] = currentPoint;
        //printf(" [%d]", pos);
    }
    //printf("\n");

    // Cleanup
    PyMem_RawFree(pathLengths);
    PyMem_RawFree(paths);

    *pathFindingResultLen = bestPathLen;
    return bestPath;
}


static void computeReachabilityMatrix(int listSize, const float * points, bool* reachabilityMatrix, float deviationThreshold){

    // Disabled memset, important that reachabilityMatrix is allocated with calloc
    //memset(reachabilityMatrix, false, listSize*listSize*sizeof(bool));

    for(int pId0 = 0; pId0 < listSize; pId0++){
        float p0X = points[2*pId0];
        float p0Y = points[2*pId0 + 1];

        for(int pId1 = pId0+1; pId1 < listSize; pId1++){
            float p1X = points[2*pId1];
            float p1Y = points[2*pId1 + 1];

            float maxDeviation = 0;
            for(int pId = pId0+1; pId < pId1; pId++){
                float posX = points[2*pId];
                float posY = points[2*pId + 1];

                float deviation = distanceToLine(posX, posY, p0X, p0Y, p1X, p1Y);
                maxDeviation = fmax(deviation, maxDeviation);
            }

            if(maxDeviation > deviationThreshold)
                break;

            reachabilityMatrix[listSize * pId0 + pId1] = true;
        }
    }

}

static void capsule_cleanup(PyObject *capsule) {
    void *memory = PyCapsule_GetPointer(capsule, NULL);
    // Use your specific gc implementation in place of free if you have to
    PyMem_RawFree(memory);
}

static bool array_imported = false;

PyObject *
compute_accelerated_stroke(PyObject *self, PyObject *args){
    if(!array_imported){
        import_array();
        array_imported = true;
    }

    // TODO make argument
    float deviationThreshold;
    float maxAcceleration;

    // Parse input arguments
    PyObject *strokeObj;
    if(!PyArg_ParseTuple(args, "Off", &strokeObj, &deviationThreshold, &maxAcceleration))
        return NULL;

    // Get points object from stroke
    PyObject *pointsObj;
    pointsObj = PyObject_GetAttrString(strokeObj, "points");
    if(pointsObj == NULL)
        return NULL;

    // Check points object is indeed a list
    if(!PyList_Check(pointsObj)){
        Py_DECREF(pointsObj);
        PyErr_SetString(PyExc_TypeError, "points object is not a list");
        return NULL;
    }

    // Get size of list
    int listSize = PyList_Size(pointsObj);
    //printf("Size: %i\n", listSize);

    // Create an iterator for the points list
    PyObject *pointsIterator = PyObject_GetIter(pointsObj);
    if(pointsIterator == NULL){
        Py_DECREF(pointsObj);
        return NULL;
    }

    // Create memory to store the points in
    float* points = PyMem_RawMalloc(sizeof(float) * 2*listSize);
    if(points == NULL){
        Py_DECREF(pointsIterator);
        Py_DECREF(pointsObj);
        return PyErr_NoMemory();
    }

    // Iterate over the points
    PyObject *pointsItem;
    size_t pos = 0;
    while((pointsItem = PyIter_Next(pointsIterator))){
        PyArrayObject *posObj;
        posObj = (PyArrayObject*)PyObject_GetAttrString(pointsItem, "pos");

        bool hasError = false;
        if(posObj == NULL){
            hasError = true;
        } else if(PyArray_NDIM(posObj) != 1){
            PyErr_SetString(PyExc_TypeError, "pos object has more than one dimension");
            hasError = true;
        } else if(PyArray_DIM(posObj, 0) != 2){
            PyErr_SetString(PyExc_TypeError, "pos object has more than two elements");
            hasError = true;
        } else if(PyArray_DTYPE(posObj)->type != 'd' && PyArray_DTYPE(posObj)->type != 'f'){
            PyErr_SetString(PyExc_TypeError, "pos object does not contain doubles or floats");
            hasError = true;
        }

        if(hasError){
            Py_DECREF(posObj);
            Py_DECREF(pointsItem);
            Py_DECREF(pointsIterator);
            Py_DECREF(pointsObj);
            PyMem_RawFree(points);
            return NULL;
        }


        float xPos, yPos;
        if(PyArray_DTYPE(posObj)->type == 'd'){
            double *xPosPtr;
            double *yPosPtr;
            xPosPtr = PyArray_GETPTR1(posObj, 0);
            yPosPtr = PyArray_GETPTR1(posObj, 1);
            xPos = (float)*xPosPtr;
            yPos = (float)*yPosPtr;
        } else {
            float *xPosPtr;
            float *yPosPtr;
            xPosPtr = PyArray_GETPTR1(posObj, 0);
            yPosPtr = PyArray_GETPTR1(posObj, 1);
            xPos = *xPosPtr;
            yPos = *yPosPtr;
        }

        points[pos++] = xPos;
        points[pos++] = yPos;

        Py_DECREF(posObj);
        Py_DECREF(pointsItem);
    }

    // Free iterator and check for errors
    Py_DECREF(pointsIterator);
    Py_DECREF(pointsObj);

    if (PyErr_Occurred()) {
        PyMem_RawFree(points);
        return NULL;
    }

    // Initialize reachability matrix
    bool *reachabilityMatrix = PyMem_RawCalloc(listSize * listSize, sizeof(bool));
    if(reachabilityMatrix == NULL){
        PyMem_RawFree(points);
        return PyErr_NoMemory();
    }

    // Compute reachability matrix
    computeReachabilityMatrix(listSize, points, reachabilityMatrix, deviationThreshold);

    // Compute shortest path
    int pathFindingResultLen = 0;
    int* pathFindingResult = run4DDijkstra(listSize, points, reachabilityMatrix, maxAcceleration, &pathFindingResultLen);
    //PyMem_RawFree(pathFindingResult);

    // Cleanup
    PyMem_RawFree(reachabilityMatrix);
    PyMem_RawFree(points);

    // Hand over result to numpy
    int nd = 1;
    npy_intp dims[] = {pathFindingResultLen};
    PyObject* arr = PyArray_SimpleNewFromData(nd, dims, NPY_INT, (void *)pathFindingResult);
    PyObject *capsule = PyCapsule_New(pathFindingResult, NULL, capsule_cleanup);
    // NULL can be a string but use the same string while calling PyCapsule_GetPointer inside capsule_cleanup
    PyArray_SetBaseObject((PyArrayObject *) arr, capsule);

    return arr;
    //Py_RETURN_NONE;
}
