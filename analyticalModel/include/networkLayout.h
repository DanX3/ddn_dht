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
    std::vector<Connection*> links, linksForScratch;
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

inline ostream& operator<<(ostream& stream, const Node& n) {
    stream
        << "id:" << n.id << std::endl
        << "type:" << n.type << std::endl;
    for (auto link: n.links) {
        stream << *link << std::endl;
    }
    return stream;
}

class NetworkLayout {
private:
    enum class NodeType;
    std::vector<Connection> links, linksForScratch;
    std::vector<Node> nodes;

    void populateNodes(const Value& nodesArray);
    void populateLinks(const Value& nodesArray);
    bool nodesAreValid(const Value& nodesArray);
    bool linksAreValid(const Value& nodesArray);
    Node& getNode(int id);
    Connection& getLink(std::pair<int,int>edges);
    void normalizePair(std::pair<int,int>& p);

    Connection recursiveTrial(int callerId, int targetId, unsigned int hopLeft,
        Connection& flagConnection);



protected:
public:
    NetworkLayout(std::string& jsonPath);
    Connection abstractLinkBetween(int id1, int id2);
};

#endif
