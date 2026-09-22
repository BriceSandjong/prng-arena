#include "../include/PeriodSearcher.hpp"
#include "../include/Reader.hpp"
#include "../include/PeriodPrinter.hpp"

int main(int argc, char *argv[]) {
  Reader rd = Reader(argv[1]);
  std::vector<std::string> v = rd.getAllValuesToVector();

  PeriodPrinter::printPeriod(v, PeriodSearcher::searchPeriod(v));
}