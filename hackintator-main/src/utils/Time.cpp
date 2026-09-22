#include "../../include/utils/Time.hpp"


std::chrono::time_point<std::chrono::high_resolution_clock> getCurrentTime(){
  return std::chrono::high_resolution_clock::now();
}

std::chrono::duration<double> getExecutionTime(std::chrono::time_point<std::chrono::high_resolution_clock> start, std::chrono::time_point<std::chrono::high_resolution_clock> stop){
  return std::chrono::duration_cast<std::chrono::microseconds>(stop - start);
}