#include <iostream>
#include <fstream>
#include "model.h"

#if PLOT
int main(int argc, char** argv) {
    Connection ClientToHome(1., 1e3, 1e-3);
    for (double Ps=2e-2; Ps<2e5; Ps*=1.1) {
        std::cout << Ps
            << " " << ClientToHome.ratio(Ps)
            << std::endl;
    }

    return 0;
}
#else
int main(int argc, char** argv) {
    Connection ClientToHome(10., 1e3, 1e-3);
    Connection HomeToSecondary(0.5, 1e3, 1e-3);
    std::ofstream modelData;
    modelData.open("model.dat");
    for (double dataSize=1e-3; dataSize<1e3; dataSize*=1.1) {
        double totalTime = 0.0;
        double metadataSize = dataSize * 0.03;
        totalTime += ClientToHome.networkTime(dataSize + metadataSize);
        totalTime += HomeToSecondary.networkTime(metadataSize);
        totalTime += HomeToSecondary.ackTime();
        totalTime += 2 * 1e-2; //log time
        totalTime += ClientToHome.ackTime();
        modelData
            << dataSize << " "
            << totalTime << " "
            << totalTime-dataSize/1e3 << '\n';
    }
    modelData.close();


    double totalTime = 0.0;
    double dataSize = 1e-3;
    double metadataSize = dataSize * 0.03;
    for (int i=0; i<100; i++) {
        totalTime += ClientToHome.networkTime(dataSize + metadataSize);
        totalTime += HomeToSecondary.networkTime(metadataSize);
        totalTime += HomeToSecondary.ackTime();
        totalTime += 2 * 1e-2; //log time
        totalTime += ClientToHome.ackTime();
    }
    std::cout << "100x small data" << totalTime << '\n';
    return 0;
}
#endif
