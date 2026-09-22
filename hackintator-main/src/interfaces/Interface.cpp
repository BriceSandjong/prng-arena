#include "../../include/interfaces/Interface.hpp"


Interface::Interface(std::string outputFile) {
    setFileHandler(outputFile);
}

Interface::~Interface() {
    if (file != NULL)
        delete file;
}

void Interface::setFileHandler(std::string path) {
    this->file = new FileHandler(path);
}

void Interface::setCommand(std::string command) {
    this->command = command;
}

void Interface::setArgs(std::vector<std::string> args) {
    this->args = args;
}

std::string Interface::getCommand() const {
    return this->command;
}

std::vector<std::string> Interface::getArgs() const {
    return this->args;
}

std::string Interface::getCommandLine() const {
    if (this->args.size() == 0)
        return this->command;

    std::string args = this->args[0];

    for (unsigned long i = 1; i < this->args.size(); i++) {
        args = args + " " + this->args[i];
    }

    return this->command + " " + args;
}

FileHandler *Interface::getFileHandler() const {
    return this->file;
}
