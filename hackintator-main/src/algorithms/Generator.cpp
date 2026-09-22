#include "../../include/algorithms/Generator.hpp"
#include "../../include/definitions/OutputPaths.hpp"


Generator::Generator(std::string configName, std::string scriptArgs) : Algorithm::Algorithm(configName, scriptArgs, GUESS_OUT_FILE) {

}

Generator::~Generator() {
  
}

OutputReader* Generator::initOutputReader() {
  return new OutputReader(interface->getFileHandler(), config);
}
