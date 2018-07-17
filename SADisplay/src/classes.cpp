#include "classes.h"

Span::Span(int x1, int x2) : start(x1), end(x2)
{ }

int Span::getStart() {
  return start;
}

int Span::getEnd() {
  return end;
}

Contig::Contig(std::string p_name, int p_alignedLength, int p_startPos,
  int p_endPos, int p_chrStartPos, int p_chrEndPos, bool p_relativeStrand,
  int p_mappingQuality) : name(p_name), alignedLength(p_alignedLength),
  startPos(p_startPos), endPos(p_endPos), chrStartPos(p_chrStartPos),
  chrEndPos(p_chrEndPos), relativeStrand(p_relativeStrand),
  mappingQuality(p_mappingQuality)
{ /* Nothing here as everything is set above */ }

Contig::Contig() { }

void Contig::print() {
  char a;
  if (relativeStrand) {
    a = '+';
  } else {
    a = '-';
  }
  std::cout << name << "\t" << alignedLength << "\t" << a << "\t" << mappingQuality << "\t" << chrStartPos << std::endl;
}

int Contig::getChrStart() {
  return chrStartPos;
}

int Contig::getChrEnd() {
  return chrEndPos;
}

int Contig::getLength() {
  return alignedLength;
}

bool Contig::getRelStrand() {
  return relativeStrand;
}

int Contig::getStart() {
  return startPos;
}

int Contig::getEnd() {
  return endPos;
}

int Contig::getMapQual() {
  return mappingQuality;
}

bool Contig::operator<(const Contig& ctgB) {
  return (chrStartPos < ctgB.chrStartPos);
}

bool Contig::operator>(const Contig& ctgB) {
  return (chrStartPos > ctgB.chrStartPos);
}

std::string Contig::getName() {
  return name;
}

void Contig::setAllAfterInit(std::string p_name, int p_alignedLength, int p_startPos,
  int p_endPos, int p_chrStartPos, int p_chrEndPos, bool p_relativeStrand,
  int p_mappingQuality) {
    name = p_name;
    alignedLength = p_alignedLength;
    startPos = p_startPos;
    endPos = p_endPos;
    chrStartPos = p_chrStartPos;
    chrEndPos = p_chrEndPos;
    relativeStrand = p_relativeStrand; //true = + & false = -
    mappingQuality = p_mappingQuality; //0 - 255
  }

void Contig::setQName(std::string qName) {
  name = qName;
}

void Contig::setQStart(int qStart) {
  startPos = qStart;
}

void Contig::setQEnd(int qEnd) {
  endPos = qEnd;
}

void Contig::setQLength(int qLength) {
  alignedLength = qLength;
}

void Contig::setTStart(int tStart) {
  chrStartPos = tStart;
}

void Contig::setTEnd(int tEnd) {
  chrEndPos = tEnd;
}

void Contig::setMPQ(int MPQ) {
  mappingQuality = MPQ;
}

void Contig::setRelStrand(bool relStrand) {
  relativeStrand = relStrand;
}

void Contig::setRow(int rowNb) {
  onRow = rowNb;
}

int Contig::getRow() {
  return onRow;
}

Row::Row(std::vector<Span> newSpanList) : spanList(newSpanList)
{ }

bool Row::inSpan(int x1, int x2, int minsep) {
  for (int i(0); i < spanList.size(); i++) {
    int start(spanList[i].getStart());
    int end(spanList[i].getEnd());
    if (x1 >= start - minsep && x1 <= end + minsep || x2 >= start - minsep && x2 <= end + minsep) {
      return true;
    }
  }
  return false;
}

void Row::addSpan(int x1, int x2) {
  spanList.push_back(Span(x1,x2));
}
