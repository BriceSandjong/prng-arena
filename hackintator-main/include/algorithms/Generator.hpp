#pragma once

#include <string>
#include "Algorithm.hpp"
#include "../OutputReader.hpp"


class Generator : public Algorithm {
	public:
		Generator(std::string configName, std::string scriptArgs);
		~Generator();

		OutputReader* initOutputReader();
};