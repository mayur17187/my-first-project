#include <iostream>
#include <vector>
#include <ncurses.h> // The library for terminal graphics
#include <cstdlib>   // For random numbers
#include <ctime>     // For time
#include <unistd.h>  // For usleep()

using namespace std;

// Structure to represent coordinates
struct Point {
    int x, y;
};

// --- CLASS: FOOD ---
class Food {
private:
    Point position;
    int maxWidth, maxHeight;

public:
    Food(int width, int height) : maxWidth(width), maxHeight(height) {
        spawn();
    }

    void spawn() {
        position.x = rand() % (maxWidth - 2) + 1;
        position.y = rand() % (maxHeight - 2) + 1;
    }

    Point getPosition() const { return position; }

    // Draw the food as a '#' or '@'
    void draw() {
        mvaddch(position.y, position.x, 'O'); // 'O' represents food
    }
};

// --- CLASS: SNAKE ---
class Snake {
private:
    vector<Point> body;
    Point direction;
    bool growing;

public:
    Snake(int startX, int startY) {
        body.push_back({startX, startY});
        body.push_back({startX - 1, startY});
        body.push_back({startX - 2, startY});
        direction = {1, 0}; // Moving right initially
        growing = false;
    }

    void changeDirection(int dx, int dy) {
        // Prevent 180-degree turns (can't go left if moving right)
        if ((direction.x == -dx && direction.y == 0) || (direction.y == -dy && direction.x == 0)) {
            return;
        }
        direction = {dx, dy};
    }

    void move() {
        Point newHead = {body[0].x + direction.x, body[0].y + direction.y};
        body.insert(body.begin(), newHead);

        if (!growing) {
            body.pop_back(); // Remove tail if not eating
        } else {
            growing = false;
        }
    }

    void grow() {
        growing = true;
    }

    bool checkCollision(int width, int height) {
        Point head = body[0];

        // Wall Collision
        if (head.x <= 0 || head.x >= width - 1 || head.y <= 0 || head.y >= height - 1) {
            return true;
        }

        // Self Collision
        for (size_t i = 1; i < body.size(); i++) {
            if (head.x == body[i].x && head.y == body[i].y) {
                return true;
            }
        }
        return false;
    }

    Point getHead() const { return body[0]; }

    void draw() {
        for (size_t i = 0; i < body.size(); i++) {
            if (i == 0)
                mvaddch(body[i].y, body[i].x, '0'); // Head
            else
                mvaddch(body[i].y, body[i].x, 'o'); // Body
        }
    }
};

// --- CLASS: GAME ---
class Game {
private:
    Snake snake;
    Food food;
    int width, height;
    int score;
    bool gameOver;

public:
    Game(int w, int h) : snake(w / 2, h / 2), food(w, h), width(w), height(h), score(0), gameOver(false) {
        initscr();            // Start ncurses
        cbreak();             // Line buffering disabled
        noecho();             // Don't echo user input
        curs_set(0);          // Hide cursor
        keypad(stdscr, TRUE); // Enable function keys (Arrow keys)
        nodelay(stdscr, TRUE); // Non-blocking input
        srand(time(0));       // Seed random number
    }

    ~Game() {
        endwin(); // End ncurses
    }

    void handleInput() {
        int ch = getch();
        switch (ch) {
            case KEY_UP: case 'w': snake.changeDirection(0, -1); break;
            case KEY_DOWN: case 's': snake.changeDirection(0, 1); break;
            case KEY_LEFT: case 'a': snake.changeDirection(-1, 0); break;
            case KEY_RIGHT: case 'd': snake.changeDirection(1, 0); break;
            case 'q': gameOver = true; break;
        }
    }

    void update() {
        snake.move();

        Point head = snake.getHead();
        Point foodPos = food.getPosition();

        // Eat Food
        if (head.x == foodPos.x && head.y == foodPos.y) {
            score += 10;
            snake.grow();
            food.spawn();
        }

        // Collision Check
        if (snake.checkCollision(width, height)) {
            gameOver = true;
        }
    }

    void draw() {
        clear(); // Clear screen

        // Draw Board Borders
        for (int i = 0; i < width; i++) {
            mvaddch(0, i, '#');
            mvaddch(height - 1, i, '#');
        }
        for (int i = 0; i < height; i++) {
            mvaddch(i, 0, '#');
            mvaddch(i, width - 1, '#');
        }

        // Draw Elements
        snake.draw();
        food.draw();

        // Draw Score
        mvprintw(0, 2, " Score: %d ", score);

        refresh(); // Push buffer to screen
    }

    void run() {
        while (!gameOver) {
            handleInput();
            update();
            draw();
            usleep(100000); // Delay in microseconds (controls speed)
        }
        showGameOver();
    }

    void showGameOver() {
        nodelay(stdscr, FALSE); // Make input blocking again for the exit screen
        clear();
        mvprintw(height / 2, width / 2 - 5, "GAME OVER!");
        mvprintw(height / 2 + 1, width / 2 - 10, "Final Score: %d", score);
        mvprintw(height / 2 + 3, width / 2 - 12, "Press any key to exit...");
        refresh();
        getch();
    }
};

int main() {
    // Standard terminal size is usually 80x24
    Game game(40, 20); 
    game.run();
    return 0;
}