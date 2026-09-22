#include "../../include/interfaces/InterfaceSystem.hpp"


int InterfaceSystem::run(const char* commandLine) {
    return system(commandLine);
}
