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
#include <map> // Necessary to use a hashmap
#include <sstream> // Necessary to use std::to_string
#include <sqlite3.h> // Necessary to build a db file
#include <algorithm> // Necessary to use std::sort
// #include <cstdio> // Necessary to use strtol

// LOCAL MODULES
#include "Classes.h"

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
 * \brief callback function to use the database
 * \param NotUsed : void function unused
 * \param argc : int
 * \param argv : pointer to char array
 * \param azColName : pointer to char array
 * \return int
**/
static int callback(void *NotUsed, int argc, char **argv, char **azColName);

/**
 * \brief function that converts ints to strings
 * \param number int to convert
 * \return std::string converted from int
**/
std::string toString(int number);


#endif // INTRO_H_INCLUDED
