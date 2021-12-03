import pygame
import random
from enum import Enum
from collections import namedtuple
import heapq
import numpy
import math
class Node():
  def __init__(self, x, y, type):
    self.x = x
    self.y = y
    self.type = type

    self.g = 0
    self.h = 0

    self.parent = None

    self.neighbors = []

  def __lt__(self, other):
    return (self.g + self.h) < (other.g + other.h)

pygame.init()
# font = pygame.font.Font('arial.ttf', 25)
font = pygame.font.SysFont('arial', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)

BLOCK_SIZE = 20
SPEED = 20


class SnakeGame:

    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()

        # init game state
        self.direction = Direction.RIGHT

        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head,
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]

        self.score = 0
        self.food = None
        self._place_food()

    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y)
        self.find_optimal_path()
        if self.food in self.snake:
            self._place_food()
            self.find_optimal_path()

    def find_optimal_path(self):
        node_grid = numpy.empty(shape=(32,24), dtype=numpy.object)

        #create node grid
        for i in range(node_grid.shape[0]):
            for j in range(node_grid.shape[1]):
                node_grid[i, j] = Node(i, j, "")
        #add start and hazard blocks
        shx = int(self.head.x/BLOCK_SIZE)
        shy = int(self.head.y/BLOCK_SIZE)
        s1 = Node(shx, shy, "X")
        node_grid[shx, shy] = s1

        for n in self.snake[1:]:
            x = int(n.x/BLOCK_SIZE)
            y = int(n.y/BLOCK_SIZE)
            node_grid[x, y] = Node(x, y, "X")


        #set up neighbour and compute heuristics
        for i in range(node_grid.shape[0]):
            for j in range(node_grid.shape[1]):

                min_distance = math.inf
                curr_distance = abs(node_grid[i, j].x - self.food.x) + abs(node_grid[i, j].y - self.food.y)
                if curr_distance < min_distance:
                    min_distance = curr_distance
                node_grid[i, j].h = min_distance

                curr_neighbors = []
                if i > 0 and node_grid[i - 1, j].type != "X":
                    curr_neighbors.append(node_grid[i - 1, j])
                if j > 0 and node_grid[i, j - 1].type != "X":
                    curr_neighbors.append(node_grid[i, j - 1])
                if i < node_grid.shape[0] - 1 and node_grid[i + 1, j].type != "X":
                    curr_neighbors.append(node_grid[i + 1, j])
                if j < node_grid.shape[1] - 1 and node_grid[i, j + 1].type != "X":
                    curr_neighbors.append(node_grid[i, j + 1])
                node_grid[i, j].neighbors = curr_neighbors

        #A* search
        frontier = []
        frontier.append(s1)
        heapq.heapify(frontier)
        explored_list = []
        final_node = None

        ebx = self.food.x/BLOCK_SIZE
        eby = self.food.y/BLOCK_SIZE

        while True:
            if frontier == []:
                break
            leaf = heapq.heappop(frontier)
            explored_list.append(leaf)
            if leaf.x == ebx and leaf.y == eby:
                final_node = leaf
                break
            for node in leaf.neighbors:
                curr_path_cost = leaf.g + 1
                if (node not in frontier and node not in explored_list or node in frontier and curr_path_cost < node.g):
                    node.parent = leaf
                    node.g = curr_path_cost
                    heapq.heappush(frontier, node)
        if final_node is None:
            final_node = explored_list.pop()

        temp = []
        while final_node is not None:
            temp.append(final_node)
            final_node = final_node.parent
        self.opt = temp[:-1]


    def agent_decide_dir(self):
        if len(self.opt) != 0:
            n = self.opt.pop()
        else:
            self.find_optimal_path()
            n = self.opt.pop()
        x = n.x - int(self.head.x/BLOCK_SIZE)
        y = n.y - int(self.head.y/BLOCK_SIZE)

        if x == 0:
            if y > 0:
                return Direction.DOWN
            else:
                return Direction.UP
        else:
            if x > 0:
                return Direction.RIGHT
            else:
                return Direction.LEFT

    def play_step(self):
        self.direction = self.agent_decide_dir()

        # 2. move
        self._move(self.direction) # update the head
        self.snake.insert(0, self.head)

        # 3. check if game over
        game_over = False
        if self._is_collision():
            game_over = True
            print("collision")
            return game_over, self.score

        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            self._place_food()
        else:
            self.snake.pop()

        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return game_over, self.score

    def _is_collision(self):
        # hits boundary
        if self.head.x > self.w - BLOCK_SIZE or self.head.x < 0 or self.head.y > self.h - BLOCK_SIZE or self.head.y < 0:
            return True
        # hits itself
        if self.head in self.snake[1:]:
            return True

        return False

    def _update_ui(self):
        self.display.fill(BLACK)

        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def _move(self, direction):
        x = self.head.x
        y = self.head.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)


if __name__ == '__main__':
    game = SnakeGame()

    # game loop
    while True:
        game_over, score = game.play_step()

        if game_over == True:
            break

    print('Final Score', score)


    pygame.quit()
