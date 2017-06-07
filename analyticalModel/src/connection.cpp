#include "connection.h"

/*
 * The class Connection keep track of the setting of the Connection
 * like considering the bandwidth that the link has
 * and keeping a status, the meaningful variables are shown to the user
 *
 * Ps: the packet size in MB
 * Smax: Size in MB after which we get to full bandwidth communication
 */

const double Connection::ackSize = 2e-16;
const double Connection::checksumRatio = 0.25;

Connection::Connection(double __Smax, double __bandwidth, double __latency,
                       std::pair<int, int> __edges) :
    Smax(__Smax),
    bandwidth(__bandwidth),
    latency(__latency),
    edges(__edges)
    {
    }

Connection::Connection(const char* jsonPath) {
    std::string content;
    Utils::readFromFile(jsonPath, content);
    rapidjson::Document document;
    document.Parse(&content[0]);
    rapidjson::Value& value = document["bandwidth"];
    bandwidth = value.GetDouble();

    value = document["Smax"];
    Smax = value.GetDouble();

    value = document["latency"];
    latency = value.GetDouble();
}

template<bool Const, class ValueT>
Connection::Connection(GenericArray<Const, ValueT>& jsonArrayValue) {
    latency = jsonArrayValue["latency"];
    bandwidth = jsonArrayValue["bandwidth"];
    Smax = jsonArrayValue["Smax"];
}

double Connection::clamp(double x, double min, double max) {
    if (x < min) return min;
    if (x > max) return max;
    return x;
}

double Connection::ratio(double Ps) {
    if (clamp(Ps-Smax, 0, Ps) != 0) {
        double fakeData = clamp(Ps, 0., Smax) * 2 + clamp(Ps-Smax, 0, Ps);
        return Ps / fakeData;
    } else {
        return (0.5 * Ps * Ps) / (Smax * Smax);
    }
}

double Connection::networkTime(double Ps) {
    //return latency + Ps / (bandwidth * ratio(Ps));
    return latency + Ps * (1.0 + checksumRatio) / bandwidth;
}

double Connection::ackTime() {
    return latency;
}


double Connection::getBandwidth() const {
    return bandwidth;
}

void Connection::parseString(const char* json) {
    Document document;
    document.Parse(json);
    Value& value = document["a"];
    Value& value2 = document["b"];
    int valueRead = value.GetInt();
    const char* stringRead = value2.GetString();
    std::cout << "a:" << valueRead << '\n';
    std::cout << "b:" << stringRead << '\n';
    //std::cout << document["a"] << '\n';
    //std::cout << document["b"] << '\n';
}

double Connection::getSMax() const { return Smax; }
double Connection::getLatency() const { return latency; }

std::pair<int, int> Connection::getEdges() const {
    return edges;
}