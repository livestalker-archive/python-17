#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "deviceapps.pb-c.h"

#define MAGIC  0xFFFFFFFF
#define DEVICE_APPS_TYPE 1
#define DEBUG 1
#define dprint(fmt, ...) \
            do { if (DEBUG) fprintf(stderr, fmt, __VA_ARGS__); } while (0)

typedef struct pbheader_s {
    uint32_t magic;
    uint16_t type;
    uint16_t length;
} pbheader_t;
#define PBHEADER_INIT {MAGIC, 0, 0}

// fields
const char F_DEVICE[] = "device";
const char F_TYPE[]   = "type";
const char F_ID[]     = "id";
const char F_APPS[]   = "apps";
const char F_LAT[]    = "lat";
const char F_LON[]    = "lon";

// https://github.com/protobuf-c/protobuf-c/wiki/Examples
void example() {
    DeviceApps msg = DEVICE_APPS__INIT;
    DeviceApps__Device device = DEVICE_APPS__DEVICE__INIT;
    void *buf;
    unsigned len;

    char *device_id = "e7e1a50c0ec2747ca56cd9e1558c0d7c";
    char *device_type = "idfa";
    device.has_id = 1;
    device.id.data = (uint8_t*)device_id;
    device.id.len = strlen(device_id);
    device.has_type = 1;
    device.type.data = (uint8_t*)device_type;
    device.type.len = strlen(device_type);
    msg.device = &device;

    msg.has_lat = 1;
    msg.lat = 67.7835424444;
    msg.has_lon = 1;
    msg.lon = -22.8044005471;

    msg.n_apps = 3;
    msg.apps = malloc(sizeof(uint32_t) * msg.n_apps);
    msg.apps[0] = 42;
    msg.apps[1] = 43;
    msg.apps[2] = 44;
    len = device_apps__get_packed_size(&msg);

    buf = malloc(len);
    device_apps__pack(&msg, buf);

    fprintf(stderr,"Writing %d serialized bytes\n",len); // See the length of message
    fwrite(buf, len, 1, stdout); // Write to stdout to allow direct command line piping

    free(msg.apps);
    free(buf);
}

// Read iterator of Python dicts
// Pack them to DeviceApps protobuf and write to file with appropriate header
// Return number of written bytes as Python integer
static PyObject* py_deviceapps_xwrite_pb(PyObject* self, PyObject* args) {
    int ix = 0;
    const char* path;
    PyObject* o;
    PyObject *iterator;
    PyObject *item;
    PyObject *v_device;

    // Parse arguments (iterator, string)
    if (!PyArg_ParseTuple(args, "Os", &o, &path))
        return NULL;

    // Get iterator
    iterator = PyObject_GetIter(o);
    if (iterator == NULL)
        return NULL;

    // Loop through items
    while (item = PyIter_Next(iterator)) {
        // item support mapping protocol
        if (PyMapping_Check(item)) {
            process_item(item);
        }
        // item not support item protocol
        else {
            dprint("Item with index %i does not mapping object.", ix);
        }
        Py_DECREF(item);
        ix ++;
    }

    Py_DECREF(iterator);

    printf("\nWrite to: %s\n", path);
    Py_RETURN_NONE;
}

void process_item(PyObject* item) {
    //TODO if device exists
    PyObject* v_device = PyMapping_GetItemString(item, F_DEVICE);
    PyObject* v_type = PyMapping_GetItemString(v_device, F_TYPE);
    PyObject* v_id = PyMapping_GetItemString(v_device, F_ID);
    PyObject* v_apps = PyMapping_GetItemString(item, F_APPS);
    PyObject* v_lat = PyMapping_GetItemString(item, F_LAT);
    PyObject* v_lon = PyMapping_GetItemString(item, F_LON);
    pack_and_write(v_type, v_id, v_apps, v_lat, v_lon);
    Py_XDECREF(v_device);
    Py_XDECREF(v_type);
    Py_XDECREF(v_id);
    Py_XDECREF(v_apps);
    Py_XDECREF(v_lat);
    Py_XDECREF(v_lon);
    return;
}

void pack_and_write(PyObject* type, PyObject* id, PyObject* apps, PyObject* lat, PyObject* lon) {
    DeviceApps msg = DEVICE_APPS__INIT;
    DeviceApps__Device device = DEVICE_APPS__DEVICE__INIT;
    void *buf;
    unsigned len;

    char *device_id = PyString_AsString(id);
    char *device_type = PyString_AsString(type);
    dprint("\nID: %s", device_id);
    dprint("\nType: %s", device_type);
    return;
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
