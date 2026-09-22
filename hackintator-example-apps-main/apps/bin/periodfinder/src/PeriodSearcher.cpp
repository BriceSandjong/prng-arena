#include "../include/PeriodSearcher.hpp"

int PeriodSearcher::searchPeriod(std::vector<std::string> generatedNumbers){
  for (size_t i=1; i<generatedNumbers.size();i++)
    if (PeriodFinder::findPeriod( generatedNumbers, i )) 
      return i;

  return generatedNumbers.size();
}