// FizzBuzzz.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include <iostream>
#include <stdio.h>
#include <stdlib.h>
using namespace std;

void fizzBuzzNormal(int n) {
    for (int i = 1; i <= n; i++) {
        if (i % 15 == 0)printf("Number: %d - FizzBuzz\n", i);
        else if (i % 3 == 0)printf("Number: %d - Fizz\n", i);
        else if (i % 5 == 0)printf("Number: %d - Buzz\n", i);
    }
}

void fizzBuzzBetter(int n, char* result) {
    for (int i = 1; i <= n; i++) {
        char buffer[50]; 
        if (i % 15 == 0) {
            strcat_s(buffer,1000, "FizzBuzz\n");
        }
        else if (i % 3 == 0) {
            strcat_s(buffer,1000, "Fizz\n");
        }
        else if (i % 5 == 0) {
            strcat_s(buffer,1000, "Buzz\n");
        }
        else strcat_s(buffer,1000, "*");

        strcat_s(result, 1000, buffer);

    }
}

int main()
{
    int n;
    cout << "Enter the number:";
    char result[1000] = "";
    cin >> n;
    fizzBuzzNormal(n);
    fizzBuzzBetter(n, result);
    printf("%s", result);
    return 0;


}

