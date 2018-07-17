#ifndef CLASSES_H_INCLUDED
#define CLASSES_H_INCLUDED

// STANDARD MODULES
#include <string>
#include <vector>
#include <iostream>
#include <algorithm>    // std::sort

// DECLARATION OF DEFINES
#define MAX_STRING_SIZE 1024 // Defined string size for reading .paf file

// CLASSES
class Contig {
public:
  Contig(std::string p_name, int p_alignedLength, int p_startPos,
    int p_endPos, int p_chrStartPos, int p_chrEndPos, bool p_relativeStrand,
    int p_mappingQuality);
  Contig();
  void print();
  // Others
  std::string getName();
  // FOR SORTING & THE MAPPING VISUALISATION
  int getChrStart();
  int getChrEnd();
  int getLength();
  bool getRelStrand();
  // FOR THE LINKS
  int getStart();
  int getEnd();
  // FOR SORTING
  bool operator<(const Contig& ctgB);
  bool operator>(const Contig& ctgB);
  // FOR INFO
  int getMapQual();
  // FOR SETTING
  void setAllAfterInit(std::string p_name, int p_alignedLength, int p_startPos,
    int p_endPos, int p_chrStartPos, int p_chrEndPos, bool p_relativeStrand,
    int p_mappingQuality);
  void setRow(int rowNb);
  void setQName(std::string qName);
  void setQStart(int qStart);
  void setQEnd(int qEnd);
  void setQLength(int qLength);
  void setTStart(int tStart);
  void setTEnd(int tEnd);
  void setMPQ(int MPQ);
  void setRelStrand(bool relStrand);
  int getRow();
private:
  std::string name;
  int alignedLength;
  int startPos;
  int endPos;
  int chrStartPos;
  int chrEndPos;
  bool relativeStrand; //true = + & false = -
  int mappingQuality; //0 - 255
  int onRow;
};

class Span {
public:
  Span(int x1, int x2);
  int getStart();
  int getEnd();
private:
  int start;
  int end;
};

class Row {
public:
  Row(std::vector<Span> newSpanList);
  bool inSpan(int x1, int x2, int minsep);
  void addSpan(int x1, int x2);
private:
  std::vector<Span> spanList;
};

#endif
