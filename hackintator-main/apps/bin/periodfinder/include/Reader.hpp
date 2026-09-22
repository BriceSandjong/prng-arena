#pragma once

#include <fstream>
#include <string>
#include <vector>

class Reader {
private:
  std::ifstream *file;

public:
  Reader(std::string filePath);
  ~Reader();
  void setFile(std::ifstream *file);
  std::vector<std::string> getAllValuesToVector() const;
};