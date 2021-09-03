# ! This code should be run in an interpretor (test and approved with: Pycharm, VScode)

import string
import random
import time
import sys
from datetime import datetime
from tkinter import Tk, Label
from itertools import count
import winsound
from PIL import Image, ImageTk


class Game:

    def __init__(self, board_size=10):
        self.size = board_size
        self.entity = "•"  # default case icon
        self.board = [[self.entity for col in range(self.size)] for line in range(self.size)]
        self.beta = string.ascii_uppercase  # stock upper letter inside a var
        self.nb_players = 0
        self.wall_icon = "#"  # default wall icon
        self.round = 0
        self.timer = datetime.now().strftime("%H:%M:%S")
        self.walls = []
        self.players_list = []
        self.leaderboard_dict = {}
        self.keys = {"Up": "z", "Down": "s", "Left": "q", "Right": "d", "Wall": "w", "Spell": "c"}  # default commands
        self.players_spawn2 = [
            (0, int(len(self.board[0]) / 2) - 1 if self.size % 2 == 0 else int(self.size / 2)),
            (
                len(self.board[::-1][0]) - 1,
                int(len(self.board[0]) / 2) - 0 if self.size % 2 == 0 else int(self.size / 2))
        ]  # spawns for 2 players
        self.players_spawn4 = [
            (0, 0),
            (0, len(self.board[::-1][0]) - 1),
            (len(self.board[::-1][0]) - 1, 0),
            (len(self.board[::-1][0]) - 1, len(self.board[::-1][0]) - 1)
        ]  # spawns 4 players

    def draw(self):
        letters = list(self.beta)
        letters.insert(0, "   ")  # insert at the early of the list blank string for a good display of the board
        print(*letters[:self.size + 1])  # *unconcatenate -> not a list anymore, :slice -> from the start to the end
        for number, i in enumerate(self.board):  # works as range
            if number >= 10:  # if board size >= 10
                print(number, end="  ")
                print(" ".join(i))
            else:
                print(number, end="   ")
                print(" ".join(i))

    def add_wall(self, pos: tuple):
        self.walls.append(pos)
        self.board[pos[0]][pos[1]] = self.wall_icon

    def add_player(self, player):
        line, col = player.position
        self.board[line][col] = player.name[0]  # first letter of the player's name
        self.players_list.append(player)
        self.nb_players += 1

    def is_wall(self, pos: tuple):
        return pos in self.walls

    def coord_to_tuple(self, target):  # convert "2B" into a usable tuple as (2, 1)
        line, col = target[:-1], target[-1::].upper()  # :-1 takes all except last item, -1:: takes the last item
        for letter in self.beta:
            if letter == col:
                col_number = self.beta.index(letter)
                return int(line), col_number

    def print_transfo_pos(self, pos):  # convert (2, 1) into a string as "2B"
        line, col = pos[0], pos[1]
        col_beta = self.beta[col]
        return str(str(line) + col_beta)

    def board_range(self, coord: tuple):
        line, col = coord[0], coord[1]
        return 0 <= line <= self.size - 1 and 0 <= col <= self.size - 1

    def play(self):
        self.leaderboard()
        denomination = ["first", "second", "third", "fourth"]
        cpt = 0
        IA_activated = False

        print("")
        menu = 0
        ended = False
        while not ended:
            try:
                menu = int(input(f"1. Rules \n2. See the leaderboard \n3. Change commands \n4. Play game\n"))
                if type(menu) == int and menu in [1, 2, 3, 4]:
                    ended = True
                else:
                    print("Wrong number!")
            except ValueError:
                print("Wrong input! Need an int..")

        if menu == 1:  # rules
            print(f"""
            {Color.red}So, we begin with the defaults rules of this game:{Color.end}
            - The default board size is 10
            - 2 players spawn, one on the middle-top, one on the middle-bottom
            - The first player who reaches the enemy spawn win
            - Players can place wall OR move each turn

            {Color.red}I added some features to make a better gameplay:{Color.end}
            - Board can be scaled between 6 and 26
            - 4 players can spawn, each in a corner
            - Player can chose a profession:
                -> Sorcerer can launch a Fireball that destroys one wall
                -> Scout can dash in one direction that move the player of 2 bits
            - If you chose to play alone, you'll playing vs an AI (that disables profession)
            - Now players can move AND add a wall OR use a spell
            - An event destroy the board each two rounds from the third one
            - A leaderboard is accessible to view player's performance
            - Collision are detected
            - User can change commands
            """)
            self.play()

        elif menu == 2:  # see the leaderboard
            if len(self.leaderboard_dict) == 0:
                print(f"{Color.red} Leaderboard is empty! {Color.end}")

            else:
                print("")
                # sort by number of game won -> x: x[1] refer to value, if x: x[0] refer to key (pseudo's len)
                sorted_dict = sorted(self.leaderboard_dict.items(), key=lambda x: x[1], reverse=True)
                print(f"{Color.red}Top 3 players is: {Color.end}")
                enum = 1
                for player, games in sorted_dict[:5]:
                    print(f"{enum}. {Color.magenta}{player}{Color.end} with "
                          f"{Color.magenta}{games}{Color.end} win")
                    enum += 1
            print("")
            self.play()

        elif menu == 3:  # change commands keys
            self.print_keys()
            keys = input(
                f"{Color.yellow}Do u want to let them default?{Color.red} (Y or N){Color.yellow}: {Color.end}\n")
            while not (keys.lower() == "y" or keys.lower() == "n"):
                print(f"{Color.red}Wrong input!{Color.end}")
                keys = input(f"{Color.yellow}Do u want to let them default?{Color.red}"
                             f" (Y or N){Color.yellow}: {Color.end}\n")
            if keys == "y":
                pass

            elif keys == "n":
                key = input(f"{Color.yellow}Which key do you want to change?{Color.red} "
                            f"(or E to end){Color.yellow} (ex: Z,Q,S,D,W,C): {Color.end}\n")
                while key.lower() != "e":
                    replace = input(f"{Color.orange}{key}{Color.yellow} will be replaced by: {Color.end}\n")
                    for action, val in self.keys.items():
                        if val == key:
                            self.keys[action] = replace
                    self.print_keys()
                    key = input(f"{Color.yellow}Which key do you want to change?{Color.red} "
                                f"(or E to end){Color.yellow} (ex: Z,Q,S,D,W,C): {Color.end}\n")
            self.play()

        elif menu == 4:  # play game
            # how much players
            ended = False
            hmp = 0
            while not ended:
                try:
                    hmp = int(input(f"{Color.yellow}How many players want to play? 1, 2 or 4: {Color.end}\n"))
                    if type(hmp) == int and hmp in [1, 2, 4]:
                        ended = True
                    else:
                        print("Wrong number!")
                except ValueError:
                    print("Wrong input! Need an int..")

            # adding players
            while cpt < hmp:
                ask_player_class = 0  # default value
                if hmp != 1:
                    ask_player_name = input(f"{Color.yellow}Name of the {Color.orange}{denomination[cpt]}"
                                            f"{Color.yellow} player: {Color.end}")
                    ended = False
                    while not ended:
                        try:
                            ask_player_class = int(input(f"{Color.yellow}Class of the {Color.orange}{denomination[cpt]}"
                                                         f"{Color.yellow} player {Color.red} \n1. Sorcerer \n2. Scout \n"
                                                         f"{Color.yellow}Enter a number: {Color.end}"))
                            if type(ask_player_class) == int and ask_player_class == 1 or ask_player_class == 2:
                                ended = True
                            else:
                                print("Wrong number!")
                        except ValueError:
                            print("Wrong input! Need an int..")

                else:
                    ask_player_name = input(f"{Color.yellow}Name of the player: {Color.end}")
                    player = Player(ask_player_name, game1, self.players_spawn2[0])
                    robot = IA("Robot", game1, self.players_spawn2[1])
                    IA_activated = True

                if ask_player_class == 1:
                    print(f"{Color.orange}{ask_player_name}{Color.yellow} you chose to be a {Color.orange}Sorcerer"
                          f"{Color.end}")
                    player = Sorcerer(ask_player_name, game1,
                                      (self.players_spawn2[cpt] if hmp == 2 else self.players_spawn4[cpt]))

                elif ask_player_class == 2:
                    print(f"{Color.orange}{ask_player_name}{Color.yellow} you chose to be a {Color.orange}Scout"
                          f"{Color.end}")
                    player = Scout(ask_player_name, game1,
                                   (self.players_spawn2[cpt] if hmp == 2 else self.players_spawn4[cpt]))
                print("")
                cpt += 1

            p = 0
            ended = False
            # loop for playing with multiple players
            if not IA_activated:
                while not ended:
                    if not self.players_list[p].is_winner():
                        self.round += 1
                        print(f"\n{Color.yellow}Round {Color.orange}{self.round}{Color.end}")

                        print(f"{Color.red}{self.players_list[p].name} {Color.yellow}u play!{Color.end} "
                              f"(Position: {self.print_transfo_pos(self.players_list[p].position)})")

                        if self.round >= 3 and self.round % 2 == 1:
                            event.broken_ground()

                        self.draw()
                        self.players_list[p].play()
                        self.draw()
                        if self.players_list[p].is_winner():
                            ended = True
                            self.ending_play(self.players_list[p].name)

                        print(f"{Color.yellow}Remaining walls: {Color.red}{self.players_list[p].player_walls}"
                              f"{Color.end}")
                        self.players_list[p].play_skills()
                        if not self.players_list[p].is_winner():
                            p += 1
                            if p >= self.nb_players:
                                p = 0
                    else:
                        ended = True
                        self.ending_play(self.players_list[p].name)

            # loop for playing vs IA
            else:
                while not ended:
                    if not self.players_list[p].is_winner():
                        self.round += 1
                        print(f"\n{Color.yellow}Round {Color.orange}{self.round}{Color.end}")

                        if self.round % 2 == 1:
                            print(f"{Color.red}{self.players_list[0].name} {Color.yellow}u play!{Color.end} "
                                  f"(Position: {self.print_transfo_pos(self.players_list[0].position)})")

                        if self.round >= 3 and self.round % 3 == 0:
                            event.broken_ground()

                        self.draw()

                        if self.round % 2 == 1:  # human play one turn over two
                            self.players_list[0].play()
                            self.draw()

                            if self.players_list[0].player_walls > 0:
                                print(f"{Color.yellow}Remaining walls: {Color.red}{self.players_list[0].player_walls}"
                                      f"{Color.end}")
                                target = input(f"{Color.yellow}Where do you want to place a wall? Enter a position "
                                               f"(ex: 2B) {Color.red} \n(or E to end){Color.yellow}: {Color.end}")
                                while "-" in target and target.lower() != "e":
                                    print(f"{Color.red}Out of board's range!{Color.end}")
                                    print(f"{Color.yellow}Remaining walls: {Color.red}"
                                          f"{self.players_list[0].player_walls}{Color.end}")
                                    target = input(f"{Color.yellow}Where do you want to place a wall? Enter a position "
                                                   f"(ex: 2B) {Color.red} \n(or E to end){Color.yellow}: {Color.end}")

                                if target.lower() != "e" and "-" not in target:
                                    self.players_list[0].place_wall(self.coord_to_tuple(target))

                        else:
                            self.players_list[1].play_alone()

                        if self.players_list[p].is_winner():
                            ended = True
                            if self.players_list[0].is_winner():
                                self.draw()
                                self.animation(False)
                                self.ending_play(self.players_list[0].name)
                            else:
                                self.draw()
                                self.animation(True)

                        p += 1
                        if p >= self.nb_players:
                            p = 0
                    else:
                        ended = True
                        if self.players_list[0].is_winner():
                            self.draw()
                            self.animation(False)
                            self.ending_play(self.players_list[0].name)
                        else:
                            self.draw()
                            self.animation(True)

    def animation(self, bool):  # end message if playing vs the AI
        message = """
         .===.     
        //- -\\    
        \\_#_//    
    }-. /\--o/\ .-{
       " |___| "   
         [] []     
        /:] [:\   """ + f"{Color.red} Robots always win {Color.end}"
        message2 = """
           .-.      
        ._(u u)_.   
          (_O_)     
        ,"|+  |".   
        _\|+__|/_   
          (   )     
         __) (__   """ + f"{Color.red} You won, this time. {Color.end}"
        if bool:
            for char in message:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(0.02)
        else:
            for char in message2:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(0.02)

    def print_keys(self):  # print commands
        print(f"{Color.yellow}Keys are: {Color.end}")
        for key, val in self.keys.items():
            print(f"{Color.orange}{key} -> {val.upper()}{Color.end}")

    def leaderboard(self):  # take values of leaderboard.txt to write it in a dict
        game = 1
        file = open("leaderboard.txt", "r+")
        for name in file.read().splitlines():
            if name in self.leaderboard_dict.keys():
                self.leaderboard_dict[name] += game
            else:
                self.leaderboard_dict[name] = game
        file.close()

    def ending_play(self, player):  # write the name of the winner in leaderboard.txt + winning message
        with open("leaderboard.txt", "w+") as f:
            f.write(player + '\n')
            print("A window has been opened.")
            self.window(player, self.subtime())

    def subtime(self):  # timer to see performance at the end of a game
        format = "%H:%M:%S"
        return datetime.strptime(datetime.now().strftime(format), format) - datetime.strptime(self.timer, format)

    def window(self, player, timer):  # graphic interface if ended game
        root = Tk()
        root.title('Quoridor by bugsbunny')
        root.geometry("500x455")
        root.config(background="white")

        text = Label(root, text="Thanks for playing!", font=("Consolas", 20), bg="white", fg="black")
        text.pack()

        text3 = Label(root, text=f"{player} won in {timer}", font=("Consolas", 15), bg="white", fg="black")
        text3.pack()

        text2 = Label(root, text="Your name will be added in the leaderboard if you're in the top5!",
                      font=("Consolas", 10), bg="white", fg="red")
        text2.pack()

        lbl = Interface(root)
        lbl.pack()
        lbl.load('rick.gif')

        winsound.PlaySound("rick.wav", winsound.SND_ASYNC)
        root.mainloop()


