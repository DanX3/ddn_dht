#include "networkLayout.h"


NetworkLayout::NetworkLayout(std::string& jsonPath) {
    std::string content;
    Utils::readFromFile(jsonPath.c_str(), content);
    Document document;
    //document.Parse(&content[0]);
    document.Parse(content.c_str());
    populateNodes(document["nodes"]);
    populateLinks(document["links"]);

    Connection& link = getLink(std::pair<int,int>{3,2});
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
        std::pair<int,int> edges{firstEdge, secondEdge};
        normalizePair(edges);

        //creating the link and adding it to the corresponding nodes
        links.push_back(Connection(
            linksArray[i]["Smax"].GetDouble(),
            linksArray[i]["bw"].GetDouble(),
            linksArray[i]["latency"].GetDouble(),
            edges));
        getNode(firstEdge).links.push_back(&links.back());
        getNode(secondEdge).links.push_back(&links.back());
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

Node& NetworkLayout::getNode(int id) {
    for (Node& node: nodes) {
        if (node.id == id) {
            return node;
        }
    }

    //a bit harsh but for now works
    //will be better returning NONE or similar,
    //in order to behave accordingly
    Utils::printError("Out for range node id",
        "called node " + std::to_string(id) + "but none found");
    exit(1);
}

Connection& NetworkLayout::getLink(std::pair<int,int>edges) {
    normalizePair(edges);
    for (Connection& link: links) {
        if (link.getEdges() == edges) {
            return link;
        }
    }

    //a bit harsh but for now works
    //will be better returning NONE or similar,
    //in order to behave accordingly
    Utils::printError("Non-existing link",
        "called node <" +
        std::to_string(edges.first) + "-" +
        std::to_string(edges.second) + "> but none found");
    exit(1);
}

void NetworkLayout::normalizePair(std::pair<int,int>& p) {
    if (p.first > p.second) {
        int temp = p.first;
        p.first = p.second;
        p.second = temp;
    }
}

Connection NetworkLayout::abstractLinkBetween(int id1, int id2) {
    linksForScratch = links;
    Connection handler;
    handler.setUsable(false);
    recursiveTrial(id1, id2, nodes.size(), handler);
}

Connection NetworkLayout::recursiveTrial(int callerId, int targetId, unsigned int hopLeft,
    Connection& flagConnection) {
    if (hopLeft == 0) {
        flagConnection.setUsable(false);
        return flagConnection;
    }

    //we got it, now answer back to the beginning
    if (callerId == targetId) {
        flagConnection.setUsable(true);
        return flagConnection;
    }
    //check the links
    else {
        std::pair<int,int> linkEdges{callerId,targetId};
        normalizePair(linkEdges);
        Connection bestConnection;
        bestConnection.makeWorstConnectionEver();
        for (auto link: getNode(linkEdges.first).links) {
            //skip calling back the link from where it has been called
            if (link->getEdges().first == callerId || link->getEdges().second == callerId) {
                continue;
            }

            //tries all the remaining links
            Connection result = recursiveTrial(linkEdges.first, linkEdges.second,
                hopLeft-1, flagConnection);
            if (result.isUsable() && result.lessLatencyThan(bestConnection)) {
                bestConnection = result;
            }
        }
        return bestConnection;
    }
}
