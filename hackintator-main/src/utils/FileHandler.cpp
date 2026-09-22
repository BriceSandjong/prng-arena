#include "../../include/utils/FileHandler.hpp"
#include <filesystem>


FileHandler::FileHandler(std::string path){
  this->path = path;
  createHandler();
}

FileHandler::~FileHandler(){
  destroyHandler();
}

void FileHandler::createHandler(){
  this->handler = new std::fstream();
  this->handler->open(path, std::fstream::in | std::fstream::out | std::fstream::app);
}

void FileHandler::destroyHandler(){
  if(handler != NULL){
    handler->close();
    delete handler;
  }
}

void FileHandler::wipe() {
  destroyHandler();
  std::filesystem::remove(path);
  createHandler();
}

void FileHandler::write(std::string value){
  handler->seekp(0, std::ios::end);
  *handler << value;
  handler->seekp(0, std::ios::end);
}

void FileHandler::writeToNextLine(std::string value){
  this->write('\n' + value);
}

std::string FileHandler::read(int index) const {
  handler->seekp(0, std::ios::beg);
  std::string line;
  int i = 0;

  while (std::getline(*handler, line) && index > i++) { }
  
  if(handler->eof()) {
    handler->clear();
    throw std::range_error("File : Index is out of range");
  }

  return line;
}