class Player:

    def __init__(self, name, game, position: tuple):
        self.start = position
        self.position = position
        self.name = name
        self.game = game
        self.game.add_player(self)
        self.player_walls = 5

    def move(self, mvmt: tuple):
        n_line, n_col = self.position[0] + mvmt[0], self.position[1] + mvmt[1]  # calculation new pos
        pos = self.game.board[n_line][n_col] if self.game.board_range((n_line, n_col)) else None
        if pos == self.game.entity and pos != event.broken_ground_icon:
            self.game.board[self.position[0]][self.position[1]] = self.game.entity  # change icon previous pos
            self.position = n_line, n_col  # init new pos
            self.game.board[self.position[0]][self.position[1]] = self.name[0]  # change icon new pos
            return True
        else:
            self.display_move_error()
            return False

    def display_move_error(self):
        print(f"{Color.red}Can't move because of an entity! (Or out of board's range){Color.end}")

    def place_wall(self, pos: tuple):
        if not self.game.is_wall(pos) and self.game.board[pos[0]][pos[1]] == self.game.entity and self.player_walls > 0:
            self.game.add_wall(pos)
            self.player_walls -= 1
            return True
        else:
            self.display_place_wall_error()
            return False

    def display_place_wall_error(self):
        print(f"{Color.red}An entity is already there or you don't have no more walls to place!{Color.end}")

    def is_winner(self):
        last_line = len(self.game.board[::-1][0]) - 1  # last line of the board, scaled on the size
        if self.position != self.start:
            if self.start[0] == 0:  # if player spawned on first line
                return self.position[0] == last_line  # bool if now his position is on last line
            elif self.start[0] == last_line:  # if player spawned on last line
                return self.position[0] == 0  # bool if now his position is on first line
        else:
            return False

    def play(self):
        action = input(f"{Color.yellow} {self.game.keys['Up'].upper()}: Up \n {self.game.keys['Down'].upper()}: Down"
                       f" \n {self.game.keys['Right'].upper()}: Right \n "
                       f"{self.game.keys['Left'].upper()}: Left{Color.end}\n")
        action_low = action.lower()
        if action_low == self.game.keys['Up']:
            if not self.move((-1, 0)):  # if move() return false
                self.play()  # go at the top of this function
        elif action_low == self.game.keys['Down']:
            if not self.move((1, 0)):
                self.play()
        elif action_low == self.game.keys['Right']:
            if not self.move((0, 1)):
                self.play()
        elif action_low == self.game.keys['Left']:
            if not self.move((0, -1)):
                self.play()


