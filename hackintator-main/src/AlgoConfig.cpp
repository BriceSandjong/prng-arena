#include "../include/AlgoConfig.hpp"
#include "../include/definitions/Placeholders.hpp"
#include "../include/utils/String.hpp"


AlgoConfig::AlgoConfig(std::string configName, std::string scriptArgs) {
  std::filesystem::path configFile = std::string("apps/").append(configName).append(".ini");

  this->configReader = new QuotedConfigReader(configFile);
  this->scriptArgs = scriptArgs;
}

AlgoConfig::~AlgoConfig() {
  delete configReader;
}

std::string AlgoConfig::getCmd() {
  return parseVars(configReader->getParameter("cmd"));
};

std::string AlgoConfig::getOutput() {
  return configReader->getParameter("output");
};

std::string AlgoConfig::getLineFilter() {
  return configReader->getParameter("line_filter");
};

std::string AlgoConfig::getDelimiter() {
  return configReader->getParameter("delimiter");
};

int AlgoConfig::getStartLine() {
  return paramToInt(configReader->getParameter("start_line"));
};

int AlgoConfig::getEndLine() {
  std::string param = configReader->getParameter("end_line");

  return param.empty() ? -1 : paramToInt(param);
};

std::string AlgoConfig::getInputFormat() {
  return configReader->getParameter("input_format");
}

bool AlgoConfig::isRepeatCycle() {
  return configReader->getParameter("repeat") == std::string("true");
}

int AlgoConfig::paramToInt(std::string param) {
  return atoi(param.c_str());
}

std::string AlgoConfig::parseVars(std::string input) {
  for (auto const& [key, val] : STATIC_PLACEHOLDERS)
    replaceAll(input, key, val);

  replaceAll(input, SCRIPT_ARGS, scriptArgs);

  return input;
}