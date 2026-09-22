#pragma once

#include <string>
#include "Algorithm.hpp"
#include "../utils/FileHandler.hpp"
#include "../OutputReader.hpp"


class Guesser: public Algorithm {
	public:
		Guesser(OutputReader* input, std::string configName, std::string scriptArgs);
		~Guesser();

		void initInputSource(size_t inputSize);

	private:
		OutputReader* input;
		FileHandler* formattedInput;

		std::string convertDataToFormat(const std::string &rawData);
};