class Scout(Player):

    def __init__(self, name, game, position: tuple):
        super().__init__(name, game, position)

    def play_skills(self):
        if not self.is_winner():
            action = input(f"{Color.yellow}{self.game.keys['Wall'].upper()}: Place wall \n"
                           f"{self.game.keys['Spell'].upper()}: Dash \n{Color.red}(or E to end){Color.end}\n")
            action_low = action.lower()

            if action_low == self.game.keys['Wall']:
                target = input(f"{Color.yellow}Where do you want to place a wall? Enter a position (ex: 2B)"
                               f"{Color.red} \n(or E to end){Color.yellow}: {Color.end}")
                if target.lower() == "e":
                    return False
                else:
                    if "-" in target:
                        print(f"{Color.red}Out of board's range!{Color.end}")
                        self.play_skills()
                    else:
                        if not self.place_wall(self.game.coord_to_tuple(target)):
                            self.play_skills()

            elif action_low == self.game.keys['Spell']:
                if random.choice([True, False, True]):  # 33% chance of fail
                    self.dash()
                else:
                    print(f"{Color.red}The spell failed to launch!{Color.end}")

            elif action_low == "e":
                return False

            else:
                self.play_skills()

    def dash(self):
        direction = input(f"{Color.yellow}In which direction do you want to dash? Z, S, Q or D "
                          f"{Color.red}\n(or E to end){Color.yellow}: {Color.end}")
        inp_low = direction.lower()
        if inp_low == "z":
            if not self.move((-2, 0)):
                self.dash()
        elif inp_low == "s":
            if not self.move((2, 0)):
                self.dash()
        elif inp_low == "d":
            if not self.move((0, 2)):
                self.dash()
        elif inp_low == "q":
            if not self.move((0, -2)):
                self.dash()
        elif inp_low == "e":
            return False


