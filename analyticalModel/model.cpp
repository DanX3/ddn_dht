#include "model.h"

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

Connection::Connection(double __Smax, double __bandwidth, double __latency) :
    Smax(__Smax),
    bandwidth(__bandwidth),
    latency(__latency)
    {
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


