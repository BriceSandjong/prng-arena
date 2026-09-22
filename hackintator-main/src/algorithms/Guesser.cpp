#include "../../include/algorithms/Guesser.hpp"
#include "../../include/definitions/OutputPaths.hpp"
#include "../../include/definitions/Placeholders.hpp"
#include "../../include/utils/String.hpp"


Guesser::Guesser(OutputReader* input, std::string configName, std::string scriptArgs) : Algorithm::Algorithm(configName, scriptArgs, GEN_OUT_FILE) {
    this->input = input;
    formattedInput = new FileHandler(GEN_OUT_FORMAT_FILE);
}

Guesser::~Guesser() {
    delete formattedInput;
}

void Guesser::initInputSource(size_t inputSize) {    
    input->reset();
    formattedInput->wipe();

    for (size_t i = 0; i < inputSize; i++)
        formattedInput->write(convertDataToFormat(input->readNext()));
}

std::string Guesser::convertDataToFormat(const std::string &rawData) {
    std::string inputFormat = config->getInputFormat();

    replaceAll(inputFormat, "\\n", "\n");
    replaceAll(inputFormat, "\\r", "\r");
    replaceAll(inputFormat, "\\t", "\t");

    replaceAll(inputFormat, DATA, rawData);

    return inputFormat;
}