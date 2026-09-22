#include "../../include/utils/Argument.hpp"

Argument::Argument(std::string name, std::string altName, std::string description, bool flag){
  this->name = name;
  this->flag = flag;
  this->altName = altName;
  this->description = description;
  
  this->value = flag ? "0" : "";
}

bool Argument::hasAltName() const {
  return !altName.empty();
}

std::string Argument::getName() const {
  return name;
}

std::string Argument::getAltName() const {
  return altName;
}

std::string Argument::getValue() const {
  return value;
}

std::string Argument::getDescription() const {
  return description;
}

bool Argument::isFlag() const {
  return flag;
}

void Argument::setValue(std::string value) {
  this->value = value;
}
