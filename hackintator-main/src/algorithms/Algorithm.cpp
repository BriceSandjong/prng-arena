#include "../../include/algorithms/Algorithm.hpp"
#include "../../include/interfaces/InterfaceConsole.hpp"
#include "../../include/interfaces/InterfaceSystem.hpp"


Algorithm::Algorithm(std::string configName, std::string scriptArgs, std::filesystem::path outputPath) {
    this->config = new AlgoConfig(configName, scriptArgs);

    interface = buildInterface(outputPath);

    output = new OutputReader(interface->getFileHandler(), config);
}

Algorithm::~Algorithm() {
    delete config;
    delete interface;
    delete output;
}

void Algorithm::runApp() {
    interface->run(config->getCmd().c_str());
}

void Algorithm::generateOutput(unsigned long size) {
    //TODO stop runApp when size is attained
    runApp();
}

std::string Algorithm::getNextValue() {
    return output->readNext();
}

Interface* Algorithm::buildInterface(const std::filesystem::path& outputFile) {
    std::string outputType = config->getOutput();
    bool isConsoleOutput = outputType.compare("console") == 0;
    
    if (isConsoleOutput)
        return new InterfaceConsole(outputFile.string());
    return new InterfaceSystem(outputType);
}