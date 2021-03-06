#ifndef UTILS_H
#define UTILS_H

#include <fstream>
#include <fstream>
#include <iostream>

class Utils {
private:
protected:
public:
    static void readFromFile(const char* file, std::string& content);
    static void printError(std::string shortMessage, std::string message);
    static int getNextNode(int myId, std::pair<int,int> edges);
    static void printWarning(std::string shortMessage, std::string message);
};

 #endif
