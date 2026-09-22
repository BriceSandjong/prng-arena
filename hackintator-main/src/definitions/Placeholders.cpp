#include "../../include/definitions/Placeholders.hpp"
#include <filesystem>
#include "../../include/definitions/OutputPaths.hpp"

const std::filesystem::path outputAbsolutePath = std::filesystem::absolute(GEN_OUT_FORMAT_FILE);
const std::string outputArgs = std::string("$(cat \"").append(outputAbsolutePath.string()).append("\")");

const std::map<std::string, std::string> STATIC_PLACEHOLDERS = {
  {CMD_GEN_OUT_FILE, outputAbsolutePath.string()},
  {CMD_GEN_OUT_ARGS, outputArgs},
  {CMD_GEN_OUT_STR, std::string("\"").append(outputArgs).append("\"")},
};
