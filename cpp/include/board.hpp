#pragma once
#include <cstdlib>

class Board {
    public:
        static const int8_t EMPTY = 0;
        static const int8_t TAIL = 1;
        static const int8_t HEAD = 2;
        static const int8_t APPLE = 3;
        static const int8_t PEPPER = 4;

        static const int DIRECTION_Y[4];
        static const int DIRECTION_X[4];

        static const int SIZE_Y = 10;
        static const int SIZE_X = 10;

        static const int MAX_SNAKE_LENGTH = SIZE_X * SIZE_Y;

        Board();
        ~Board() = default;

        bool is_in_table(int y, int x) const;
        bool is_empty(int y, int x) const;
        bool set_to_empty(int y, int x, int8_t value);
        bool set_cell(int y, int x, int8_t value);
        int8_t get_cell(int y, int x) const;
        void set_cell_to_random_empty(int8_t value, int& y_out, int& x_out);
        bool make_move(int dir_y, int dir_x);

        int8_t table[SIZE_Y][SIZE_X];
        int head_y;
        int head_x;
        int tail_y;
        int tail_x;
        int moving_dir_y;
        int moving_dir_x;
        int length;

        int snake_y[MAX_SNAKE_LENGTH];
        int snake_x[MAX_SNAKE_LENGTH];
        int snake_size;

    private:
        void init_snake();
        void place_adjacent_segment(int y, int x, int& out_y, int& out_x);
};