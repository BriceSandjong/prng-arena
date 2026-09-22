#pragma once

#include <string>
#include "utils/FileHandler.hpp"
#include "algorithms/Generator.hpp"
#include "algorithms/Guesser.hpp"


class Comparator {
	public:
		Comparator(Generator* a, Guesser* b, unsigned long nbIteration, size_t inputSize, std::string command);
		~Comparator();
		
		void execute();

	private:
		Generator* a;
		Guesser* b;
		FileHandler* csvFile;
		unsigned long nbIteration;
		std::string command;

		bool isCorrectGuess();
		void runRatioPrinter(double* ratio);
		int getPrinterDelay();
};