#pragma once

#include <string>
#include "../include/utils/ArgumentParser.hpp"


#define GENERATOR_NAME "-g"
#define GUESSER_NAME "-p"
#define ITERATION_COUNT "-n"
#define SOURCE_SIZE "-ns"
#define GEN_SCRIPT_ARGS_C "-ag"
#define GUESS_SCRIPT_ARGS_C "-ap"


class ArgReader {
	public:
		ArgReader(int argc, char *argv[]);
		~ArgReader();

        std::string getGeneratorName() const;
        std::string getGuesserName() const;
        size_t getIterationCount() const;
        size_t getInputSize() const;
        std::string getGenScriptArgs() const;
        std::string getGuessScriptArgs() const;

	private:
        ArgumentParser* argParser;

        void validateAlgoName(std::string name) const;
        void validateUnsignedNumber(std::string arg) const;
        size_t convertToUnsignedLong(std::string arg) const;
};