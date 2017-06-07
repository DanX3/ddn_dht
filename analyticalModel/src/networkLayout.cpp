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
    assert(nodesArray.IsArray());
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
    checkNodes(linksArray);
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
    Utils::printError("Array object not found", "array type expected as 'node'");
//    if (!linksArray.IsArray()) {
//        std::err << "Object \"nodes\" is not an array"
//    }
//    for (SizeType i=0; i<linksArray.Size(); ++i) {
//    }
}

bool NetworkLayout::checkLinks(const Value &nodesArray) {

}
