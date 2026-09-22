#pragma once

#include <map>
#include <string>


#define DATA "%data%"
#define SCRIPT_ARGS "%args%"

#define CMD_GEN_OUT_FILE "%generator_output_file%"
#define CMD_GEN_OUT_ARGS "%generator_output_to_separate_args%"
#define CMD_GEN_OUT_STR "%generator_output_to_string%"


extern const std::map<std::string, std::string> STATIC_PLACEHOLDERS;