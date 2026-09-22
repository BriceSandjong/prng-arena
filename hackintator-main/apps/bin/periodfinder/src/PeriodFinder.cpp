#include "../include/PeriodFinder.hpp"


bool PeriodFinder::findPeriod( const std::vector<std::string> &v, size_t n ){
  bool is_period = false;
  size_t j = 0;

  if (n < v.size()){
    while (j < v.size() - n && v[j] == v[j + n]) ++j;
    is_period = j + n == v.size();
  }

  return is_period;
}
