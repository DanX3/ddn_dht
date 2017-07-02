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

void Utils::printError(std::string shortMessage, std::string message) {
    //print the short message in bold red font
    //the message is in normal black font
    std::cout << "\e[1;31m" << shortMessage << "\e[0;30m: " << message << std::endl;
}

int Utils::getNextNode(int myId, std::pair<int,int> edges) {
    if (edges.first == myId)
        return edges.second;
    return edges.first;
}
