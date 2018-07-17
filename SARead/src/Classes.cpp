#include "Classes.h" 

using namespace std; //

Chromosome::Chromosome(std::string p_name, int p_length, int p_ctgNbr, int p_totalAlignedLength) : name(p_name),
  length(p_length), ctgNbr(p_ctgNbr), totalAlignedLength(p_totalAlignedLength)
{ /* Nothing here as everything is set above */ }

std::string Chromosome::getName() {
  return name;
}
int Chromosome::getLength() {
  return length;
}

int Chromosome::getCtgNber(){
  return ctgNbr;
}

int Chromosome::getAlignedLength() {
  return totalAlignedLength;
}

std::vector<int> Chromosome::getLineList(){
  return linesConcerned;
}

void Chromosome::setLength(int newLength) {
  length = newLength;
}

void Chromosome::setCtgNber(int newCtgNumber){
  ctgNbr = newCtgNumber;
}

void Chromosome::setAlignedLength(int newTotalAlignedLength) {
  totalAlignedLength = newTotalAlignedLength;
}

void Chromosome::addToLength(int lengthToAdd){
  totalAlignedLength += lengthToAdd;
}

void Chromosome::addToCtgNbr(int nbrToAdd) {
  ctgNbr += nbrToAdd;
}

void Chromosome::addLine(int lineNbr) {
  linesConcerned.push_back(lineNbr);
}

void Chromosome::printLinesToFile(std::ofstream& outFlux) {
  for (int i(0); i < linesConcerned.size(); i++) {
    outFlux << linesConcerned[i] << ";";
  }
  outFlux << endl;
}

ProgressBar::ProgressBar(int plength, int ptotal, std::string pmsg) : length(plength), total(ptotal), msg(pmsg)
{
  setStep(); // Calculates step
}

int ProgressBar::getLength(){
  return length;
}

int ProgressBar::getTotal() {
  return total;
}

void ProgressBar::setStep() {
  step = total/length;
  //std::cout << std::endl << "Total:" << total << std::endl << "length: " << length << std::endl << "Step:" << step << std::endl;
}

void ProgressBar::printProgress(int pCurrent) {
  if (step != 0) {
    //0 would mean TOO FEW OPERATIONS!
    int toPrint(0);
    toPrint = pCurrent/step;
    if (pCurrent == total) {
      std::string eqString("");
      for (int i(0); i < length-1; i++) {
        eqString += "=";
      }
      std::cout << msg << " [" << eqString << "] " << std::endl;
    } else if (toPrint == 0) {
      std::string emptyString("");
      for (int i(0); i < length-1; i++) {
        emptyString += " ";
      }
      std::cout << msg << " [" << emptyString << "]" << "\r";
    } else {
      std::string eqString("");
      std::string emptyString("");
      for (int i(0); i < toPrint-1; i++) {
        eqString += "=";
      }
      for (int i(0); i < length - toPrint - 1; i++) {
        emptyString += " ";
      }
      eqString += ">";
      std::cout << msg << " [" << eqString << emptyString << "]" << "\r";
    }
  }
}
