#include "../../../include/utils/config/ConfigReader.hpp"
#include <fstream>
#include "../../../include/utils/String.hpp"


ConfigReader::ConfigReader(std::filesystem::path configFile) {
    this->configFile = configFile;
    std::map<std::string, std::string> config = {};
    parse();
}

ConfigReader::~ConfigReader() {

}

std::string ConfigReader::getParameter(std::string name) {
    return config[name];
}

void ConfigReader::parse() {
    std::ifstream fileStream(configFile);

    if (fileStream.fail())
        throw std::filesystem::filesystem_error(
            std::string("Could not read config file ").append(configFile.string()), 
            make_error_code(std::errc::no_such_file_or_directory));

    std::string line;

    while (std::getline(fileStream, line))
    {
        std::istringstream isLine(line);
        std::pair<std::string, std::string> parameter = extractParamFromLine(isLine);
        addToConfig(parameter);
    }
}

std::pair<std::string, std::string> ConfigReader::extractParamFromLine(std::istringstream &isLine) {
    std::string key;
    std::string value;

    std::getline(isLine, key, '=');
    std::getline(isLine, value);

    return {key, value};
}

void ConfigReader::addToConfig(std::pair<std::string, std::string> parameter) {
    if (parameter.first == "")
        return;

    std::string key = trim_copy(parameter.first);
    std::string value = trim_copy(parameter.second);
    this->config[key] = value;
}