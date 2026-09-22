#pragma once

#include <string>
#include <string_view>
#include <vector>
#include "Argument.hpp"

class HelpMenu {
  private:
    std::string programName;
    std::string_view description;
    std::vector<Argument> const *argsList;

    void printDescription() const;
    void printOptions() const;
    void printUsage() const;
    void printArgsDescription(const Argument *args) const;
  public:
    HelpMenu(const char *programName, std::string_view description, std::vector<Argument> const *argsList);
    void print() const;
};
