#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <zlib.h>
#include "deviceapps.pb-c.h"

#define MAGIC  0xFFFFFFFF
#define DEVICE_APPS_TYPE 1
#define DEBUG 1
#define dprintp(fmt) \
            do { if (DEBUG) fprintf(stderr, fmt); } while (0)
#define dprint(fmt, ...) \
            do { if (DEBUG) fprintf(stderr, fmt, __VA_ARGS__); } while (0)

typedef struct pbheader_s {
    uint32_t magic;
    uint16_t type;
    uint16_t length;
} pbheader_t;

typedef struct datapkg_s {
    char* type;
    char* id;
    int count;
    long* apps;
    float* lat;
    float* lon;
    gzFile out_file;
} datapkg_t;

#define PBHEADER_INIT {MAGIC, 0, 0}

// functions
int process_item(PyObject*, gzFile);
int pack_and_write(datapkg_t dp);

// fields
char const * F_DEVICE = "device";
char const * F_TYPE   = "type";
char const * F_ID     = "id";
char const * F_APPS   = "apps";
char const * F_LAT    = "lat";
char const * F_LON    = "lon";

// Read iterator of Python dicts
// Pack them to DeviceApps protobuf and write to file with appropriate header
// Return number of written bytes as Python integer
static PyObject* py_deviceapps_xwrite_pb(PyObject* self, PyObject* args) {
    int ix = 0;
    int written = 0;
    const char* path;
    PyObject* o;
    PyObject *iterator;
    PyObject *item;
    gzFile out_file;

    // Parse arguments (iterator, string)
    if (!PyArg_ParseTuple(args, "Os", &o, &path))
        return NULL;

    // Get iterator
    iterator = PyObject_GetIter(o);
    if (iterator == NULL)
        return NULL;
    out_file = gzopen(path, "wb");
    if (out_file == NULL){
        PyErr_SetString(PyExc_IOError, "Cannot open a file");
        Py_DECREF(iterator);
	    return NULL;
    }
    // Loop through items
    while ((item = PyIter_Next(iterator))) {
        // item support mapping protocol
        if (PyMapping_Check(item)) {
            written += process_item(item, out_file);
        }
        // item not support item protocol
        else {
            dprint("Item with index %i does not mapping object.", ix);
            PyErr_SetString(PyExc_ValueError, "The deviceapps type must be a dictionary");
        }
        Py_DECREF(item);
        ix++;
    }

    Py_DECREF(iterator);

    gzclose(out_file);
    if (PyErr_Occurred()) {
        return NULL;
    }
    return Py_BuildValue("i", written);
}

int process_item(PyObject* item, gzFile out_file) {
    PyObject *v_device, *v_type, *v_id, *v_apps, *v_lat, *v_lon;
    unsigned written = 0;
    int i = 0;
    datapkg_t dp = {NULL, NULL, 0, NULL, NULL, NULL, out_file};
    v_device = PyMapping_GetItemString(item, F_DEVICE);
    if (v_device != NULL) {
        v_type = PyMapping_GetItemString(v_device, F_TYPE);
        v_id = PyMapping_GetItemString(v_device, F_ID);
        dp.type = PyString_AsString(v_type);
        dp.id = PyString_AsString(v_id);
    }
    v_apps = PyMapping_GetItemString(item, F_APPS);
    if (v_apps && PySequence_Check(v_apps)) {
        dp.count = PySequence_Size(v_apps);
        dp.apps = malloc(sizeof(long) * dp.count);
        for (i = 0; i < dp.count; i++) {
            PyObject *id_app = PyList_GET_ITEM(v_apps, i);
            dp.apps[i] = PyInt_AsLong(id_app);
        }
    }

    if (PyMapping_HasKeyString(item, F_LON)) {
        v_lat = PyMapping_GetItemString(item, F_LAT);
        if (v_lat && PyNumber_Check(v_lat)) {
            dp.lat = (float* )malloc(sizeof(float));
            *dp.lat = PyFloat_AsDouble(v_lat);
        }
    }

    if (PyMapping_HasKeyString(item, F_LON)) {
        v_lon = PyMapping_GetItemString(item, F_LON);
        if (v_lon && PyNumber_Check(v_lon)) {
            dp.lon = (float* )malloc(sizeof(float));
            *(dp.lon) = PyFloat_AsDouble(v_lon);
        }
    }
    written = pack_and_write(dp);
    if (dp.lat) free(dp.lat);
    if (dp.lon) free(dp.lon);
    if (dp.apps) free(dp.apps);
    return written;
}

int pack_and_write(datapkg_t dp) {
    DeviceApps msg = DEVICE_APPS__INIT;
    DeviceApps__Device device = DEVICE_APPS__DEVICE__INIT;
    void *buf;
    unsigned len;
    int i = 0;

    // Debug info
    dprint("\nID: %s\n", dp.id);
    dprint("Type: %s\n", dp.type);
    dprint("Apps count: %i\n", dp.count);
    dprintp("Apps ids: ");
    for (i = 0; i < dp.count; i++)
        dprint("%li ", dp.apps[i]);
    dprintp("\n");
    if (dp.lat) dprint("lat: %.4f\n", *(dp.lat));
    if (dp.lon) dprint("lon: %.4f\n", *(dp.lon));

    if (dp.type && dp.id) {
        device.has_id = 1;
        device.id.data = (uint8_t*)dp.id;
        device.id.len = strlen(dp.id);
        device.has_type = 1;
        device.type.data = (uint8_t*)dp.type;
        device.type.len = strlen(dp.type);
        msg.device = &device;
    }

    if (dp.lat) {
        msg.has_lat = 1;
        msg.lat = *(dp.lat);
    }

    if (dp.lon) {
       msg.has_lon = 1;
       msg.lon = *(dp.lon);
    }

    msg.n_apps = dp.count;
    msg.apps = malloc(sizeof(uint32_t) * msg.n_apps);
    for (i = 0; i < dp.count; i++) {
        msg.apps[i] = dp.apps[i];
    }
    len = device_apps__get_packed_size(&msg);

    buf = malloc(len);
    device_apps__pack(&msg, buf);

    // write header
    pbheader_t header = {0, 0, 0};
    header.magic = MAGIC;
    header.type = DEVICE_APPS_TYPE;
    header.length = len;
    gzwrite(dp.out_file, &header, sizeof(pbheader_t));

    // write message
    dprint("Writing %d serialized bytes\n",len);
    gzwrite(dp.out_file, buf, len);

    free(msg.apps);
    free(buf);
    return sizeof(pbheader_t) + len;
}

// Unpack only messages with type == DEVICE_APPS_TYPE
// Return iterator of Python dicts
static PyObject* py_deviceapps_xread_pb(PyObject* self, PyObject* args) {
    const char* path;

    if (!PyArg_ParseTuple(args, "s", &path))
        return NULL;

    printf("Read from: %s\n", path);
    Py_RETURN_NONE;
}


static PyMethodDef PBMethods[] = {
     {"deviceapps_xwrite_pb", py_deviceapps_xwrite_pb, METH_VARARGS, "Write serialized protobuf to file fro iterator"},
     {"deviceapps_xread_pb", py_deviceapps_xread_pb, METH_VARARGS, "Deserialize protobuf from file, return iterator"},
     {NULL, NULL, 0, NULL}
};


PyMODINIT_FUNC initpb(void) {
     (void) Py_InitModule("pb", PBMethods);
}
