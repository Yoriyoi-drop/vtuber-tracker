#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../cpp/include/face_tracker_cpp.h"

namespace py = pybind11;

PYBIND11_MODULE(facebook_cpp_wrapper, m) {
    m.doc() = "C++ wrapper for face tracking";

    py::class_<FaceTrackingData>(m, "FaceTrackingData")
        .def(py::init<>())
        .def_readwrite("head_yaw", &FaceTrackingData::head_yaw)
        .def_readwrite("head_pitch", &FaceTrackingData::head_pitch)
        .def_readwrite("head_roll", &FaceTrackingData::head_roll)
        .def_readwrite("eye_left", &FaceTrackingData::eye_left)
        .def_readwrite("eye_right", &FaceTrackingData::eye_right)
        .def_readwrite("mouth_open", &FaceTrackingData::mouth_open)
        .def_readwrite("mouth_wide", &FaceTrackingData::mouth_wide)
        .def_readwrite("face_detected", &FaceTrackingData::face_detected);

    py::class_<FaceTrackerCpp>(m, "FaceTrackerCpp")
        .def(py::init<>())
        .def("initialize", &FaceTrackerCpp::initialize)
        .def("process_frame", &FaceTrackerCpp::process_frame)
        .def("update_sensitivity", &FaceTrackerCpp::update_sensitivity,
             py::arg("yaw_mult") = 1.0f,
             py::arg("pitch_mult") = 1.0f,
             py::arg("roll_mult") = 1.0f,
             py::arg("eye_left_mult") = 1.0f,
             py::arg("eye_right_mult") = 1.0f,
             py::arg("mouth_open_mult") = 1.0f,
             py::arg("mouth_wide_mult") = 1.0f)
        .def("update_deadzones", &FaceTrackerCpp::update_deadzones,
             py::arg("yaw_deadzone") = 0.05f,
             py::arg("pitch_deadzone") = 0.05f,
             py::arg("roll_deadzone") = 0.05f,
             py::arg("eye_left_deadzone") = 0.05f,
             py::arg("eye_right_deadzone") = 0.05f,
             py::arg("mouth_open_deadzone") = 0.05f,
             py::arg("mouth_wide_deadzone") = 0.05f)
        .def("smooth_data", &FaceTrackerCpp::smooth_data)
        .def("start_calibration", &FaceTrackerCpp::start_calibration)
        .def("is_calibrated", &FaceTrackerCpp::is_calibrated)
        .def("collect_calibration_sample", &FaceTrackerCpp::collect_calibration_sample);
}