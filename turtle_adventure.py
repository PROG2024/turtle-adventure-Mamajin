"""
The turtle_adventure module maintains all classes related to the Turtle's
adventure game.
"""
from turtle import RawTurtle
from gamelib import Game, GameElement
import random as rd
import time
import math


class TurtleGameElement(GameElement):
    """
    An abstract class representing all game elemnets related to the Turtle's
    Adventure game
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__game: "TurtleAdventureGame" = game

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game


class Waypoint(TurtleGameElement):
    """
    Represent the waypoint to which the player will move.
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__id1: int
        self.__id2: int
        self.__active: bool = False

    def create(self) -> None:
        self.__id1 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")
        self.__id2 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")

    def delete(self) -> None:
        self.canvas.delete(self.__id1)
        self.canvas.delete(self.__id2)

    def update(self) -> None:
        # there is nothing to update because a waypoint is fixed
        pass

    def render(self) -> None:
        if self.is_active:
            self.canvas.itemconfigure(self.__id1, state="normal")
            self.canvas.itemconfigure(self.__id2, state="normal")
            self.canvas.tag_raise(self.__id1)
            self.canvas.tag_raise(self.__id2)
            self.canvas.coords(self.__id1, self.x-10, self.y-10, self.x+10, self.y+10)
            self.canvas.coords(self.__id2, self.x-10, self.y+10, self.x+10, self.y-10)
        else:
            self.canvas.itemconfigure(self.__id1, state="hidden")
            self.canvas.itemconfigure(self.__id2, state="hidden")

    def activate(self, x: float, y: float) -> None:
        """
        Activate this waypoint with the specified location.
        """
        self.__active = True
        self.x = x
        self.y = y

    def deactivate(self) -> None:
        """
        Mark this waypoint as inactive.
        """
        self.__active = False

    @property
    def is_active(self) -> bool:
        """
        Get the flag indicating whether this waypoint is active.
        """
        return self.__active


class Home(TurtleGameElement):
    """
    Represent the player's home.
    """

    def __init__(self, game: "TurtleAdventureGame", pos: tuple[int, int], size: int):
        super().__init__(game)
        self.__id: int
        self.__size: int = size
        x, y = pos
        self.x = x
        self.y = y

    @property
    def size(self) -> int:
        """
        Get or set the size of Home
        """
        return self.__size

    @size.setter
    def size(self, val: int) -> None:
        self.__size = val

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, outline="brown", width=2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def update(self) -> None:
        # there is nothing to update, unless home is allowed to moved
        pass

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def contains(self, x: float, y: float):
        """
        Check whether home contains the point (x, y).
        """
        x1, x2 = self.x-self.size/2, self.x+self.size/2
        y1, y2 = self.y-self.size/2, self.y+self.size/2
        return x1 <= x <= x2 and y1 <= y <= y2


