#pragma once

#include <string>
#include <fstream>


class FileHandler {
  public:
    FileHandler(std::string path);
    ~FileHandler();
    
    std::string read(int index) const;
    void write(std::string value);
    void writeToNextLine(std::string value);
    void wipe();

  private:
    std::string path;
    std::fstream *handler;

    void createHandler();
    void destroyHandler();
};
