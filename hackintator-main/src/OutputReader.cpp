#include "../include/OutputReader.hpp"


OutputReader::OutputReader(FileHandler* fileHandler, AlgoConfig* algoConfig) {
  this->fileHandler = fileHandler;
  this->algoConfig = algoConfig;
  reset();
}

OutputReader::~OutputReader() {

}

void OutputReader::reset() {
  this->lineIndex = algoConfig->getStartLine();
  this->lineGroupIndex = 0;
  this->delimiterIndex = 0;
}

std::string OutputReader::readNext() {
  if (algoConfig->getEndLine() != -1 && lineIndex > algoConfig->getEndLine())
    return "";
  
  std::string fullLine = tryGetNextLine();

  if (fullLine.empty())
    return fullLine;
  
  std::string filteredLine = getLineGroup(fullLine);
  return getToken(filteredLine);
}

std::string OutputReader::tryGetNextLine() {
  try {
    return fileHandler->read(lineIndex++);
  }
  catch (const std::range_error& e) {
    if (!algoConfig->isRepeatCycle())
      return "";

    reset();
    return readNext();
  }
}

std::string OutputReader::getToken(const std::string &filteredLine) {
  if (algoConfig->getDelimiter().empty())
    return filteredLine;

  size_t start = delimiterIndex;
  size_t end = filteredLine.find(algoConfig->getDelimiter(), delimiterIndex);

  if (end != std::string::npos) {
    delimiterIndex = end + algoConfig->getDelimiter().length();
    lineIndex--;

    return filteredLine.substr(start, end - start);
  }

  delimiterIndex = 0;
  return filteredLine.substr(start);
}

std::string OutputReader::getLineGroup(const std::string &input) {
  if (algoConfig->getLineFilter().empty())
    return input;

  std::smatch matches = getMatches(input, algoConfig->getLineFilter());

  if (matches.empty())
    return readNext();

  bool hasGroups = (matches.size() > 1);
  if (!hasGroups) {
    std::string fullLine = matches[0];
    return fullLine;
  }
  
  return findNextGroup(matches);
}

std::string OutputReader::findNextGroup(const std::smatch &lineMatches) {
  unsigned long index = ++lineGroupIndex;

  bool isLastGroup = (index == lineMatches.size() - 1);
  if (isLastGroup)
    lineGroupIndex = 0;
  else 
    lineIndex--;

  return lineMatches[index];
}

std::smatch OutputReader::getMatches(const std::string &input, const std::string &regexStr) {
  std::smatch matches;

  std::regex_search(input, matches, std::regex(regexStr));

  return matches;
}