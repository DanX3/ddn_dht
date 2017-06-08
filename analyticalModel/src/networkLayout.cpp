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
    if (!nodesAreValid(nodesArray)) {
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
    if (!linksAreValid(linksArray)) {
        exit(1);
    }

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

bool NetworkLayout::nodesAreValid(const Value &nodesArray) {
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

bool NetworkLayout::linksAreValid(const Value &linksArray) {
    if (linksArray.Size() == 0) {
        Utils::printError("No link found", "expected at least one link");
        return false;
    }

    
    for (SizeType i=0; i<linksArray.Size(); ++i) {
        if (linksArray[i].MemberCount() != 4) {
            Utils::printError("Bad link object",
                "link " + std::to_string(i) + " has different number of fields than expected");
            return false;
        } 

        if (!linksArray[i].HasMember("edges")) {
            Utils::printError("edges not found", "could not find 'edges' field for link " 
            + std::to_string(i));
            return false;
        }
        if (!linksArray[i].HasMember("Smax")) {
            Utils::printError("Smax not found", "could not find 'Smax' field for link " 
            + std::to_string(i));
            return false;
        }
        if (!linksArray[i].HasMember("bw")) {
            Utils::printError("bw not found", "could not find 'bw' field for link " 
            + std::to_string(i));
            return false;
        }
        if (!linksArray[i].HasMember("latency")) {
            Utils::printError("latency not found", "could not find 'latency' field for link " 
            + std::to_string(i));
            return false;
        }
    }
    return true;
}
