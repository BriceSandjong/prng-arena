cmake_minimum_required(VERSION 3.16)

project(hackintator LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

file(GLOB_RECURSE HACKINTATOR_SOURCES CONFIGURE_DEPENDS
    "${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp"
)

add_executable(hackintator ${HACKINTATOR_SOURCES})
target_include_directories(hackintator PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/include")
set_target_properties(hackintator PROPERTIES OUTPUT_NAME main)

# Keep behavior close to the Makefile by writing binaries to output/.
set_target_properties(hackintator PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/output"
    RUNTIME_OUTPUT_DIRECTORY_DEBUG "${CMAKE_CURRENT_SOURCE_DIR}/output"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_CURRENT_SOURCE_DIR}/output"
    RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${CMAKE_CURRENT_SOURCE_DIR}/output"
    RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL "${CMAKE_CURRENT_SOURCE_DIR}/output"
)

if(WIN32)
    target_link_libraries(hackintator PRIVATE psapi)
endif()
