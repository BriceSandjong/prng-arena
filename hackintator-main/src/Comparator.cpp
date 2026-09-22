#include "../include/Comparator.hpp"
#include "../include/utils/Hardware.hpp"
#include <iostream>
#include <thread>
#include "../include/utils/Time.hpp"


Comparator::Comparator(Generator* a, Guesser* b, unsigned long nbIteration, size_t inputSize, std::string command) {
  this->a = a;
  this->b = b;
  this->nbIteration = nbIteration;
  this->csvFile = new FileHandler("output/results.csv");
  this->csvFile->wipe();
  this->command = command;

  try { 
    initCPU();
  } catch (std::system_error const&){
    std::cout << "Unable to init CPU" << std::endl;
  }

  a->generateOutput(nbIteration);
  b->initInputSource(inputSize); //optionnal. Size may vary, but must check that it is smaller than nbIteration
  b->generateOutput(nbIteration);
}

Comparator::~Comparator() {

}

void Comparator::execute() {
  double nbMatches = 0;
  double ratio = 0;
  std::chrono::time_point<std::chrono::high_resolution_clock> start = getCurrentTime();

  runRatioPrinter(&ratio);
  csvFile->write(command + "\n");

  for (unsigned long i = 0; i < nbIteration; i++) {
    bool isMatch = isCorrectGuess();
    nbMatches += isMatch;

    ratio = nbMatches/(i+1);
  }
  csvFile->writeToNextLine(std::to_string(ratio) + ';');
  ratio = -1;

  csvFile->writeToNextLine(std::to_string(getExecutionTime(start, getCurrentTime()).count()) + ';');
  try {
    csvFile->writeToNextLine(std::to_string(getCPUUsage()));
    csvFile->writeToNextLine(std::to_string(getPhysicalMemoryUsage()));
  } catch (std::system_error const&){
    std::cout << "Unable to write hardware values" << std::endl;
  }
  
  delete csvFile;
}

bool Comparator::isCorrectGuess() {
  std::string actual = a->getNextValue();
  std::string guessed = b->getNextValue();
  csvFile->write(actual + ';' + guessed + ';');

  return actual.compare(guessed) == 0;
}

void Comparator::runRatioPrinter(double* ratio) {
  std::thread thread([](double* ratio, int delay) {
    while (*ratio != -1) {
      std::this_thread::sleep_for(std::chrono::seconds(delay));
      std::cout << "Match Ratio: " << *ratio << std::endl;
    }
  }, ratio, getPrinterDelay());
  
  thread.detach();  
}

int Comparator::getPrinterDelay() {
  ConfigReader* configReader = new ConfigReader("app_conf.ini");
  int delay = std::stoi(configReader->getParameter("Chrono"));
  return delay == 0 ? 1 : delay;
}