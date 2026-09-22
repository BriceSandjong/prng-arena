#pragma once

#include <string>
#include <filesystem>
#include "../AlgoConfig.hpp"
#include "../interfaces/Interface.hpp"
#include "../OutputReader.hpp"


class Algorithm {
	public:
		std::string getNextValue();
		void generateOutput(unsigned long size);

	protected:
		Algorithm(std::string configName, std::string scriptArgs, std::filesystem::path outputPath);
		virtual ~Algorithm();

		AlgoConfig* config;
		Interface* interface;
		
		void runApp();

	private:
		OutputReader* output;

		Interface* buildInterface(const std::filesystem::path& outputFile);
};