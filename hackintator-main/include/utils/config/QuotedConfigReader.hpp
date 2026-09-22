#pragma once

#include <filesystem>
#include "ConfigReader.hpp"


class QuotedConfigReader : public ConfigReader {
	public:
		QuotedConfigReader(std::filesystem::path configFile);
		~QuotedConfigReader();

		std::string getParameter(std::string name) override;

	private:
		std::string extractQuotedValue(const std::string &input);
    bool isFirstCharQuote(const std::string &input);
    bool isLastCharQuote(const std::string &input);
    bool isQuote(char character);
};