#include "networkLayout.h"


template <bool Const, class ValueT>
NetworkLayout::NetworkLayout(std::string& jsonPath) {
    std::string content;
    Utils::readFromFile(&jsonPath[0], content);
    Document document;
    document.Parse(&content[0]);
    GenericArray<Const, ValueT> nodesArray = document["nodes"].GetArray();
    GenericArray<Const, ValueT> linksArray = document["links"].GetArray();
    populateNodes(nodesArray);
    populateLinks(linksArray);
}

template <bool Const, class ValueT>
void NetworkLayout::populateNodes(GenericArray<Const, ValueT> nodes) {
    for (GenericArray<Const, ValueT> link: links) {
        std::cout << "Ahah" << '\n';
    }
}

template <bool Const, class ValueT>
void NetworkLayout::populateLinks(GenericArray<Const, ValueT> links) {
    for (GenericArray<Const, ValueT>ink: links) {
        std::cout << "Eheh" << '\n';
    }
}
