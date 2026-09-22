#include "../include/PeriodPrinter.hpp"

void PeriodPrinter::printPeriod(std::vector<std::string> generatedNumbers, int numbersInPeriod){
  for (int i=0; i<numbersInPeriod; i++)
    std::cout << generatedNumbers[i] << std::endl;
}