class Player(TurtleGameElement):
    """
    Represent the main player, implemented using Python's turtle.
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 turtle: RawTurtle,
                 speed: float = 5):
        super().__init__(game)
        self.__speed: float = speed
        self.__turtle: RawTurtle = turtle

    def create(self) -> None:
        turtle = RawTurtle(self.canvas)
        turtle.getscreen().tracer(False) # disable turtle's built-in animation
        turtle.shape("turtle")
        turtle.color("green")
        turtle.penup()

        self.__turtle = turtle

    @property
    def speed(self) -> float:
        """
        Give the player's current speed.
        """
        return self.__speed

    @speed.setter
    def speed(self, val: float) -> None:
        self.__speed = val

    def delete(self) -> None:
        pass

    def update(self) -> None:
        # check if player has arrived home
        if self.game.home.contains(self.x, self.y):
            self.game.game_over_win()
        turtle = self.__turtle
        waypoint = self.game.waypoint
        if self.game.waypoint.is_active:
            turtle.setheading(turtle.towards(waypoint.x, waypoint.y))
            turtle.forward(self.speed)
            if turtle.distance(waypoint.x, waypoint.y) < self.speed:
                waypoint.deactivate()

    def render(self) -> None:
        self.__turtle.goto(self.x, self.y)
        self.__turtle.getscreen().update()

    # override original property x's getter/setter to use turtle's methods
    # instead
    @property
    def x(self) -> float:
        return self.__turtle.xcor()

    @x.setter
    def x(self, val: float) -> None:
        self.__turtle.setx(val)

    # override original property y's getter/setter to use turtle's methods
    # instead
    @property
    def y(self) -> float:
        return self.__turtle.ycor()

    @y.setter
    def y(self, val: float) -> None:
        self.__turtle.sety(val)


class Enemy(TurtleGameElement):
    """
    Define an abstract enemy for the Turtle's adventure game
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game)
        self.__size = size
        self.__color = color

    @property
    def size(self) -> float:
        """
        Get the size of the enemy
        """
        return self.__size

    @property
    def color(self) -> str:
        """
        Get the color of the enemy
        """
        return self.__color

    def hits_player(self):
        """
        Check whether the enemy is hitting the player
        """
        return (
            (self.x - self.size/2 < self.game.player.x < self.x + self.size/2)
            and
            (self.y - self.size/2 < self.game.player.y < self.y + self.size/2)
        )

    def hits_wall(self):
        """
        Check whether the enemy hit a wall
        """
        # self.x < 10 or self.x > 790 or self.y < 10 or self.y > 490
        return self.x < 10 or self.x > 790 or self.y < 10 or self.y > 490


class RandDirEnemy(Enemy):
    """
    Random Walk Enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.__id = None
        self.angle = rd.uniform(0, 2 * math.pi)  # initial random direction
        self.speed = 3

    def create(self) -> None:
        """
        create the enemy
        """
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill='red')

    def update(self) -> None:
        """
        make the enemy move and check for collision
        """
        # Generate a random change in angle
        turn = rd.uniform(-0.1, 0.1)
        # Update angle
        self.angle += turn
        # Calculate new position based on angle
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
        if self.hits_player():
            self.game.game_over_lose()
        if self.hits_wall():
            self.speed *= -1

    def render(self) -> None:
        """
        render enemy
        """
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def delete(self) -> None:
        """
        delete the entity
        """
        self.canvas.delete(self.__id)


class ChasingEnemy(Enemy):
    """
    Chasing Enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.__id = None
        self.speed = 2

    def create(self) -> None:
        """
        create the Chasing enemy
        """
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill='green')

    def update(self) -> None:
        """
        make the enemy move and check for collision
        """
        # calculate direction towards player
        dx = self.game.player.x - self.x
        dy = self.game.player.y - self.y
        angle = math.atan2(dy, dx)
        # move towards the player
        self.x += self.speed * math.cos(angle)
        self.y += self.speed * math.sin(angle)
        # check for collision with player
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        """
        render enemy
        """
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def delete(self) -> None:
        """
        delete the entity
        """
        self.canvas.delete(self.__id)


class FencingEnemy(Enemy):
    """
    Fencing Enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str,
                 radius: int,
                 angle: int,
                 speed: int):
        super().__init__(game, size, color)
        self.__id = None
        self.radius = radius  # Increase the radius for a larger circular path
        self.circle_speed = speed  # Adjust the circle speed as needed
        self.angle = angle

    def create(self) -> None:
        """
        create the Fencing enemy
        """
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill="yellow")

    def update(self) -> None:
        """
        make the enemy move and check for collision
        """
        # Calculate direction towards player
        self.angle += self.circle_speed
        self.angle %= 360
        angle_radians = math.radians(self.angle)
        # Calculate the enemy's position on the circular path around the home
        self.x = self.game.home.x + self.radius * math.cos(angle_radians)
        self.y = self.game.home.y + self.radius * math.sin(angle_radians)
        # Check for collision with player
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        """
        render enemy
        """
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def delete(self) -> None:
        """
        delete the entity
        """
        self.canvas.delete(self.__id)


class WallEnemy(Enemy):
    """
    Custom Enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.__id = None
        # self.angle = rd.uniform(0, 2 * math.pi)  # initial random direction
        self.speed = 5

    def create(self) -> None:
        """
        create the enemy
        """
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, fill='black')

    def update(self) -> None:
        """
        make the enemy move and check for collision
        """
        self.y -= self.speed
        if self.hits_player():
            self.game.game_over_lose()
        if self.hits_wall():
            self.speed *= -1

    def render(self) -> None:
        """
        render enemy
        """
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def delete(self) -> None:
        """
        delete the entity
        """
        self.canvas.delete(self.__id)


