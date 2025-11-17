#ifndef FACE_TRACKER_CPP_H
#define FACE_TRACKER_CPP_H

#include <vector>
#include <string>

// Struct untuk menyimpan data pelacakan wajah
struct FaceTrackingData {
    float head_yaw;
    float head_pitch;
    float head_roll;
    float eye_left;
    float eye_right;
    float mouth_open;
    float mouth_wide;
    bool face_detected;
};

// Class utama untuk pelacakan wajah di C++
class FaceTrackerCpp {
private:
    // Parameter pelacakan
    float head_yaw_multiplier;
    float head_pitch_multiplier;
    float head_roll_multiplier;
    float eye_left_multiplier;
    float eye_right_multiplier;
    float mouth_open_multiplier;
    float mouth_wide_multiplier;

public:
    FaceTrackerCpp();
    ~FaceTrackerCpp();

    // Inisialisasi pelacakan
    bool initialize();

    // Proses frame dan kembalikan data pelacakan
    FaceTrackingData process_frame(float* landmarks, int num_landmarks);

    // Update parameter sensitivitas
    void update_sensitivity(
        float yaw_mult = 1.0f,
        float pitch_mult = 1.0f,
        float roll_mult = 1.0f,
        float eye_left_mult = 1.0f,
        float eye_right_mult = 1.0f,
        float mouth_open_mult = 1.0f,
        float mouth_wide_mult = 1.0f
    );

    // Update deadzone
    void update_deadzones(
        float yaw_deadzone = 0.05f,
        float pitch_deadzone = 0.05f,
        float roll_deadzone = 0.05f,
        float eye_left_deadzone = 0.05f,
        float eye_right_deadzone = 0.05f,
        float mouth_open_deadzone = 0.05f,
        float mouth_wide_deadzone = 0.05f
    );

    // Fungsi smoothing gerakan
    FaceTrackingData smooth_data(const FaceTrackingData& raw_data);

    // Fungsi kalibrasi
    void start_calibration();
    bool is_calibrated() const;
    bool collect_calibration_sample(const FaceTrackingData& sample);
};

#endif // FACE_TRACKER_CPP_H