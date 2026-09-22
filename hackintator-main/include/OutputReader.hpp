#pragma once

#include <regex>
#include <string>
#include "utils/FileHandler.hpp"
#include "AlgoConfig.hpp"


class OutputReader {
  public:
    OutputReader(FileHandler* fileHandler, AlgoConfig* algoConfig);
    ~OutputReader();

    void reset();
    std::string readNext();

  private:
    FileHandler* fileHandler;
    int lineIndex;
    int lineGroupIndex;
    int delimiterIndex;
    AlgoConfig* algoConfig;

    std::string tryGetNextLine();
    std::string getToken(const std::string &filteredLine);
    std::string getLineGroup(const std::string &input);
    std::string findNextGroup(const std::smatch &lineMatches);
		std::smatch getMatches(const std::string &input, const std::string &regexStr);
};