class EnemyGenerator:
    """
    An EnemyGenerator instance is responsible for creating enemies of various
    kinds and scheduling them to appear at certain points in time.
    """

    def __init__(self, game: "TurtleAdventureGame", level: int):
        self.__game: TurtleAdventureGame = game
        self.__level: int = level
        self.__game.after(200, self.create_enemy)

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game

    @property
    def level(self) -> int:
        """
        Get the game level
        """
        return self.__level

    @staticmethod
    def rand_x():
        return rd.randint(60, 790)

    @staticmethod
    def rand_y():
        return rd.randint(10, 490)

    def create_enemy(self):
        """
        Create a new enemy, possibly based on the game level
        """
        # create 22 new Random Walk Enemies
        for i in range(22):
            new_enemy = RandDirEnemy(self.__game, 20, "red")
            new_enemy.x = self.rand_x()
            new_enemy.y = self.rand_y()
            self.game.add_element(new_enemy)
        # create chasing enemy
        chase_enemy = ChasingEnemy(self.__game, 20, "green")
        chase_enemy.x = self.rand_x()
        chase_enemy.y = self.rand_y()
        self.game.add_element(chase_enemy)
        # create fencing enemy
        for i in range(50, 151, 50):
            fence_enemy = FencingEnemy(self.__game,
                                       20, "yellow",
                                       i, 0, int(i/50))
            fence_enemy.x = self.game.home.x
            fence_enemy.y = self.game.home.y
            self.game.add_element(fence_enemy)
        # wall enemy
        for i in range(200, 601, 200):
            wall_enemy = WallEnemy(self.__game, 20, "black")
            wall_enemy.x = i
            wall_enemy.y = 20
            self.game.add_element(wall_enemy)


class TurtleAdventureGame(Game):  # pylint: disable=too-many-ancestors
    """
    The main class for Turtle's Adventure.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, parent, screen_width: int, screen_height: int, level: int = 1):
        self.level: int = level
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.waypoint: Waypoint
        self.player: Player
        self.home: Home
        self.enemies: list[Enemy] = []
        self.enemy_generator: EnemyGenerator
        super().__init__(parent)

    def init_game(self):
        self.canvas.config(width=self.screen_width, height=self.screen_height)
        turtle = RawTurtle(self.canvas)
        # set turtle screen's origin to the top-left corner
        turtle.screen.setworldcoordinates(0, self.screen_height-1, self.screen_width-1, 0)

        self.waypoint = Waypoint(self)
        self.add_element(self.waypoint)
        self.home = Home(self, (self.screen_width-100, self.screen_height//2), 20)
        self.add_element(self.home)
        self.player = Player(self, turtle)
        self.add_element(self.player)
        self.canvas.bind("<Button-1>", lambda e: self.waypoint.activate(e.x, e.y))

        self.enemy_generator = EnemyGenerator(self, level=self.level)

        self.player.x = 50
        self.player.y = self.screen_height//2

    def add_enemy(self, enemy: Enemy) -> None:
        """
        Add a new enemy into the current game
        """
        self.enemies.append(enemy)
        self.add_element(enemy)

    def game_over_win(self) -> None:
        """
        Called when the player wins the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Win",
                                font=font,
                                fill="green")

    def game_over_lose(self) -> None:
        """
        Called when the player loses the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Lose",
                                font=font,
                                fill="red")
