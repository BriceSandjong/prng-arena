#include "../../include/interfaces/InterfaceConsole.hpp"
#include <cstdio>
#include <stdexcept>

#if defined(_WIN32)
#define POPEN _popen
#define PCLOSE _pclose
#else
#define POPEN popen
#define PCLOSE pclose
#endif

int InterfaceConsole::run(const char* commandLine) {
    FILE *output = POPEN(commandLine, "r");
    if (!output) {
        throw std::runtime_error("popen/_popen failed!");
    }

    char line[255];
    std::string result = "";

    while (fgets(line, sizeof(line), output) != nullptr) {
        result += line;
    }

    getFileHandler()->wipe();
    getFileHandler()->write(result);

    PCLOSE(output);
    return 0;
}