class Sorcerer(Player):

    def __init__(self, name, game, position: tuple):
        super().__init__(name, game, position)

    def play_skills(self):
        if not self.is_winner():
            action = input(f"{Color.yellow}{self.game.keys['Wall'].upper()}: Place wall \n"
                           f"{self.game.keys['Spell'].upper()}: Fireball \n{Color.red}(or E to end){Color.end}\n")
            action_low = action.lower()

            if action_low == self.game.keys['Wall']:
                target = input(f"{Color.yellow}Where do you want to place a wall? Enter a position (ex: 2B)"
                               f"{Color.red} \n(or E to end){Color.yellow}: {Color.end}\n")
                if target.lower() == "e":
                    return False
                else:
                    if "-" in target:
                        print(f"{Color.red}Out of board's range!{Color.end}")
                        self.play_skills()
                    else:
                        if not self.place_wall(self.game.coord_to_tuple(target)):
                            self.play_skills()

            elif action_low == self.game.keys['Spell']:
                target = input(f"{Color.yellow}Which wall do you want to destroy? Enter a position (ex: 2B){Color.red}"
                               f"\n(or E to end){Color.yellow}: {Color.end}\n")
                if target.lower() == "e":
                    return False
                else:
                    if random.choice([True, False, True]):  # 33% chance of fail
                        if not self.fireball(self.game.coord_to_tuple(target)):
                            self.play_skills()
                    else:
                        print(f"{Color.red}The spell failed to launch!{Color.end}")

            elif action_low == "e":
                return False

            else:
                self.play_skills()

    def fireball(self, target):
        if target in self.game.walls:
            self.game.walls.remove(target)
            self.game.board[target[0]][target[1]] = self.game.entity
            print(f"{Color.cyan}Wall has been destroyed!{Color.end}")
            return True
        else:
            print(f"{Color.red}No wall here!{Color.end}")
            return False

