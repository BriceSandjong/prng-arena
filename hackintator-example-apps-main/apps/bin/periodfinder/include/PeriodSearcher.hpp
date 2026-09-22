#pragma once

#include "../include/PeriodFinder.hpp"

#include <vector>
#include <string>

class PeriodSearcher{
  public:
    static int searchPeriod(std::vector<std::string> generatedNumbers);
};