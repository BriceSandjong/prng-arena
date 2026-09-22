#include "../../../include/utils/config/QuotedConfigReader.hpp"


QuotedConfigReader::QuotedConfigReader(std::filesystem::path configFile) : ConfigReader(configFile) {

};

QuotedConfigReader::~QuotedConfigReader() {

};

std::string QuotedConfigReader::getParameter(std::string name) {
  return extractQuotedValue(ConfigReader::getParameter(name));
};

std::string QuotedConfigReader::extractQuotedValue(const std::string &input) {
  if (isFirstCharQuote(input) && isLastCharQuote(input))
    return input.substr(1, input.size() - 2);
  return input;
};

bool QuotedConfigReader::isFirstCharQuote(const std::string &input) {
  return isQuote(input[0]);
}

bool QuotedConfigReader::isLastCharQuote(const std::string &input) {
  char lastChar = input[input.size()-1];
  return isQuote(lastChar);
}

bool QuotedConfigReader::isQuote(char character) {
  return character == '"';
}