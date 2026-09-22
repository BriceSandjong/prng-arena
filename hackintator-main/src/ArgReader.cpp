#include "../include/ArgReader.hpp"
#include <filesystem>


ArgReader::ArgReader(int argc, char *argv[]) {
  argParser = new ArgumentParser();
  argParser->addArgument(GENERATOR_NAME, "--generator", "Generator name, as written in the .ini config file");
  argParser->addArgument(GUESSER_NAME, "--guesser", "Guesser name, as written in the .ini config file");
  argParser->addArgument(ITERATION_COUNT, "--iteration-count", "Number of outputs compared between Generator and Guesser");
  argParser->addArgument(SOURCE_SIZE, "--source-size", "Sets the maximal length read from Generator");
  argParser->addArgument(GEN_SCRIPT_ARGS_C, "--generator-arguments", "Add arguments to the generator script");
  argParser->addArgument(GUESS_SCRIPT_ARGS_C, "--guesser-arguments", "Add arguments to the guesser script");

  argParser->parse(argc, argv);
}

ArgReader::~ArgReader() {
  delete argParser;
}

std::string ArgReader::getGeneratorName() const {
  std::string arg = argParser->get(GENERATOR_NAME);
  validateAlgoName(arg);
  return arg;
}

std::string ArgReader::getGuesserName() const {
  std::string arg = argParser->get(GUESSER_NAME);
  validateAlgoName(arg);
  return arg;
}

size_t ArgReader::getIterationCount() const {
  std::string arg = argParser->get(ITERATION_COUNT).c_str();

  if (arg.empty())
    return -1;

  validateUnsignedNumber(arg);
  return convertToUnsignedLong(arg);
}

size_t ArgReader::getInputSize() const {
  std::string arg = argParser->get(SOURCE_SIZE).c_str();

  if (arg.empty())
    return getIterationCount();

  validateUnsignedNumber(arg);
  return convertToUnsignedLong(arg);
}

std::string ArgReader::getGenScriptArgs() const {
  return argParser->get(GEN_SCRIPT_ARGS_C);
}

std::string ArgReader::getGuessScriptArgs() const {
  return argParser->get(GUESS_SCRIPT_ARGS_C);
}

void ArgReader::validateAlgoName(std::string name) const {
  if (name.empty())
    throw std::invalid_argument("Algorithm name cannot be left empty");

  std::filesystem::path file {std::string("apps/").append(name).append(".ini")};
  if (!std::filesystem::exists(file))
    throw std::invalid_argument("Algorithm not found");
}

void ArgReader::validateUnsignedNumber(std::string arg) const {
  if (arg[0] == '-')
    throw std::invalid_argument("Value cannot be negative");
}

size_t ArgReader::convertToUnsignedLong(std::string arg) const {
  try {
    return std::stoul(arg);
  }
  catch (const std::invalid_argument& e) {
    throw std::invalid_argument("Invalid number");
  }
  catch (const std::out_of_range& e) {
    size_t maxValue = std::numeric_limits<size_t>::max();
    throw std::invalid_argument(std::string("Number is too long. Max is ").append(std::to_string(maxValue)).c_str());
  }
}