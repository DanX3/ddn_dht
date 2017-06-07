#include "utils.h"

void Utils::readFromFile(const char* file, std::string& content) {
    std::ifstream jsonfile;
    jsonfile.open(file);
    std::string buffer;
    while (true) {
        jsonfile >> buffer;
        if (jsonfile.eof()) break;
        content += buffer;
    }
}

