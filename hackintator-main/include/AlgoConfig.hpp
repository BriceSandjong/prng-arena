#pragma once

#include <string>
#include "utils/config/QuotedConfigReader.hpp"


class AlgoConfig {
	public:
		AlgoConfig(std::string configName, std::string scriptArgs);
		~AlgoConfig();

		std::string getCmd();
		std::string getOutput();
		std::string getLineFilter();
		std::string getDelimiter();
		int getStartLine();
		int getEndLine();
		std::string getInputFormat();
		bool isRepeatCycle();

	private:
		std::string scriptArgs;
		QuotedConfigReader* configReader;

		int paramToInt(std::string param);
		std::string parseVars(std::string input);
};