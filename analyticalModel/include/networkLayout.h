#ifndef NETWORKLAYOUT_H
#define NETWORKLAYOUT_H

#include "utils.h"
#include "rapidjson/document.h"
#include "connection.h"
#include <vector>
#include <string>
using namespace rapidjson;

enum class NodeType { CLIENT, SECONDARY, HOME, NONE };


struct Node {
    int id;
    std::string type;
};

inline ostream& operator<<(ostream& stream, const NodeType& node) {
    switch(node) {
        case NodeType::CLIENT: stream << "CLIENT"; break;
        case NodeType::SECONDARY: stream << "SECONDARY"; break;
        case NodeType::HOME: stream << "HOME"; break;
        case NodeType::NONE: stream << "NONE"; break;
    }
    return stream;
}

inline ostream& operator<<(ostream& stream, const Node& node) {
    stream << node.id << ": " << node.type;
    return stream;
}

class NetworkLayout {
private:
    enum class NodeType;
    std::vector<Connection> links;
    std::vector<Node> nodes;

    void populateNodes(const Value& nodesArray);
    void populateLinks(const Value& nodesArray);
    bool nodesAreValid(const Value& nodesArray);
    bool linksAreValid(const Value& nodesArray);

protected:
public:
    NetworkLayout(std::string& jsonPath);
};

 #endif
