#include "main.h"
// NOW 15:01
using namespace svg;

// FUNCTIONS
int main(int argc, char* argv[]) {
	// Check the number of parameters
	if (argc != 2 && argc != 11) {
		std::cout << "WARNING: Bad argument number!" << std::endl;
		// Tell the user how to run the program
		printHelp();
		return 1;
	}

	std::string firstArg(argv[1]);
	if (firstArg == "-h" || firstArg == "--help" || firstArg == "help") {
		printHelp();
		return 1;
	}

	// Sets variable
	std::string dbFilePath(argv[1]);
	std::cout << "Checking if database exists...\t";
  // Checking if database exists
  if (!(fileExist(dbFilePath))) {
    std::cerr << "DATABASE ERROR: Cannot find " << dbFilePath << " !" << std::endl;
    return 1;
  }
  std::cout << "OK" << std::endl;

	// Building config from ARGS
	std::cout << "Checking options...\t\t\t"; 													// DEBUG << std::endl;

	int offset(strtol(argv[2], NULL, 10));												// Separation between aligns
	//std::cout << "Separation:\t\t" << offset << std::endl;			// DEBUG

	int yoffset(strtol(argv[4], NULL, 10));												// Y offset before and after chromosome
	//std::cout << "Y offset:\t\t" << yoffset << std::endl; 			// DEBUG

	int zoomFactor(strtol(argv[3], NULL, 10));										// Zoom factor
	//std::cout << "Zoom factor:\t\t" << zoomFactor << std::endl;	// DEBUG

	bool showLinks(true);																					// Show branching of chromosomes
	if (std::string(argv[5]) != "y") {														// If arg is != y -> False
		showLinks = false;																					// set FALSE
	}
	//std::cout << "Show links:\t\t" << showLinks << std::endl; 	// DEBUG

	svg::Color c1(getColorFromArg(argv[6]));											// Color of central chromosome
	//std::cout << "Chrom color:\t\t" << c1.print() << std::endl; // DEBUG

	svg::Color c2(getColorFromArg(argv[7]));											// Color of - strand
	//std::cout << "+ color:\t\t" << c2.print() << std::endl; 		// DEBUG

	svg::Color c3(getColorFromArg(argv[8]));											// Color of + strand
	//std::cout << "- color:\t\t" << c3.print() << std::endl; 		// DEBUG

	bool showInfo(true);																					// Show info on graph
	//std::cout << std::string(argv[9]) << std::endl; 						// DEBUG
	if (std::string(argv[9]) != "y") {
		showInfo = false;
	}
	//std::cout << "Show info:\t\t" << showInfo << std::endl; 		// DEBUG

	std::string targetName(argv[10]);															//Target Name
	//std::cout << "Target name:\t\t" << targetName << std::endl; // DEBUG

	std::cout << "OK" << std::endl;

	// SELECTING FROM DATABASE AND CREATING THE CONTIGLIST
	int chrLength(0);																															// Setting a var chrLength
	std::vector<Contig> ctgList(readDB(dbFilePath, targetName, &chrLength));			// Setting a contig list
	std::cout << "Sorting block list...\t\t\t";																				// Sorting the list
	std::sort(ctgList.begin(), ctgList.end());
  std::cout << "OK" << std::endl;

	std::cout << "Creating .svg figure...\t\t\t";																			// Setting a string with SVGFilePath
	std::string SVGFilePath(dbFilePath.substr(0, dbFilePath.find_last_of("\\/")+1) + targetName + ".svg");
  buildGraph(ctgList, chrLength, offset, zoomFactor, c1, c2, c3, yoffset, showLinks, showInfo, targetName, SVGFilePath);
	std::cout << "OK" << std::endl;
	std::cout << "Output path:\n" << SVGFilePath << std::endl;
  return 0;
}

