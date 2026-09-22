#include "../include/algorithms/Generator.hpp"
#include "../include/algorithms/Guesser.hpp"
#include "../include/Comparator.hpp"
#include "../include/ArgReader.hpp"


int main(int argc, char *argv[])
{
    ArgReader args = ArgReader(argc, argv);

    Generator* algoA = new Generator(args.getGeneratorName(), args.getGenScriptArgs());

    OutputReader* outputReader = algoA->initOutputReader();
    Guesser* algoB = new Guesser(outputReader, args.getGuesserName(), args.getGuessScriptArgs());

    std::string commandLineStr= "";
    for (int i = 0; i < argc; i++) commandLineStr.append(std::string(argv[i]).append(" "));

    Comparator* comparatorContainer = new Comparator(algoA, algoB, args.getIterationCount(), args.getInputSize(), commandLineStr);

    comparatorContainer->execute();

    delete algoA;
    delete algoB;
    delete comparatorContainer;
    delete outputReader;

    return 0;
}
