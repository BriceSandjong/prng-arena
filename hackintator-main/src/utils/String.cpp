#include "../../include/utils/String.hpp"
#include <algorithm>


void ltrim(std::string &s) {
    s.erase(s.begin(), std::find_if(s.begin(), s.end(), [](unsigned char ch) {
        return !std::isspace(ch);
    }));
}

void rtrim(std::string &s) {
    s.erase(std::find_if(s.rbegin(), s.rend(), [](unsigned char ch) {
        return !std::isspace(ch);
    }).base(), s.end());
}

void trim(std::string &s) {
    rtrim(s);
    ltrim(s);
}

std::string ltrim_copy(std::string s) {
    ltrim(s);
    return s;
}

std::string rtrim_copy(std::string s) {
    rtrim(s);
    return s;
}

std::string trim_copy(std::string s) {
    trim(s);
    return s;
}

void replaceAll(std::string &input, std::string toSearch, std::string replacement) {
    size_t pos = input.find(toSearch);
    
    while (pos != std::string::npos) {
        input.replace(pos, toSearch.size(), replacement);
        pos = input.find(toSearch, pos + replacement.size());
    }
}