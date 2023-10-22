import tkinter as tk
import random
import threading
import time


class Game:
    """Game of The Bug!"""

    def __init__(self):
        self.root = tk.Tk()
        self.ai_iq = 0  # [0,10] 0 best IQ , 10 lowest IQ
        self.root.title(Game.__doc__)
        self.canvas = tk.Canvas(self.root, width=500, height=500)
        self.canvas.pack()
        self.canvas.config(bg="black")
        self.lock = threading.Lock()
        # probably GIL handel this but i implement for fun
        self.rock_amount = 22
        self.paper_amount = 22
        self.scissor_amount = 22
        self.rock_positions = []
        self.paper_positions = []
        self.scissors_positions = []

    def make_random_coords(self, mid_x=250, mid_y=250, offset=100):
        """create a random coordinates for objects"""
        return [
            random.randint(mid_x - offset, mid_x + offset),
            random.randint(mid_y - offset, mid_y + offset),
        ]

    def move_towards_enemy(self, coords, enemy_positions):
        """
        Euclidean Distance
        https://www.geeksforgeeks.org/program-calculate-distance-two-points/
        distance = sqrt((x2-x1)**2+(y2-y1)**2)
        """
        if not enemy_positions:
            return
        # find the nearest enemy
        if random.randint(1, 65) > self.ai_iq:
            nearest_enemy = min(
                enemy_positions,
                key=lambda enemy: (
                    (enemy[0] - coords[0]) ** 2 + (enemy[1] - coords[1]) ** 2
                )
                ** 0.5,
            )  # I know this isn't simple in first look :)

            dx = nearest_enemy[0] - coords[0]
            dy = nearest_enemy[1] - coords[1]
            distance = (dx**2 + dy**2) ** 0.5

            if distance > 0:
                coords[0] += dx / distance
                coords[1] += dy / distance
            # move to enemy location
        else:
            nearest_enemy = enemy_positions[random.randint(0, len(enemy_positions) - 1)]
            if nearest_enemy[0] > coords[0]:
                coords[0] += 1
            else:
                coords[0] -= 1
            if nearest_enemy[1] > coords[1]:
                coords[1] += 1
            else:
                coords[1] -= 1
        # This way has lower intelligence to make the game a little more realistic

    def generate_rock(self):
        """generate rock in space"""
        while len(self.rock_positions) < self.rock_amount:
            gem = self.make_random_coords()
            if (
                gem not in self.rock_positions
                and gem not in self.paper_positions
                and gem not in self.scissors_positions
            ):
                with self.lock:
                    self.rock_positions.append(gem)
            time.sleep(0.09)

    def generate_paper(self):
        """generate paper in space"""
        while len(self.paper_positions) < self.paper_amount:
            gem = self.make_random_coords()
            if (
                gem not in self.rock_positions
                and gem not in self.paper_positions
                and gem not in self.scissors_positions
            ):
                with self.lock:
                    self.paper_positions.append(gem)
            time.sleep(0.09)

    def generate_scissors(self):
        """generate scissors in space"""
        while len(self.scissors_positions) < self.scissor_amount:
            gem = self.make_random_coords()
            if (
                gem not in self.rock_positions
                and gem not in self.paper_positions
                and gem not in self.scissors_positions
            ):
                with self.lock:
                    self.scissors_positions.append(gem)
            time.sleep(0.09)

    def move_coordinates(self):
        """move objects around"""
        # Its better to move objects separately in different threads
        found = False
        enemy_pos_del = None
        for rock in self.rock_positions:
            enemy_positions = self.scissors_positions
            for enemy_pos in enemy_positions:
                if rock[0] == enemy_pos[0] and rock[1] == enemy_pos[1]:
                    found = True
                    enemy_pos_del = enemy_pos
                    break
            if not found:
                self.move_towards_enemy(rock, enemy_positions)
            else:
                with self.lock:
                    self.scissors_positions.remove(enemy_pos_del)
                found = False
                print("[A Scissors died]")

        for paper in self.paper_positions:
            enemy_positions = self.rock_positions
            for enemy_pos in enemy_positions:
                if paper[0] == enemy_pos[0] and paper[1] == enemy_pos[1]:
                    found = True
                    enemy_pos_del = enemy_pos
                    break
            if not found:
                self.move_towards_enemy(paper, enemy_positions)
            else:
                found = False
                with self.lock:
                    self.rock_positions.remove(enemy_pos_del)
                print("[A Rock died]")

        for scissors in self.scissors_positions:
            enemy_positions = self.paper_positions
            for enemy_pos in enemy_positions:
                if scissors[0] == enemy_pos[0] and scissors[1] == enemy_pos[1]:
                    found = True
                    enemy_pos_del = enemy_pos
                    break
            if not found:
                self.move_towards_enemy(scissors, enemy_positions)
            else:
                found = False
                with self.lock:
                    self.paper_positions.remove(enemy_pos_del)
                print("[A Paper died]")

        self.root.after(3, self.move_coordinates)

    def add_new_object(self):
        """add a rock or paper or scissor to keep the game alive"""
        while True:
            gem = self.make_random_coords()
            with self.lock:
                random.choice(
                    [self.rock_positions, self.paper_positions, self.scissors_positions]
                ).append(gem)
            time.sleep(0.1)

    def draw_coordinates(self):
        """draw objects by coordinate"""
        self.canvas.delete("all")  # delete previous movements
        for pos in self.paper_positions:
            pos[0] = max(100, min(400, pos[0]))
            pos[1] = max(100, min(400, pos[1]))
            self.canvas.create_rectangle(
                pos[0], pos[1], pos[0] + 10, pos[1] + 10, fill="blue"
            )
        for pos in self.rock_positions:
            pos[0] = max(100, min(400, pos[0]))
            pos[1] = max(100, min(400, pos[1]))
            self.canvas.create_rectangle(
                pos[0], pos[1], pos[0] + 10, pos[1] + 10, fill="red"
            )
        for pos in self.scissors_positions:
            pos[0] = max(100, min(400, pos[0]))
            pos[1] = max(100, min(400, pos[1]))
            self.canvas.create_rectangle(
                pos[0], pos[1], pos[0] + 10, pos[1] + 10, fill="green"
            )
        self.root.after(150, self.draw_coordinates)

    def start_game(self):
        """run all needed threads"""
        threading.Thread(target=self.generate_paper).start()
        threading.Thread(target=self.generate_rock).start()
        threading.Thread(target=self.generate_scissors).start()
        threading.Thread(target=self.move_coordinates).start()
        threading.Thread(target=self.add_new_object).start()
        self.draw_coordinates()
        self.root.mainloop()


if __name__ == "__main__":
    game = Game()
    game.start_game()
