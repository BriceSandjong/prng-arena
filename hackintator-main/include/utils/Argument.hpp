#pragma once
#include <string>

class Argument {
  private:
    std::string altName;
    std::string name;
    std::string value;
    std::string description;
    bool flag;
  public:
    Argument(std::string name, std::string altName, std::string description, bool flag);
    bool hasAltName() const;
    std::string getName() const;
    std::string getAltName() const;
    std::string getValue() const;
    std::string getDescription() const;
    bool isFlag() const;
    void setValue(std::string value);
};
