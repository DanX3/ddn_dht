#ifndef NETWORKLAYOUT_H
#define NETWORKLAYOUT_H

#include "utils.h"
#include "rapidjson/document.h"
#include "connection.h"
#include <vector>
using namespace rapidjson;

enum class NodeType {
    CLIENT,
    SECONDARY,
    HOME,
    NONE
};


struct Node {
    int id;
    NodeType type;
};

inline ostream& operator<<(ostream& stream, const NodeType& node) {
    switch(node) {
        case NodeType::CLIENT: stream << "CLIENT"; break;
        case NodeType::SECONDARY: stream << "SECONDARY"; break;
        case NodeType::HOME: stream << "HOME"; break;
        case NodeType::NONE: stream << "NONE"; break;
    }
}

inline ostream& operator<<(ostream& stream, const Node& node) {
    stream << node.id << ": " << node.type << std::endl;
}

class NetworkLayout {
private:
    enum class NodeType;
    std::vector<Connection> links;
    std::vector<Node> nodes;

    NodeType stringToNodetype(std::string s);
    void populateNodes(const Value& nodesArray);
    //void populateLinks(Document& document);

protected:
public:
    NetworkLayout(std::string& jsonPath);
};

 #endif
