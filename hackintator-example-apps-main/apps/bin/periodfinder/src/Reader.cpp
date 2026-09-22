#include "../include/Reader.hpp"

Reader::Reader(std::string filePath) {
  this->file = new std::ifstream(filePath);

  if (!file->good())
    throw std::string("Reader : Error opening file");
}

Reader::~Reader() {
  file->close();
  delete file;
}

std::vector<std::string> Reader::getAllValuesToVector() const{
  std::vector<std::string> g1;
 
  if (this->file->is_open()) {
    std::string str;
    while (file->good() && std::getline(*file, str))
      g1.push_back(str);
  }
  return g1;
}

void Reader::setFile(std::ifstream *file) { 
  this->file = file; 
}