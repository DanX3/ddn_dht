#include <iostream>
#include <fstream>
#include "model.h"
#include "stdlib.h"

void simulateTWrite(double indexStart, double indexStop, double step) {
    Connection ClientToHome(10., 1e3, 1e-3);
    Connection HomeToSecondary(0.5, 1e3, 1e-3);
    std::ofstream modelData;
    modelData.open("model.dat");
    for (double dataSize=indexStart; dataSize<indexStop; dataSize*=step) {
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
}

void printUsage(char** argv) {
    std::cout << "Usage: " << argv[0] << " n" << '\n'
        << '\t' << "0: T_write" << '\n';
}

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
    if (argc == 1) {
        printUsage(argv);
        return 1;
    }
    int indexChosen = atoi(argv[1]);
    if (indexChosen == 0) {
        simulateTWrite(1e-3, 1e3, 1.1);
    }
    else {
        printUsage(argv);
        return 1;
    }
    return 0;
}
#endif
