#ifndef CONNECTION_H
#define CONNECTION_H

#include "rapidjson/document.h"
#include <iostream>
#include <iomanip>
#include <fstream>
#include "utils.h"

using std::ostream;
using namespace rapidjson;

class Connection {
private:
    static const double ackSize; //64 Byte
    static const double checksumRatio;
    double Smax, bandwidth, latency;
    bool usable;
    std::pair<int,int> edges;
    std::string idName;
    double clamp(double x, double min, double max);
protected:
public:
    Connection(double _Smax = 0.0, double __bandwidth = 0.0,  
        double __latency=0.0, std::pair<int, int> __edges = {0, 0});
    Connection(const char* jsonPath);

    double ratio (double Ps);
    double networkTime(double Ps);
    double ackTime();
    bool broaderThan(const Connection& c) const;
    bool lessLatencyThan(const Connection& c) const;
    void makeWorstConnectionEver();

    //gets
    double getBandwidth() const;
    double getSMax() const;
    double getLatency() const;
    bool isUsable() const;
    std::pair<int, int> getEdges() const;

    //sets
    void setUsable(bool newValue);
    void setBandwidth(double newBandwidth);


    void parseString(const char* json);
    Connection operator+(Connection lhs);
};

inline ostream& operator<<(ostream& stream, const Connection& c) {
    stream
        << std::setw(15) << "bandwidth: " << c.getBandwidth() << std::endl
        << std::setw(15) << "Smax: " << c.getSMax() << std::endl
        << std::setw(15) << "latency: " << c.getLatency() << std::endl
        << std::setw(15) << "edges: " << c.getEdges().first << " <---> "
                                      << c.getEdges().second << std::endl
        << '\n';
    return stream;
}

#endif