std::vector<Contig> readDB(std::string &dbFilePath, std::string &targetName, int * chrLength) {
	// Handles the DATABASE
	sqlite3 *db; // declare a SQLITE3 object
	sqlite3_stmt * stmt;
	char *zErrMsg = 0; // Sets the error message pointer
	const char *tail = 0;
	int rc; // Creates a handler
	char sSQL [MAX_STRING_SIZE] = "\0";

	std::cout << "Opening database...\t\t\t";
	rc = sqlite3_open(dbFilePath.c_str(), &db); // Opens the database
	if (rc) {
		std::cout << "DATABASE ERROR: Cannot open the database file!\n" << sqlite3_errmsg(db) << std::endl;
		std::exit(1);
	} else {
		std::cout << "OPENED" << std::endl;
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

	// Gets the number of different queries
	std::cout << "Counting queries...\t\t\t";
  int count(0);
  std::string sql("SELECT COUNT(*) FROM ALIGNED WHERE TNAME = '" + targetName + "'");
	//std::cout << sql << std::endl;
  rc = sqlite3_prepare_v2(db, sql.c_str(), MAX_STRING_SIZE, &stmt, &tail);
  if (rc != SQLITE_OK) {
    std::cerr << "DATABASE ERROR: Cannot select!" << std::endl;
    sqlite3_free(zErrMsg);
  } else {
		rc = sqlite3_step(stmt);
		int ncols(sqlite3_column_count(stmt));
		while (rc == SQLITE_ROW) {
			for (int i(0); i < ncols; i++) {
				std::string result(reinterpret_cast<const char *>(sqlite3_column_text(stmt, i)));
				count = strtol(result.c_str(), NULL, 10);
			}
			rc = sqlite3_step(stmt);
		}
  }
	sqlite3_reset(stmt);
	std::cout << count << std::endl;

	// Gets the number of different queries
	std::cout << "Fetching target info...\t\t\t";
  sql = "SELECT TLENGTH FROM ALIGNED WHERE TNAME = '" + targetName + "' LIMIT 1;";
	//std::cout << sql << std::endl;
  rc = sqlite3_prepare_v2(db, sql.c_str(), MAX_STRING_SIZE, &stmt, &tail);
  if (rc != SQLITE_OK) {
    std::cerr << "DATABASE ERROR: Cannot select!" << std::endl;
    sqlite3_free(zErrMsg);
  } else {
		rc = sqlite3_step(stmt);
		int ncols(sqlite3_column_count(stmt));
		while (rc == SQLITE_ROW) {
			for (int i(0); i < ncols; i++) {
				std::string result(reinterpret_cast<const char *>(sqlite3_column_text(stmt, i)));
				*chrLength = strtol(result.c_str(), NULL, 10);
			}
			rc = sqlite3_step(stmt);
		}
  }
	sqlite3_reset(stmt);
	std::cout << *chrLength << " bp" << std::endl;

	// Selecting all queries
	std::cout << "Building contig list...\t\t\t";
	// Declares a vector of contigs
	std::vector<Contig> ctgList;
	// SELECT STMT
	sql = "SELECT * FROM ALIGNED WHERE TNAME = '" + targetName + "'";
	//std::cout << sql << std::endl;
  rc = sqlite3_prepare_v2(db, sql.c_str(), MAX_STRING_SIZE, &stmt, &tail);
  if (rc != SQLITE_OK) {
    std::cerr << "DATABASE ERROR: Cannot select!" << std::endl;
    sqlite3_free(zErrMsg);
  } else {
		rc = sqlite3_step(stmt);
		int ncols(sqlite3_column_count(stmt));
		while (rc == SQLITE_ROW) {
			Contig newContig;
			for (int i(0); i < ncols; i++) {
				std::string result(reinterpret_cast<const char *>(sqlite3_column_text(stmt, i)));
				switch (i) {
	        case 1: newContig.setQName(result); break;    													// QUERY NAME
	        case 2: newContig.setQLength(strtol(result.c_str(), NULL, 10)); break;  // QUERY LENGTH
					case 3: newContig.setQStart(strtol(result.c_str(), NULL, 10)); break;  	// QUERY START
					case 4: newContig.setQEnd(strtol(result.c_str(), NULL, 10)); break; 		// QUERY END
					case 5: 																																// RELATIVE STRAND
						if (result == "1") {
							newContig.setRelStrand(true);
						} else {
							newContig.setRelStrand(false);
						}
					break;
					case 8: newContig.setTStart(strtol(result.c_str(), NULL, 10)); break;  	// TARGET START
					case 9: newContig.setTEnd(strtol(result.c_str(), NULL, 10)); break;  		// TARGET END
					case 10: newContig.setMPQ(strtol(result.c_str(), NULL, 10)); break; 		// MAPPING QUALITY
	      }

			}
			ctgList.push_back(newContig);
			rc = sqlite3_step(stmt);
		}
  }
	sqlite3_reset(stmt);
	sqlite3_finalize(stmt);
	sqlite3_close(db);
	std::cout << "OK" << std::endl;

	std::cout << "Contig list size...\t\t\t\t";
	std::cout << ctgList.size() << std::endl;
	return ctgList;
}

void buildGraph(std::vector<Contig> ctgList, int chrLength, int offset, int zoom, svg::Color col1, svg::Color col2, svg::Color col3, int Yoffset, bool showLinks, bool showInfo, std::string targetName, std::string SVGFilePath) {
	int lstSize(ctgList.size());

	// Initializes row lists
	std::vector<Row> minusRowLst;
	std::vector<Span> newSpanList1;
	minusRowLst.push_back(Row(newSpanList1));

	std::vector<Row> plusRowLst;
	std::vector<Span> newSpanList2;
	plusRowLst.push_back(Row(newSpanList2));

	for (int i(0); i < lstSize; i++) { // FOR EACH CTG IN LIST
		// GETS THE VARIABLES
		bool plus(ctgList[i].getRelStrand());
		// SPAN: Yposition of drawn block -> Yposition + (length of contig)
		// Y start position of contig relative to chromosome = chrStart - contig start of alignment
		int ctgSpan1(ctgList[i].getChrStart() - ctgList[i].getStart());
		// Y end position of contig relative to chromosome = ctgSpan1 + length of contig
		int ctgSpan2(ctgSpan1 + ctgList[i].getLength());
		std::string ctgName(ctgList[i].getName());

		/*DEBUG
		std::cout << std::endl;
		if (plus) {
			std::cout << "Current contig + : " << ctgSpan1 << " - " << ctgSpan2 << std::endl;
		} else {
			std::cout << "Current contig - : " << ctgSpan1 << " - " << ctgSpan2 << std::endl;
		}
		*/

		if (plus) { // Loops through PLUS ROW LIST
			for (int j(0); j < plusRowLst.size(); j++) {

				if (!(plusRowLst[j].inSpan(ctgSpan1, ctgSpan2, offset))) { // Checks if contig is in span (+ 10 bp of sep min)
					plusRowLst[j].addSpan(ctgSpan1, ctgSpan2); // Adds a soan to current row
					ctgList[i].setRow(j); // Sets the row nb to current contig
					//std::cout << "Added to row: " << j << std::endl;
					break; // Stops the loop

				} else { // CONTIG IS NOT IN SPAN
					if (j == plusRowLst.size() - 1) { // If last row of list
						std::vector<Span> newSpanList; // Create a span list
						newSpanList.push_back(Span(ctgSpan1, ctgSpan2)); // Adds current span
						plusRowLst.push_back(Row(newSpanList)); // Adds a new row to row list
						ctgList[i].setRow(j+1);
						//std::cout << "Added to row: " << j+1 << std::endl;
						break;
					}
				}
			}
		} else { // Loops through MINUS ROW LIST
			for (int j(0); j < minusRowLst.size(); j++) {

				if (!(minusRowLst[j].inSpan(ctgSpan1, ctgSpan2, offset))) { // Checks if contig is in span (+ 10 bp of sep min)
					minusRowLst[j].addSpan(ctgSpan1, ctgSpan2); // Adds a soan to current row
					ctgList[i].setRow(j); // Sets the row nb to current contig
					//std::cout << "Added to row: " << j << std::endl;
					break; // Stops the loop

				} else { // CONTIG IS NOT IN SPAN
					if (j == minusRowLst.size() - 1) { // If last row of list
						std::vector<Span> newSpanList; // Create a span list
						newSpanList.push_back(Span(ctgSpan1, ctgSpan2)); // Adds current span
						minusRowLst.push_back(Row(newSpanList)); // Adds a new row to row list
						ctgList[i].setRow(j+1);
						//std::cout << "Added to row: " << j+1 << std::endl;
						break;
					}
				}
			}
		}
	}

	// Sets the dimensions
	int nM(minusRowLst.size());
	//std::cout << "nM: " << nM << std::endl;
	int nP(plusRowLst.size());
	//std::cout << "nP: " << nM << std::endl;
	Dimensions dimensions(30*nM + 30*nP + 40, (chrLength/zoom) + 2*Yoffset);

	// Creates the svg file
  Document doc(SVGFilePath, Layout(dimensions, Layout::TopLeft));


	// Red image border.
	Polygon border(std::string("-"), Stroke(1, Color::Red));
	border << Point(0, 0) << Point(dimensions.width, 0)
			<< Point(dimensions.width, dimensions.height) << Point(0, dimensions.height);
	doc << border;

	// Creates a chromosome left of minus rows
	// REMINDER: Rectangle(Point(origin x, origin y), width, height, color)
	std::stringstream ssChrom;
	ssChrom << targetName << ";" << chrLength << ";" << lstSize;
  doc << Rectangle(Point(30*nM+10, Yoffset), 20, chrLength/zoom, ssChrom.str(), col1);

	for (int i(0); i < lstSize; i++) { // FOR EACH CTG IN LIST
		Contig contig(ctgList[i]);
		bool plus(contig.getRelStrand());
		int rowNb(contig.getRow() + 1); // Rows are not 0 indexed below (easier compute)
		int tStart(contig.getChrStart()/zoom);
		int tEnd(contig.getChrEnd()/zoom);
		int qStart(contig.getStart()/zoom);
		int qEnd(contig.getEnd()/zoom);
		int qLength(contig.getLength()/zoom);

		// BUILDS THE STRAND INFO STRING
		std::stringstream ss;
		std::string strandInID;
		if (plus) {
			strandInID = "positive (+)";
		} else {
			strandInID = "negative (-)";
		}

		ss << contig.getName() << ";" << contig.getMapQual() << ";" << strandInID << ";"
				<< contig.getLength() << "bp" << ";" << contig.getChrStart() << " to " << contig.getChrEnd() << ";"
				<< contig.getStart() << " to " << contig.getEnd();
		std::string idString(ss.str());

		// DEBUG
		//std::cout << rowNb << "\t" << plus << "\t" << tStart << "\t" << tEnd << "\t" << qStart << "\t" << qEnd << "\t" << qLength  << std::endl;
		// END DEBUG

		// BLOCKS
		// Y position : Y offset + (T start - Q start)
		int blockYPosition(Yoffset + (tStart - qStart) ); // Y position of the block to draw (same on + & - sides of chr)

		// LINKS
		// up link 1 (ctg) y position : blockYPosition + Q start
		int upLink1Y(blockYPosition + qStart);
		// down link 1 (ctg) y position : blockYPosition + Q end
		int downLink1Y(blockYPosition + qEnd);
		// up link 2 (chrom) y position : Y offset + T start
		int upLink2Y(tStart + Yoffset);
		// down link 2 (chrom) y position : Y offset + T end
		int downLink2Y(tEnd + Yoffset);

		if (plus) { // If on the + side
			// NEEDS A X OFFSET -> xOffset : position right to the chromosome
			// BLOCKS
			int xOffsetPlusRow(30*nM + 30);
			int blockXPosition(30*rowNb - 20 + xOffsetPlusRow); // 30*rowNb - 20 : x position in rows

			// LINKS
			// LINKS ON CONTIG X POSITION = X POSITION OF THE CONTIG
			// LINKS ON CHROMOSOME X POSITION = X POSITION OF THE CHROMOSOME + 20 -> 30*(nM+1)
			int linksOnChromosomeXPosition(30*(nM+1));

			doc << Rectangle(Point(blockXPosition, blockYPosition), 20, qLength, idString, col2);
			if (showInfo && qLength != 0) {
				doc << Text(Point(blockXPosition+25, blockYPosition-2), toString(qLength), Color::Black, Font(10, "Verdana"));
			}

			// SHOW THE LINKS
			if (showLinks && qLength != 0) {
				Point upCtg(blockXPosition, upLink1Y);
				Point upChr(linksOnChromosomeXPosition, upLink2Y);
				Point downCtg(blockXPosition, downLink1Y);
				Point downChr(linksOnChromosomeXPosition, downLink2Y);

				doc << Line(upCtg, upChr, Stroke(0.2, Color::Red));
				doc << Line(downCtg, downChr, Stroke(0.2, Color::Black));
				//doc << (Polygon(Color(235, 235, 235), Stroke(0, Color(0, 0, 0))) << upCtg << upChr << downChr << downCtg);
			}


		} else { // If on the - side -> y = 0
			// NEEDS A REVERSE ROW SORTING -> actualRowNb left to right : Nb minus rows - current row nb + 1 (+1 because no row 0)
			int actualRowNb(nM-rowNb+1);
			int blockXPosition(30*actualRowNb-20);

			// LINKS
			// LINKS ON CONTIG X POSITION = X POSITION OF THE CONTIG + 20
			int linksOnContigXPosition(blockXPosition+20);
			// LINKS ON CHROMOSOME X POSITION = X POSITION OF THE CHROMOSOME -> 30*nM+10
			int linksOnChromosomeXPosition(30*nM+10);

			doc << Rectangle(Point(blockXPosition, blockYPosition), 20, qLength, idString, col3);
			if (showInfo && qLength != 0) {
				doc << Text(Point(blockXPosition-15, blockYPosition-2), toString(qLength), Color::Black, Font(10, "Verdana"));
			}

			// SHOW THE LINKS
			if (showLinks && qLength != 0) {
				Point upCtg(linksOnContigXPosition, upLink1Y);
				Point upChr(linksOnChromosomeXPosition, upLink2Y);
				Point downCtg(linksOnContigXPosition, downLink1Y);
				Point downChr(linksOnChromosomeXPosition, downLink2Y);

				doc << Line(Point(linksOnContigXPosition, upLink1Y), Point(linksOnChromosomeXPosition, upLink2Y), Stroke(0.2, Color::Red));
				doc << Line(Point(linksOnContigXPosition, downLink1Y), Point(linksOnChromosomeXPosition, downLink2Y), Stroke(0.2, Color::Black));
				//doc << (Polygon(Color(235, 235, 235), Stroke(0, Color(0, 0, 0))) << upCtg << upChr << downChr << downCtg);
			}
		}
	}
	doc.save();
}

inline bool fileExist(const std::string& filepath) {
    return (access(filepath.c_str(), F_OK) != -1);
}

void printHelp() {
	std::cerr << "SADisplay builds a graph from an alignment" << std::endl
	<< "Usage: " << std::endl
	<< "SADisplay database separation zoom y_offset show_links [y/n] chromosome_color plus_color minus_color show_info [y/n] target_name" << std::endl
	<< "SADisplay -h [--help]\tprints this message" << std::endl;
}

bool checkExtension(std::string const &filePath, std::string const &ext) {
	return filePath.substr(filePath.find_last_of(".") + 1) == ext;
}

svg::Color getColorFromArg(char *arg) {
	int col[3];
	char *token(strtok(arg, ","));
	for (int i(0); i < 3; i++) {
		col[i] = strtol(token, NULL, 10);
		if (col[i] > 255 || col[i] < 0) {
			return svg::Color::Black;
		}
		token = strtok(NULL, ",");
	}
	return svg::Color(col[0], col[1], col[2]);
}

std::string toString(int number) {
  std::string toReturn;
  std::stringstream strstream;
  strstream << number;
  strstream >> toReturn;
  return toReturn;
}
