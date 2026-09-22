#include <chrono>


std::chrono::time_point<std::chrono::high_resolution_clock> getCurrentTime();

std::chrono::duration<double> getExecutionTime(std::chrono::time_point<std::chrono::high_resolution_clock> start, std::chrono::time_point<std::chrono::high_resolution_clock> stop);