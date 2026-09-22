#pragma once

#include "Interface.hpp"


class InterfaceSystem : public Interface {
    public:
        InterfaceSystem(std::string outputPath) : Interface(outputPath) {}

        int run(const char* command);
};


