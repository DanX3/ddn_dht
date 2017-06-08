#include "networkLayout.h"


NetworkLayout::NetworkLayout(std::string& jsonPath) {
    std::string content;
    Utils::readFromFile(jsonPath.c_str(), content);
    Document document;
    //document.Parse(&content[0]);
    document.Parse(content.c_str());
    populateNodes(document["nodes"]);
    populateLinks(document["links"]);
}

void NetworkLayout::populateNodes(const Value& nodesArray) {
    bool success = checkNodes(nodesArray);
    if (!success) {
        exit(1);
    }
    for (SizeType i=0; i<nodesArray.Size(); ++i) {
        nodes.push_back(Node{
            nodesArray[i]["id"].GetInt(),
            nodesArray[i]["type"].GetString(),
        });
    }
    for (const auto& node: nodes) {
        std::cout << node << '\n';
    }
}

void NetworkLayout::populateLinks(const Value& linksArray) {
    //checks for links
    for (SizeType i=0; i<linksArray.Size(); ++i) {
        assert(linksArray[i]["edges"].IsArray());
        assert(linksArray[i]["edges"].Size() == 2);
        auto iterator = linksArray[i]["edges"].Begin();
        int firstEdge = iterator++->GetInt();
        int secondEdge = iterator->GetInt();

        if (firstEdge > secondEdge)
            std::swap(firstEdge, secondEdge);
        std::pair<int,int> edges{firstEdge, secondEdge};
        links.push_back(Connection(
                            linksArray[i]["Smax"].GetDouble(),
                            linksArray[i]["bw"].GetDouble(),
                            linksArray[i]["latency"].GetDouble(),
                            edges)
                    );
    }

    for (const auto& link: links) {
        std::cout << link << std::endl;
    }
}

bool NetworkLayout::checkNodes(const Value &nodesArray) {
    if (!nodesArray.IsArray()) {
        Utils::printError("Array type expected",
                          "Element 'node' expected to be an array");
        return false;
    }
    if (nodesArray.Size() < 2) {
        Utils::printError("Insufficient Node",
                          "Insufficient nodes found. At least 2 nodes, expected. Found "
                          + std::to_string(nodesArray.Size()));
        return false;
    }

    for (SizeType i=0; i<nodesArray.Size(); ++i) {
        if (nodesArray[i].MemberCount() > 2) {
            Utils::printError("Too many fields for 'node' object",
                              "only fields 'type' and 'id' are allowed in node object");
            return false;
        }
        if (!nodesArray[i].HasMember("type")) {
            Utils::printError("'type' field expected of node",
                              "missing 'type' field for node " +
                              std::to_string(i));
            return false;
        }
        if (!nodesArray[i].HasMember("id")) {
            Utils::printError("'id' field expected of node",
                              "missing 'id' field for node " +
                              std::to_string(i));
            return false;
        }
    }
    return true;
}

bool NetworkLayout::checkLinks(const Value &nodesArray) {

}
