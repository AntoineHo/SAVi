#ifndef MAIN_H_INCLUDED
#define MAIN_H_INCLUDED

// STANDARD MODULES
#include <iostream> // Preprocessor indication > read/write from/to console
#include <string> // Necessary to use strings
#include <vector> // Necessary to use dynamically allocated tables
#include <fstream> // Necessary to read/write from/to files
#include <cstring> // Necessary to use c_string functions ex: strtok
#include <cstdlib> // Necessary to use strtol
#include <unistd.h> // Necessary for page_size
#include <algorithm>    // std::sort
#include <cmath>
#include <sqlite3.h> // Necessary to build a db file
#include <sstream> // Necessary to use std::to_string

// LOCAL MODULES
#include "classes.h"
#include "svg.h"


// DECLARATION OF DEFINES
#define MAX_STRING_SIZE 1024 // Defined string size for reading .paf file

// PROTOTYPES OF FUNCTIONS

/**
 * \brief Function that returns a true if filepath exists
 * \param filepath const std::string& a reference to the string containing the .info filepath
 * \return bool
 **/
inline bool fileExist(const std::string& filepath);

/**
 * \brief Function that just prints help to std::cout
 * \return Nothing
 **/
void printHelp();

/**
 * \brief Function that checks if the extension of a file matches to what should be
 * \param filepath const std::string& a reference to the string containing the filepath
 * \param ext const std::string& a reference to the string containing the extension
 * \return bool
 **/
bool checkExtension(const std::string& filePath, const std::string& ext);

/**
 * \brief Function that reads a .SPT (SPLITTED PAF)
 * \param filepath const std::string& a reference to the string containing the filepath
 * \param chrLength int& a reference to the variable containing the target length
 * \param chrLength std::string& a reference to the variable containing the target name
 * \return a list of Contig objects
 **/
//std::vector<Contig> readSPT(std::string &sptFilePath, int &chrLength, std::string &chrName);


/**
 * \brief Function that outputs a .SVG from a contig vector
 * \param ctgList     std::vector<Contig>&  a reference to the vector containing all contigs to represent
 * \param chrLength   int                   integer length of the chromosome to display
 * \param offset      int                   space between contigs
 * \param zoom        int                   zoom parameter, contigs smaller than this value won't be represented
 * \param col1        svg::Color            SVG::Color object
 * \param col2        svg::Color            SVG::Color object
 * \param col3        svg::Color            SVG::Color object
 * \param Yoffset     int                   up and down offset (if 0 sticks to border)
 * \param showLinks   bool                  bool to decide whether we show links were alignment starts and stops
 * \param showInfo    bool                  bool to decide whether we show contigs relative length
 * \param onlyAligned bool                  bool to decide whether we show only alignment blocks
 * \param targetName  std::string           string containing the target name of chromosome (in QUERY option of minimap2)
 * \param SVGFilePath std::string           path to which svg is outputted
 **/
void buildGraph(std::vector<Contig>& ctgList, int& chrLength, int& offset, int& zoom, svg::Color& col1, svg::Color& col2, svg::Color& col3, int& Yoffset, bool& showLinks, bool& showInfo, bool& total, std::string& targetName, std::string& SVGFilePath);

/**
 * \brief Function that pus args into a SVG::Color object
 * \param char* character array containing rgb 0-255 values ";" separated
 **/
svg::Color getColorFromArg(char *arg);

/**
 * \brief Function that reads a .DB
 * \param filepath    const std::string&  a reference to the string containing the filepath
 * \param chrLength   int&                a reference to the variable containing the target length
 * \param targetName  std::string&        a reference to the variable containing the target name
 * \return a list of Contig objects
 **/
std::vector<Contig> readDB(std::string &dbFilePath, std::string &targetName, int * chrLength);

/**
 * \brief function that converts ints to strings
 * \param number int to convert
 * \return std::string converted from int
**/
std::string toString(int number);

#endif