class Event:

    def __init__(self, game):
        self.game = game
        self.broken_ground_icon = " "  # default broken ground icon
        self.bg_list = []

    def broken_ground(self):
        random_1 = random.randint(0, self.game.size - 1)  # random y
        random_2 = random.randint(0, self.game.size - 1)  # random x
        random_tuple = (random_1, random_2)
        random_pos = self.game.board[random_1][random_2]
        if random_pos == self.game.entity and random_pos != self.broken_ground_icon and random_pos not in self.bg_list:
            self.game.board[random_1][random_2] = self.broken_ground_icon
            self.bg_list.append(random_tuple)
            print(f"{Color.magenta}The ground is collapsing!{Color.end}")
        else:
            self.broken_ground()


class IA(Player):

    def __init__(self, name, game, position: tuple):
        super().__init__(name, game, position)
        self.turn = 1
        self.default = False

    def play_alone(self):
        if not self.turn % 3 == 0 or self.default:  # each 3 turns, AI will place a wall or move if she can't
            if not self.move((-1, 0)):
                if not self.move((0, 1)):
                    if not self.move((0, -1)):
                        self.move((1, 0))
            self.default = False
        else:
            if not self.place_wall(self.calculate_enemy_pos()):
                self.default = True
                self.play_alone()
        self.turn += 1

    def calculate_enemy_pos(self):
        line, col = self.game.players_list[0].position
        return line + 1, col

    def display_move_error(self):
        return None

    def display_place_wall_error(self):
        return None


