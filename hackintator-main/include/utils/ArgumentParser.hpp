#pragma once
#include "Argument.hpp"
#include <string>
#include <string_view>
#include <vector>
#include <exception>

class ArgumentParser {
  private:
    std::string description;
    std::vector<Argument> argsList;

    void handleHelp(const char *programName) const;
    std::vector<std::string> getArgumentsName() const;
    void searchDuplicate() const;
    void setArgumentValue(int argsIndex, int *argvIndex, char **argv);
    void verifyOverlapingArgument(int argvIndex, char **argv) const;
    bool matchArgument(const Argument *args, const char *argv) const;
  public:
    ArgumentParser();
    ArgumentParser(std::string_view description);
    
    void addArgument(const char *name, const char *altName, const char *description);
    void addArgument(const char *name, const char *description);
    void addArgument(const char *name);
  
    void addFlagArgument(const char *name, const char *altName, const char *description);
    void addFlagArgument(const char *name, const char *description);
    void addFlagArgument(const char *name);

    void parse(int size, char **argv);
    std::string get(std::string args) const;
    std::vector<std::string> getValueList(std::string args) const;
};

class duplicate_argument_error : public std::exception {
  private:
    std::string msg;
  public:
    duplicate_argument_error(const char *msg);
    const char *what() const throw();
};

class no_value_argument_error : public std::exception {
  private:
    std::string msg;
  public: 
    no_value_argument_error(const char *msg);
    const char *what() const throw();
};
