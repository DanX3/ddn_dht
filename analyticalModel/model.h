#ifndef CONNECTION_H
#define CONNECTION_H

class Connection {
private:
    static const double ackSize; //64 Byte
    static const double checksumRatio;
    double Smax, bandwidth, latency;
    double clamp(double x, double min, double max);
protected:
public:
    double ratio (double Ps);
    Connection(double _Smax, double __bandwidth,  double __latency);
    double networkTime(double Ps);
    double ackTime();
};
 #endif
