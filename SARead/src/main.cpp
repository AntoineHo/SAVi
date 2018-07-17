#include "main.h"

int main(int argc, char* argv[]) {
	// Check the number of parameters
  if (argc < 2 || argc > 3) {
      // Tell the user how to run the program
      std::cerr << "Usage:\n" << "SARead\t../valid/file/path/file.paf" << std::endl;
      return 1;
  }

  std::string watarg(argv[1]);
  if (watarg == "-h") {
    std::cerr << "Reads a .paf file" << std::endl;
    std::cerr << std::endl;
    std::cerr << "SARead infile\tLaunch SARead" << std::endl;
    std::cerr << "SARead -h [--help]\tPrints this message" << std::endl;
    return 1;
  }

  std::cout << "Checking if file is readable...\t\t";
	std::string filename(argv[1]);
	std::ifstream paFlux(filename.c_str());
	if (!paFlux) {
		std::cout << "Could not read: " << filename << std::endl;
		return 1; // Terminates with error !
	}
  std::cout << "OK" << std::endl;

  std::cout << "Counting lines in file...\t\t\t";
  // Gathers the file size for the loop
  std::string currentLine;
  int lineCount(0); // Count of the lines in file that actually contain a contig info
  int curl(0); // total line count
  while (getline(paFlux, currentLine)) {
		if (currentLine[0] != '#') {
      lineCount++;
		}
    curl++;
  }
  std::cout << curl << std::endl;

  std::cout << "Checking if database exists...\t\t";
  std::string dbFile(filename + ".db"); // Creates a string with .sql filename
  // Checking if database exists
  if (fileExist(dbFile)) {
    std::cerr << "DATABASE ERROR: This database already exists!" << std::endl;
    return 1;
  }
  std::cout << "OK" << std::endl;

  // Handles the DATABASE
  sqlite3 *db; // declare a SQLITE3 object
  sqlite3_stmt * stmt;
  char *zErrMsg = 0; // Sets the error message pointer
  const char *tail = 0;
  int rc; // Creates a handler
  char sSQL [MAX_STRING_SIZE] = "\0";

  std::cout << "Creating database...\t\t\t\t";
  rc = sqlite3_open(dbFile.c_str(), &db); // Opens the database
  if (rc) {
    std::cerr << "DATABASE ERROR: Cannot create the database file!\n" << sqlite3_errmsg(db) << std::endl;
    return 1;
  } else {
    std::cout << "CREATED" << std::endl;
    std::cout << "Database path:" << std::endl << dbFile << std::endl;
  }

  std::cout << "Creating table ALIGNED...\t\t\t";
  // CREATE A SQL COMMAND
  const char *sql = "CREATE TABLE ALIGNED(ID INT PRIMARY KEY NOT NULL, QNAME TEXT, QLENGTH INT, QSTA INT, QEND INT, REL INT, TNAME TEXT, TLENGTH INT, TSTA INT, TEND INT, MPQ INT);";

  // EXECUTE SQL COMMAND
  rc = sqlite3_exec(db, sql, callback, 0, &zErrMsg);
  // Check if the table is created
  if (rc != SQLITE_OK) {
    sqlite3_free(zErrMsg);
  } else {
    std::cout << "CREATED" << std::endl;
  }

  /* // FROM STACKOVERFLOW
  By default, SQLite will pause after issuing a OS-level write command.
  This guarantees that the data is written to the disk.
  By setting synchronous = OFF, we are instructing SQLite to simply hand-off the data to the OS for writing and then continue.
  There's a chance that the database file may become corrupted if the computer suffers
  a catastrophic crash (or power failure) before the data is written to the platter
  */
  sqlite3_exec(db, "PRAGMA synchronous = OFF", NULL, NULL, &zErrMsg);

  /* // FROM STACKOVERFLOW
  Consider storing the rollback journal in memory
  by evaluating PRAGMA journal_mode = MEMORY.
  Your transaction will be faster,
  but if you lose power or your program crashes during a transaction
  your database could be left in a corrupt state with a partially-completed transaction
  */
  sqlite3_exec(db, "PRAGMA journal_mode = MEMORY", NULL, NULL, &zErrMsg);

  // Resetting file flux
  paFlux.clear();
  paFlux.seekg(0, std::ios::beg);
  // Sets a progress bar
  ProgressBar myProgress(50, curl, "Filling table: ");

  // PREPARING THE DB (BEFORE THE LOOP!)
  std::sprintf(sSQL, "INSERT INTO ALIGNED VALUES (@ID, @QNA, @QLE, @QST, @QEN, @REL, @TNA, @TLE, @TST, @TEN, @MPQ)");
  sqlite3_prepare_v2(db, sSQL, MAX_STRING_SIZE, &stmt, &tail);
  // Beginning transaction
  sqlite3_exec(db, "BEGIN TRANSACTION", NULL, NULL, &zErrMsg);

  currentLine = "";
  int i(0);
  int nbl(0); //(real index of each line)
  // For each line in file
  while (getline(paFlux, currentLine)) {
    if (currentLine[0] == '#') { // Skipping comments
      i+1;
      continue;
		}
    sqlite3_bind_text(stmt, 1, toString(nbl).c_str(), -1, NULL);
    // Get current line length
		int stringLength(currentLine.length());
		// Creates a char array
		char c_array[stringLength + 1];
    // Converts string to char array
		strcpy(c_array, currentLine.c_str());

    int position(0);
    char *token(strtok(c_array, "\t"));
		while (token != NULL) {
      switch (position) {
        case 0: sqlite3_bind_text(stmt, 2, token, -1, SQLITE_STATIC); break;    // QUERY NAME
        case 1: sqlite3_bind_text(stmt, 3, token, -1, SQLITE_STATIC); break;    // QUERY LENGTH
        case 2: sqlite3_bind_text(stmt, 4, token, -1, SQLITE_STATIC); break;    // QUERY START
        case 3: sqlite3_bind_text(stmt, 5, token, -1, SQLITE_STATIC); break;    // QUERY END

        case 4:
          if (token[0] == '+') {
            sqlite3_bind_text(stmt, 6, "1", -1, SQLITE_STATIC);                 // RELATIVE STRAND
          } else {
            sqlite3_bind_text(stmt, 6, "0", -1, SQLITE_STATIC);
          }
          break;

        case 5: sqlite3_bind_text(stmt, 7, token, -1, SQLITE_STATIC); break;    // TARGET NAME
        case 6: sqlite3_bind_text(stmt, 8, token, -1, SQLITE_STATIC); break;    // TARGET LENGTH
        case 7: sqlite3_bind_text(stmt, 9, token, -1, SQLITE_STATIC); break;    // TARGET START
        case 8: sqlite3_bind_text(stmt, 10, token, -1, SQLITE_STATIC); break;   // TARGET END

        case 11: sqlite3_bind_text(stmt, 11, token, -1, SQLITE_STATIC); break;  // MAPPING QUALITY
      }
      position++;
      token = strtok(NULL, "\t");
    }
    sqlite3_step(stmt);
    sqlite3_reset(stmt);
    nbl++;
  }
  paFlux.close();
  sqlite3_exec(db, "END TRANSACTION", NULL, NULL, &zErrMsg);
  sqlite3_finalize(stmt);

  // Closes the database
  sqlite3_close(db);
  std::cout << "Database is ready to use..." << std::endl;
	return 0;
}

// FUNCTIONS
inline bool fileExist(const std::string& filepath) {
    return (access(filepath.c_str(), F_OK) != -1);
}

static int callback(void *NotUsed, int argc, char **argv, char **azColName) {
   int i;
   for(i = 0; i<argc; i++) {
      printf("%s = %s\n", azColName[i], argv[i] ? argv[i] : "NULL");
   }
   printf("\n");
   return 0;
}

std::string toString(int number) {
  std::string toReturn;
  std::stringstream strstream;
  strstream << number;
  strstream >> toReturn;
  return toReturn;
}
