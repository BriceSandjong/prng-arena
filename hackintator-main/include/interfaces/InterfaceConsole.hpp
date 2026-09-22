#pragma once

#include "Interface.hpp"


class InterfaceConsole : public Interface {
    public:
        InterfaceConsole(std::string outputPath) : Interface(outputPath) {}
        
        int run(const char* command);
};


