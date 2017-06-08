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
    std::vector<Connection*> links;
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

<<<<<<< HEAD
inline ostream& operator<<(ostream& stream, const Node& n) {
    stream 
        << "id:" << n.id << std::endl
        << "type:" << n.type << std::endl;
    for (auto link: n.links) {
        stream << *link << std::endl;
    }
    return stream;
}

=======
>>>>>>> 0d3caf81cf9dda605010cf2715eb6744adfea5ee
class NetworkLayout {
private:
    enum class NodeType;
    std::vector<Connection> links;
    std::vector<Node> nodes;

    void populateNodes(const Value& nodesArray);
    void populateLinks(const Value& nodesArray);
    bool nodesAreValid(const Value& nodesArray);
    bool linksAreValid(const Value& nodesArray);
    Node& getNode(int id);
    Connection& getLink(std::pair<int,int>edges);
    void normalizePair(std::pair<int,int>& p);


protected:
public:
    NetworkLayout(std::string& jsonPath);
};

<<<<<<< HEAD
#endif
=======

inline ostream& operator<<(ostream& stream, const Node& n) {
    stream 
        << "id:" << n.id << std::endl
        << "type:" << n.type << std::endl;
    for (auto link: n.links) {
        stream << *link << std::endl;
    }
    return stream;
}

 #endif
>>>>>>> 0d3caf81cf9dda605010cf2715eb6744adfea5ee
