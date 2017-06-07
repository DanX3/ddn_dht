#include "networkLayout.h"


NetworkLayout::NetworkLayout(std::string& jsonPath) {
    std::string content;
    Utils::readFromFile(jsonPath.c_str(), content);
    Document document;
    //document.Parse(&content[0]);
    document.Parse(content.c_str());
    populateNodes(document["nodes"]);
    //populateLinks<Const, ValueT>(document);
}

void NetworkLayout::populateNodes(const Value& nodesArray) {
    assert(nodesArray.IsArray());
    std::cout << "nodesArray is an array" << '\n';
    for (SizeType i=0; i<nodesArray.Size(); ++i) {
        nodes.push_back(Node{
            nodesArray[i]["id"].GetInt(),
            stringToNodetype(nodesArray[i]["type"].GetString()),
        });
    }
    for (const auto& node: nodes) {
        std::cout << node << '\n';
    }
}

//void NetworkLayout::populateLinks(Document& document) {
    //GenericArray<bool, GenericArray&> linksArray = document["links"].GetArray();
    //for (auto link: linksArray) {
        //std::cout << "Eheh" << '\n';
    //}
//}

NetworkLayout::NodeType NetworkLayout::stringToNodetype(std::string s) {
    if (s == "client")
        return NetworkLayout::NodeType::CLIENT;
    if (s == "secondary")
        return NetworkLayout::NodeType::SECONDARY;
    if (s == "home")
        return NetworkLayout::NodeType::HOME;
    return NetworkLayout::NodeType::NONE;
}
