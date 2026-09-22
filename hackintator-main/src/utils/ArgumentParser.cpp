#include "../../include/utils/ArgumentParser.hpp"
#include "../../include/utils/HelpMenu.hpp"
#include <sstream>

ArgumentParser::ArgumentParser(){
  description = "";
  addFlagArgument("-h", "--help", "Show Help");
}

ArgumentParser::ArgumentParser(std::string_view description) : ArgumentParser() {
  this->description = description;
}

void ArgumentParser::addArgument(const char *name, const char *altName, const char *description){
  this->argsList.push_back(Argument(name, altName, description, false));
}

void ArgumentParser::addArgument(const char *name, const char *description){
  addArgument(name, "", description);
}

void ArgumentParser::addArgument(const char *name){
  addArgument(name, "", "");
}
  
void ArgumentParser::addFlagArgument(const char *name, const char *altName, const char *description){
  this->argsList.push_back(Argument(name, altName, description, true));
}

void ArgumentParser::addFlagArgument(const char *name, const char *description){
  addFlagArgument(name, "", description);
}

void ArgumentParser::addFlagArgument(const char *name){
  addFlagArgument(name, "", "");
}

std::string ArgumentParser::get(std::string args) const {
  for (int i = 0; i < int(argsList.size()); i++)
    if(matchArgument(&argsList[i], args.c_str()))
      return argsList[i].getValue();
  return "";
}

std::vector<std::string> ArgumentParser::getValueList(std::string args) const {
  std::string value = get(args);
  if(value.empty() || value.find(" ") == std::string::npos)
    return std::vector<std::string>({value});

  std::vector<std::string> argsList;
  std::stringstream stream(value);
  std::string buffer;

  while(std::getline(stream, buffer, ' '))
    argsList.push_back(buffer);

  return argsList;
}

std::vector<std::string> ArgumentParser::getArgumentsName() const {
  std::vector<std::string> argsName;

  for (int i = 0; i < int(argsList.size()); i++) {
    argsName.push_back(argsList[i].getName());
    if(argsList[i].hasAltName())
      argsName.push_back(argsList[i].getAltName());
  }

  return argsName;
}

bool ArgumentParser::matchArgument(const Argument *args, const char *argv) const {
  if(args->getName() == argv || (args->hasAltName() && args->getAltName() == argv))
    return true;
  return false;
}

void ArgumentParser::searchDuplicate() const {
  std::vector<std::string> argsName = getArgumentsName();

  for (int i = 0; i < int(argsName.size()); i++)
    for (int j = 0; j < int(argsName.size()); j++)
      if(i != j && argsName[i] == argsName[j])
        throw duplicate_argument_error("Duplicate Argument");
}

void ArgumentParser::parse(int size, char **argv) {
  searchDuplicate();

  for (int i = 1; i < size; i++)
    for (int j = 0; j < int(argsList.size()); j++)
      if(matchArgument(&argsList[j], argv[i]))
        setArgumentValue(j, &i, argv);
  handleHelp(argv[0]);
}

void ArgumentParser::verifyOverlapingArgument(int argvIndex, char **argv) const {
  std::vector<std::string> argsName = getArgumentsName();
  for (int i = 0; i < int(argsName.size()); i++)
    if(i != argvIndex && argsName[i] == argv[argvIndex+1])
       throw no_value_argument_error("Missing value for an argument");
}

void ArgumentParser::setArgumentValue(int argsIndex, int *argvIndex, char **argv) {
  if(argsList[argsIndex].isFlag()){
    argsList[argsIndex].setValue("1");
  } else {
    verifyOverlapingArgument(*argvIndex, argv);
    argsList[argsIndex].setValue(argv[++*argvIndex]);
  }
}

void ArgumentParser::handleHelp(const char *progName) const {
  if(std::stoi(get("-h")) == 1){
    HelpMenu help = HelpMenu(progName, description, &argsList);
    help.print();
    exit(0);
  }
}

duplicate_argument_error::duplicate_argument_error(const char *msg) : msg(msg) {}
no_value_argument_error::no_value_argument_error(const char *msg) : msg(msg) {}

const char *duplicate_argument_error::what() const throw() {
  return msg.c_str();
}

const char *no_value_argument_error::what() const throw() {
  return msg.c_str();
}
