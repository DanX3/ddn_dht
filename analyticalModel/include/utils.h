#ifndef UTILS_H
#define UTILS_H

#include <fstream>
#include <iostream>

class Utils {
private:
protected:
public:
    static void readFromFile(const char* file, std::string& content);
    static void printError(std::string shortMessage, std::string message);
    static void printWarning(std::string shortMessage, std::string message);
};

 #endif
