#include "../../include/utils/Hardware.hpp"
#include <cstring>
#include <system_error>
#include <ctime>
#include <cstdlib>

#if defined(_WIN32)
#include <windows.h>
#include <psapi.h>
#else
#include <sys/times.h>
#endif


#if !defined(_WIN32)
static clock_t lastCPU, lastSysCPU, lastUserCPU;
static int numProcessors;
#else
static ULARGE_INTEGER lastIdleTime;
static ULARGE_INTEGER lastKernelTime;
static ULARGE_INTEGER lastUserTime;
#endif

int parseLine(char* line){
    int i = strlen(line);
    const char* p = line;
    while (*p <'0' || *p > '9') p++;
    line[i-3] = '\0';
    i = atoi(p);
    return i;
}

int getPhysicalMemoryUsage(){ 
#if defined(_WIN32)
    PROCESS_MEMORY_COUNTERS_EX pmc;
    if (!GetProcessMemoryInfo(GetCurrentProcess(), reinterpret_cast<PROCESS_MEMORY_COUNTERS*>(&pmc), sizeof(pmc))) {
        throw std::system_error(GetLastError(), std::system_category(), "GetProcessMemoryInfo failed");
    }

    // Keep historical behavior: return kB.
    return static_cast<int>(pmc.WorkingSetSize / 1024);
#else
    FILE* file = fopen("/proc/self/status", "r");
    if(!file)
        throw std::system_error();

    int result = -1;
    char line[128];

    while (fgets(line, 128, file) != NULL){
        if (strncmp(line, "VmRSS:", 6) == 0){
            result = parseLine(line);
            break;
        }
    }
    fclose(file);
    return result;
#endif
}

void initCPU(){
#if defined(_WIN32)
    FILETIME idleTime;
    FILETIME kernelTime;
    FILETIME userTime;

    if (!GetSystemTimes(&idleTime, &kernelTime, &userTime)) {
        throw std::system_error(GetLastError(), std::system_category(), "GetSystemTimes failed");
    }

    lastIdleTime.LowPart = idleTime.dwLowDateTime;
    lastIdleTime.HighPart = idleTime.dwHighDateTime;
    lastKernelTime.LowPart = kernelTime.dwLowDateTime;
    lastKernelTime.HighPart = kernelTime.dwHighDateTime;
    lastUserTime.LowPart = userTime.dwLowDateTime;
    lastUserTime.HighPart = userTime.dwHighDateTime;
#else
    struct tms timeSample;
    char line[128];

    lastCPU = times(&timeSample);
    lastSysCPU = timeSample.tms_stime;
    lastUserCPU = timeSample.tms_utime;

    FILE* file = fopen("/proc/cpuinfo", "r");
    if(!file)
        throw std::system_error();

    numProcessors = 0;
    while(fgets(line, 128, file) != NULL){
        if (strncmp(line, "processor", 9) == 0)
            numProcessors++;
    }
    fclose(file);
#endif
}

double getCPUUsage(){
#if defined(_WIN32)
    FILETIME idleTime;
    FILETIME kernelTime;
    FILETIME userTime;

    if (!GetSystemTimes(&idleTime, &kernelTime, &userTime)) {
        throw std::system_error(GetLastError(), std::system_category(), "GetSystemTimes failed");
    }

    ULARGE_INTEGER idleNow;
    ULARGE_INTEGER kernelNow;
    ULARGE_INTEGER userNow;
    idleNow.LowPart = idleTime.dwLowDateTime;
    idleNow.HighPart = idleTime.dwHighDateTime;
    kernelNow.LowPart = kernelTime.dwLowDateTime;
    kernelNow.HighPart = kernelTime.dwHighDateTime;
    userNow.LowPart = userTime.dwLowDateTime;
    userNow.HighPart = userTime.dwHighDateTime;

    const ULONGLONG idleDiff = idleNow.QuadPart - lastIdleTime.QuadPart;
    const ULONGLONG kernelDiff = kernelNow.QuadPart - lastKernelTime.QuadPart;
    const ULONGLONG userDiff = userNow.QuadPart - lastUserTime.QuadPart;
    const ULONGLONG totalDiff = kernelDiff + userDiff;

    lastIdleTime = idleNow;
    lastKernelTime = kernelNow;
    lastUserTime = userNow;

    if (totalDiff == 0) {
        return 0.0;
    }

    const double busy = static_cast<double>(totalDiff - idleDiff);
    return (busy * 100.0) / static_cast<double>(totalDiff);
#else
    struct tms timeSample;
    clock_t now;
    double percent;

    now = times(&timeSample);

    if (now <= lastCPU || timeSample.tms_stime < lastSysCPU ||
        timeSample.tms_utime < lastUserCPU){

        //Overflow detection
        percent = -1.0;
    }
    else{
        percent = (timeSample.tms_stime - lastSysCPU) +
            (timeSample.tms_utime - lastUserCPU);
        percent /= (now - lastCPU);
        percent /= numProcessors;
        percent *= 100;
    }
    lastCPU = now;
    lastSysCPU = timeSample.tms_stime;
    lastUserCPU = timeSample.tms_utime;

    return percent;
#endif
}