class Interface(Label):

    def load(self, pic):  # load image values
        if isinstance(pic, str):  # check if pic is a str
            pic = Image.open(pic)
        self.cpt = 0
        self.frames = []

        try:
            for i in count(1):  # iter to infinity (step by one)
                self.frames.append(ImageTk.PhotoImage(pic.copy()))  # copy all frames
                pic.seek(i)  # set the position of the frame
        except EOFError:  # go next if no data to read
            pass

        try:
            self.delay = pic.info['duration']  # take infos from the gif's duration
        except:
            self.delay = 100  # set the delay to 100 if occuring and error

        if len(self.frames) == 1:  # if length of [frames]
            self.config(image=self.frames[0])  # go to the first frame
        else:
            self.next_frame()

    def next_frame(self):
        if self.frames:  # if list is not empty
            self.cpt += 1
            self.cpt %= len(self.frames)  # ex 8%8 = 0 but 8%higher_N = 8
            self.config(image=self.frames[self.cpt])  # apply the next frame
            self.after(self.delay, self.next_frame)  # after the delay, loop to top of this func


class Color:
    magenta = '\033[95m'
    cyan = '\033[96m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    end = '\033[0m'
    orange = '\033[38;2;255;165;0m'


if __name__ == "__main__":
    print(f"""
                        _     _            
  __ _ _   _  ___  _ __(_) __| | ___  _ __ 
 / _` | | | |/ _ \| '__| |/ _` |/ _ \| '__|
| (_| | |_| | (_) | |  | | (_| | (_) | |   
 \__, |\__,_|\___/|_|  |_|\__,_|\___/|_|   
    |_|                    {Color.magenta}by @bug$bunny{Color.end}
""")
    print(f"""
{Color.red}This game has been created for a school project in python
{Color.orange}Have a nice game!{Color.end}

Default board size is 10. U'll get some informations about the game after choosing a size.
""")

    bs = 0

    ended = False
    while not ended:
        try:
            bs = int(input(f"{Color.yellow}Which size of board do u want? Number between 6 and 26: {Color.end}\n"))
            if type(bs) == int and bs in range(6, 26):
                ended = True
            else:
                print("Wrong number!")
        except ValueError:
            print("Wrong input! Need an int..")

    try:
        with open("leaderboard.txt", "x"):  # create leaderboard.txt
            pass
    except FileExistsError:  # error if already created
        pass

    game1 = Game(bs)
    event = Event(game1)
    game1.play()
