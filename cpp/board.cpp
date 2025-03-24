#include "include/board.hpp"
#include <ctime>
#include <cstring>

const int Board::DIRECTION_Y[4] = {0, -1, 0, 1};  // LEFT UP RIGHT DOWN
const int Board::DIRECTION_X[4] = {-1, 0, 1, 0};  // LEFT UP RIGHT DOWN

Board::Board() : length(3) {
    std::srand(static_cast<unsigned int>(std::time(nullptr)));
    std::memset(table, EMPTY, sizeof(table));
    init_snake();

}

void Board::init_snake() {
    set_cell_to_random_empty(HEAD, head_y, head_x);

}

void Board::set_cell_to_random_empty(int8_t value, int &y_out, int &x_out) {

    for (int i = 0; i < 100; ++i) {
        int y = std::rand() % SIZE_Y;
        int x = std::rand() % SIZE_X;
        if (set_to_empty(y, x, value)) {

        }
    }

}