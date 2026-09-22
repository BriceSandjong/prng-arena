#pragma once

#include <vector>
#include <string>
#include "../utils/FileHandler.hpp"


class Interface {
    public:
        Interface(std::string outputPath);
        virtual ~Interface();

        virtual int run(const char *commandLine) = 0;
        std::string getCommand() const;
        std::vector<std::string> getArgs() const;
        std::string getCommandLine() const;
        FileHandler *getFileHandler() const;

    protected:
        void setCommand(std::string command);
        void setArgs(std::vector<std::string> args);
        void setFileHandler(std::string path);

    private:
        std::string command;
        std::vector<std::string> args;
        FileHandler *file;
};
