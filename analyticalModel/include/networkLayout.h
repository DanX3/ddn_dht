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
    HOME
};

struct Node {
    int id;
    NodeType type;
};

class NetworkLayout {
private:
    enum class NodeType;
    std::vector<Connection> links;
    std::vector<Node> nodes;

    template <bool Const, class ValueT>
    void populateNodes(GenericArray<Const, ValueT> nodes);
    template <bool Const, class ValueT>
    void populateLinks(GenericArray<Const, ValueT> links);

protected:
public:
    template <bool Const, class ValueT>
    NetworkLayout(std::string& jsonPath);
};

 #endif
