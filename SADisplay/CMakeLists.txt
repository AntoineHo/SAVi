cmake_minimum_required (VERSION 2.8.12)
PROJECT(SADisplay)

## Sets version number
set (MAJOR 0)
set (MINOR 1)

INCLUDE_DIRECTORIES(${CMAKE_SOURCE_DIR}/include)
FILE(GLOB SOURCES ${CMAKE_SOURCE_DIR}/src/*.cpp)

ADD_EXECUTABLE(SADisplay ${SOURCES})

TARGET_LINK_LIBRARIES(SADisplay PUBLIC -lsqlite3)
