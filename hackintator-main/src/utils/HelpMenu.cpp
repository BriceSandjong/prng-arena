#include "../../include/utils/HelpMenu.hpp"
#include <iostream>

HelpMenu::HelpMenu(const char *programName, std::string_view description, std::vector<Argument> const *argsList) {
  this->argsList = argsList;
  this->programName = programName;
  this->description = description;
}

void HelpMenu::printDescription() const {
  if(!description.empty())
    std::cout << description << "\n\n";
}

void HelpMenu::printArgsDescription(const Argument *args) const {
  if(!args->getDescription().empty())
    std::cout << "\t" << args->getDescription();
  std::cout << "\n";
}

void HelpMenu::printOptions() const {
  std::cout << "Options :\n";
  for (int i = 0; i < int(argsList->size()); i++) {
    std::cout << " " << argsList->at(i).getName();
    if(argsList->at(i).hasAltName())
      std::cout << ", " << argsList->at(i).getAltName();

    printArgsDescription(&argsList->at(i));
  }
}

void HelpMenu::printUsage() const {
  std::cout << "usage : " << programName << " ";
  for (int i = 0; i < int(argsList->size()); i++) {
    std::cout << "[" << argsList->at(i).getName();
    if(!argsList->at(i).isFlag())
      std::cout << " args";
    std::cout << "] ";
  }
  std::cout << "\n\n";
}

void HelpMenu::print() const {
  printUsage();  
  printDescription();
  printOptions();
}
