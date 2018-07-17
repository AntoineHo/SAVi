#ifndef CLASSES_H_INCLUDED
#define CLASSES_H_INCLUDED

// STANDARD MODULES
#include <iostream> // Preprocessor indication > read/write from/to console
#include <fstream> // Necessary to read/write from/to files
#include <string>
#include <vector>

// OBJECTS

class Chromosome {
public:
  Chromosome(std::string p_name, int p_length, int ctgNbr, int totalAlignedLength);
  std::string getName();
  int getLength();
  int getAlignedLength();
  int getCtgNber();
  std::vector<int> getLineList();
  void setLength(int newLength);
  void setAlignedLength(int newCtgNumber);
  void setCtgNber(int newTotalAlignedLength);
  void addToLength(int lengthToAdd);
  void addToCtgNbr(int nbrToAdd);
  void addLine(int lineNbr);
  void printLinesToFile(std::ofstream& outFlux);
private:
  std::string name;
  int length;
  int ctgNbr;
  int totalAlignedLength;
  std::vector<int> linesConcerned;
};

class ProgressBar {
public:
  ProgressBar(int plength, int ptotal, std::string pmsg);
  int getLength();
  int getTotal();
  void printProgress(int pCurrent);
  void setStep();
private:
  int length;
  int total;
  std::string msg;
  int step;
};

#endif
