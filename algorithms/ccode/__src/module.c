// Always include Python.h in the very first line of all header files and module.c
// In general, make sure that you include Python.h BEFORE all other header files.
#include <Python.h>


////////////////////////////////////////
// Modify this part

// Function includes, add new headers for the functions you write
#include "compute_accelerated_stroke.h"

// Add functions to the external interface of the compiled library.
static PyMethodDef methods[] = {
    {"compute_accelerated_stroke", compute_accelerated_stroke, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

//
////////////////////////////////////////




// The module definition.
// Most likely doesn't need to get modified when writing new functions.
static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "__lib",     /* name of module. Do not change. */
    NULL,      /* module documentation, may be NULL */
    -1,        /* size of per-interpreter state of the module,
                  or -1 if the module keeps state in global variables. */
    methods
};

// The module init function.
PyMODINIT_FUNC
PyInit___lib(void)
{
    return PyModule_Create(&module);
}

