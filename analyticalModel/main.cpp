#include <iostream>
#include <fstream>
#include "connection.h"
#include "networkLayout.h"
#include "stdlib.h"

void simulateSend(double indexStart, double indexStop, double step) {
    Connection ClientToHome(10., 1e3, 1e-3);
    std::ofstream modelData;
    modelData.open("model.dat");
    for (double dataSize=indexStart; dataSize<indexStop; dataSize*=step) {
        double totalTime = 0.0;
        double metadataSize = dataSize * 0.03;
        totalTime += ClientToHome.networkTime(dataSize + metadataSize);
        //totalTime += HomeToSecondary.networkTime(metadataSize);
        totalTime += ClientToHome.ackTime();
        //totalTime += 2 * 1e-2; //log time
        //totalTime += ClientToHome.ackTime();
        modelData
            << dataSize << " "
            << totalTime << " "
            << totalTime-dataSize/ClientToHome.getBandwidth() << '\n';
    }
    modelData.close();
}

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
            << totalTime-dataSize/ClientToHome.getBandwidth() << '\n';
    }
    modelData.close();
}

void simulateJUMBO(double indexStart, double indexStop, double step, int JUMBORequestCount) {
    Connection ClientToHome(10., 1e3, 1e-3);
    Connection HomeToSecondary(0.5, 1e3, 1e-3);
    std::ofstream modelData;
    modelData.open("model.dat");
    for (double dataSize=indexStart; dataSize<indexStop; dataSize*=step) {
        double JUMBODatasize = dataSize * JUMBORequestCount;
        double totalTime = 0.0;
        double metadataSize = JUMBODatasize * 0.03;
        totalTime += ClientToHome.networkTime(JUMBODatasize + metadataSize);
        totalTime += HomeToSecondary.networkTime(metadataSize);
        totalTime += HomeToSecondary.ackTime();
        totalTime += 2 * 1e-2; //log time
        totalTime += ClientToHome.ackTime();
        modelData
            << dataSize << " "
            << totalTime / JUMBORequestCount << " "
            << totalTime / JUMBORequestCount - JUMBODatasize/ClientToHome.getBandwidth() << '\n';
    }
    modelData.close();
}

void printUsage(char** argv) {
    std::cout << "Usage: " << argv[0] << " n" << '\n'
        << '\t' << "0: T_write" << '\n'
        << '\t' << "1: T_Send" << '\n'
        << '\t' << "2: T_write JUMBO" << '\n';
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
    //------------------------------------------------------------------------
    std::string jsonPath{"networkLayout.json"};
    NetworkLayout layout(jsonPath);
    return 0;
    //------------------------------------------------------------------------


    if (argc == 1) {
        printUsage(argv);
        return 1;
    }
    int indexChosen = atoi(argv[1]);
    switch(indexChosen) {
        case 0: simulateTWrite(1e-3, 1e3, 1.1); break;
        case 1: simulateSend(1e-3, 1e3, 1.1); break;
        case 2: simulateJUMBO(1e-3, 1e3, 1.1, 100); break;
        default:
            printUsage(argv);
            return 1;
    }

    //Connection fakeConnection(1., 2., 3.);
    //const char* jsonToParse= "{\"a\":5,\"b\":\"wonderful\"}";
    //fakeConnection.parseString(jsonToParse);

    Connection jsonConnection("firstConnection.txt");
    std::cout << jsonConnection << '\n';

    return 0;
}
#endif
