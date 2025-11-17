cmake_minimum_required(VERSION 3.12)
project(VTuberTrackerCpp)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(PkgConfig REQUIRED)
find_package(OpenCV REQUIRED)
find_package(pybind11 REQUIRED)

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)
include_directories(${OpenCV_INCLUDE_DIRS})

# Source files
set(SOURCES
    src/face_tracker_cpp.cpp
)

# Create library
add_library(facebook_cpp SHARED ${SOURCES})
target_include_directories(facebook_cpp PRIVATE include)

# Link libraries
target_link_libraries(facebook_cpp ${OpenCV_LIBS})

# Create Python binding
pybind11_add_module(facebook_cpp_wrapper src/python_wrapper.cpp)
target_link_libraries(facebook_cpp_wrapper PRIVATE facebook_cpp)

# Export library
set_target_properties(facebook_cpp PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)

# Install rules
install(TARGETS facebook_cpp
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)

install(DIRECTORY include/
    DESTINATION include
    FILES_MATCHING PATTERN "*.h"
)