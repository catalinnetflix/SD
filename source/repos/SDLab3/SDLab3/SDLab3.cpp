// SDLab3.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include <iostream>
#include <vector>
#include <string>
using namespace std;

struct KeyValue {
    string key;
    string value;
};

void format(vector<KeyValue>& pairs) {
    int maxLen = 0;

    for (int i = 0; i < pairs.size(); i++) {
        if (pairs[i].key.length() > maxLen) {
            maxLen = pairs[i].key.length();
        }
    }

    for (int i = 0; i < pairs.size(); i++) {
        cout << pairs[i].key;

        int spacesToAdd = maxLen - pairs[i].key.length();
        for (int j = 0; j < spacesToAdd; j++) {
            cout << " ";
        }

        cout << " = " << pairs[i].value << endl;
    }
}

int main() {
    vector<KeyValue> data;
    data.push_back({ "address", "192.168.1.1" });
    data.push_back({ "port", "22" });
    data.push_back({ "hostname", "name" });

    format(data);
    return 0;
}


