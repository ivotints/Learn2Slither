const int Board::DIRECTION_Y[4] = {0, -1, 0, 1};  // LEFT UP RIGHT DOWN
const int Board::DIRECTION_X[4] = {-1, 0, 1, 0};  // LEFT UP RIGHT DOWN

Board::Board() : length(3) {
    std::srand(static_cast<unsigned int>(std::time(nullptr)));
    std::memset(table, EMPTY, sizeof(table));
    init_snake();

}

void Board::set_cell_to_random_empty(int8_t value, int &y_out, int &x_out) {
    int y;
    int x;

    for (int i = 0; i < 100; ++i) {
        y = std::rand() % SIZE_Y;
        x = std::rand() % SIZE_X;
        if (table[y][x] == EMPTY) {
            table[y][x] = value;
            y_out = y;
            x_out = x;
            return ;
        }
    }
    y = 0;
    while (y < SIZE_Y) {
        x = 0;
        while (x < SIZE_X) {
            if (table[y][x] == EMPTY) {
                table[y][x] = value;
                y_out = y;
                x_out = x;
                return ;
            }
            x++;
        }
        y++;
    }
}
