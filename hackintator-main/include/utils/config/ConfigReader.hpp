#pragma once

#include <map>
#include <filesystem>
#include <string>
#include <sstream>


class ConfigReader {
	public:
		ConfigReader(std::filesystem::path configFile);
		virtual ~ConfigReader();

		virtual std::string getParameter(std::string name);

	private:
		std::filesystem::path configFile;
		std::map<std::string, std::string> config;

		void parse();
		std::pair<std::string, std::string> extractParamFromLine(std::istringstream &isLine);
		void addToConfig(std::pair<std::string, std::string> parameter);
};