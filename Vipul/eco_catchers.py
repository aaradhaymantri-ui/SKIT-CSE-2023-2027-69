import pygame
import random
import math
import json
import os
import sys

# ============================================================
# ECO CATCHERS
# Environmental Education Game
# ============================================================
#
# Controls:
#   A / LEFT ARROW   -> Move left
#   D / RIGHT ARROW  -> Move right
#   SPACE            -> Start / Restart
#   ESC              -> Quit
#
# Good objects give points.
# Bad objects reduce lives.
#
# ============================================================


# ------------------------------------------------------------
# INITIALIZATION
# ------------------------------------------------------------

pygame.init()

WIDTH = 1100
HEIGHT = 700

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT),
    pygame.RESIZABLE
)

pygame.display.set_caption(
    "EcoCatchers - Save the Planet"
)

clock = pygame.time.Clock()

FPS = 60

# ------------------------------------------------------------
# COLORS
# ------------------------------------------------------------

WHITE = (255, 255, 255)
BLACK = (15, 20, 25)

SKY_TOP = (90, 190, 245)
SKY_BOTTOM = (190, 235, 255)

GREEN = (45, 170, 85)
DARK_GREEN = (20, 110, 55)
LIGHT_GREEN = (120, 210, 95)

RED = (220, 70, 70)
ORANGE = (240, 150, 40)

BLUE = (50, 130, 220)

YELLOW = (245, 210, 60)

GRAY = (90, 100, 110)
LIGHT_GRAY = (235, 240, 240)

BROWN = (125, 80, 45)

PURPLE = (145, 80, 180)


# ------------------------------------------------------------
# FONTS
# ------------------------------------------------------------

FONT_SMALL = pygame.font.SysFont(
    "arial",
    20,
    bold=True
)

FONT_MEDIUM = pygame.font.SysFont(
    "arial",
    30,
    bold=True
)

FONT_LARGE = pygame.font.SysFont(
    "arial",
    52,
    bold=True
)

FONT_HUGE = pygame.font.SysFont(
    "arial",
    80,
    bold=True
)


# ------------------------------------------------------------
# GAME CONSTANTS
# ------------------------------------------------------------

GAME_LENGTH = 60

STARTING_LIVES = 3

PLAYER_WIDTH = 110
PLAYER_HEIGHT = 70

PLAYER_SPEED = 520

OBJECT_SIZE = 52

MAX_PARTICLES = 150

HIGH_SCORE_FILE = "eco_highscore.json"


# ------------------------------------------------------------
# OBJECT DATA
# ------------------------------------------------------------

GOOD_OBJECTS = [
    {
        "name": "RECYCLING",
        "symbol": "R",
        "points": 10,
        "color": (60, 190, 110),
    },
    {
        "name": "TREE",
        "symbol": "T",
        "points": 25,
        "color": (50, 160, 70),
    },
    {
        "name": "CLEAN WATER",
        "symbol": "W",
        "points": 15,
        "color": (50, 150, 230),
    },
    {
        "name": "SOLAR",
        "symbol": "S",
        "points": 20,
        "color": (240, 190, 50),
    },
    {
        "name": "PLANT",
        "symbol": "P",
        "points": 12,
        "color": (100, 190, 80),
    },
    {
        "name": "CAN",
        "symbol": "C",
        "points": 10,
        "color": (160, 170, 180),
    },
]

BAD_OBJECTS = [
    {
        "name": "POLLUTION",
        "symbol": "!",
        "damage": 1,
        "color": (100, 100, 110),
    },
    {
        "name": "OIL",
        "symbol": "O",
        "damage": 1,
        "color": (25, 25, 30),
    },
    {
        "name": "TOXIC",
        "symbol": "X",
        "damage": 2,
        "color": (150, 70, 190),
    },
    {
        "name": "FIRE",
        "symbol": "F",
        "damage": 1,
        "color": (240, 80, 40),
    },
    {
        "name": "CHEMICAL",
        "symbol": "!",
        "damage": 2,
        "color": (220, 120, 50),
    },
]


# ------------------------------------------------------------
# UTILITY FUNCTIONS
# ------------------------------------------------------------

def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def lerp(a, b, amount):
    return a + (b - a) * amount


def random_float(minimum, maximum):
    return random.uniform(minimum, maximum)


# ------------------------------------------------------------
# HIGH SCORE
# ------------------------------------------------------------

def load_high_score():

    if not os.path.exists(HIGH_SCORE_FILE):
        return 0

    try:

        with open(
            HIGH_SCORE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            return int(
                data.get("high_score", 0)
            )

    except Exception:
        return 0


def save_high_score(score):

    try:

        with open(
            HIGH_SCORE_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                {
                    "high_score": score
                },
                file
            )

    except Exception:
        pass


# ============================================================
# PARTICLE CLASS
# ============================================================

class Particle:

    def __init__(
        self,
        x,
        y,
        color,
        text=None
    ):

        self.x = x
        self.y = y

        self.vx = random_float(-140, 140)
        self.vy = random_float(-220, -70)

        self.life = random_float(
            0.6,
            1.2
        )

        self.max_life = self.life

        self.size = random.randint(
            4,
            10
        )

        self.color = color

        self.text = text

        self.gravity = 300

        self.rotation = random_float(
            -180,
            180
        )

        self.rotation_speed = random_float(
            -220,
            220
        )

    def update(self, dt):

        self.x += self.vx * dt

        self.y += self.vy * dt

        self.vy += (
            self.gravity * dt
        )

        self.rotation += (
            self.rotation_speed * dt
        )

        self.life -= dt

    def draw(self, surface):

        if self.life <= 0:
            return

        alpha = int(
            255 *
            (self.life /
             self.max_life)
        )

        if self.text is not None:

            image = FONT_SMALL.render(
                self.text,
                True,
                self.color
            )

            image.set_alpha(alpha)

            surface.blit(
                image,
                (
                    int(self.x),
                    int(self.y)
                )
            )

        else:

            radius = max(
                1,
                int(
                    self.size *
                    (self.life /
                     self.max_life)
                )
            )

            particle_surface = (
                pygame.Surface(
                    (
                        radius * 2,
                        radius * 2
                    ),
                    pygame.SRCALPHA
                )
            )

            pygame.draw.circle(
                particle_surface,
                (
                    self.color[0],
                    self.color[1],
                    self.color[2],
                    alpha
                ),
                (
                    radius,
                    radius
                ),
                radius
            )

            surface.blit(
                particle_surface,
                (
                    int(
                        self.x -
                        radius
                    ),
                    int(
                        self.y -
                        radius
                    )
                )
            )


# ============================================================
# FALLING OBJECT
# ============================================================

class FallingObject:

    def __init__(
        self,
        game_width,
        speed_multiplier=1.0
    ):

        self.x = random.uniform(
            40,
            game_width - 40
        )

        self.y = -OBJECT_SIZE

        self.width = OBJECT_SIZE
        self.height = OBJECT_SIZE

        self.rotation = random.uniform(
            0,
            360
        )

        self.rotation_speed = random.uniform(
            -180,
            180
        )

        self.speed = random.uniform(
            150,
            260
        ) * speed_multiplier

        # 75% chance of good item
        self.good = random.random() < 0.75

        if self.good:

            data = random.choice(
                GOOD_OBJECTS
            )

            self.name = data["name"]
            self.symbol = data["symbol"]
            self.points = data["points"]
            self.color = data["color"]
            self.damage = 0

        else:

            data = random.choice(
                BAD_OBJECTS
            )

            self.name = data["name"]
            self.symbol = data["symbol"]
            self.points = 0
            self.color = data["color"]
            self.damage = data["damage"]

    def update(self, dt):

        self.y += (
            self.speed *
            dt
        )

        self.rotation += (
            self.rotation_speed *
            dt
        )

    def rect(self):

        return pygame.Rect(
            int(self.x -
                self.width / 2),
            int(self.y -
                self.height / 2),
            self.width,
            self.height
        )

    def draw(self, surface):

        rect = self.rect()

        # Shadow

        pygame.draw.ellipse(
            surface,
            (
                0,
                0,
                0
            ),
            (
                rect.x + 5,
                rect.y + 7,
                rect.width,
                rect.height
            ),
        )

        # Main object

        pygame.draw.circle(
            surface,
            self.color,
            rect.center,
            self.width // 2
        )

        # Outer ring

        pygame.draw.circle(
            surface,
            WHITE,
            rect.center,
            self.width // 2,
            3
        )

        # Symbol

        symbol_image = FONT_MEDIUM.render(
            self.symbol,
            True,
            WHITE
        )

        symbol_rect = symbol_image.get_rect(
            center=rect.center
        )

        surface.blit(
            symbol_image,
            symbol_rect
        )


# ============================================================
# CLOUD
# ============================================================

class Cloud:

    def __init__(
        self,
        x,
        y,
        scale=1.0,
        speed=20
    ):

        self.x = x
        self.y = y
        self.scale = scale
        self.speed = speed

    def update(self, dt):

        self.x += (
            self.speed * dt
        )

        if self.x > WIDTH + 200:
            self.x = -250

    def draw(self, surface):

        color = (
            255,
            255,
            255
        )

        r1 = int(30 * self.scale)
        r2 = int(45 * self.scale)
        r3 = int(35 * self.scale)

        pygame.draw.circle(
            surface,
            color,
            (
                int(self.x),
                int(self.y)
            ),
            r1
        )

        pygame.draw.circle(
            surface,
            color,
            (
                int(
                    self.x +
                    35 *
                    self.scale
                ),
                int(
                    self.y - 15 *
                    self.scale
                )
            ),
            r2
        )

        pygame.draw.circle(
            surface,
            color,
            (
                int(
                    self.x +
                    75 *
                    self.scale
                ),
                int(self.y)
            ),
            r3
        )

        pygame.draw.rect(
            surface,
            color,
            (
                int(
                    self.x -
                    5 *
                    self.scale
                ),
                int(self.y),
                int(
                    85 *
                    self.scale
                ),
                int(
                    30 *
                    self.scale
                )
            )
        )


# ============================================================
# TREE
# ============================================================

class Tree:

    def __init__(
        self,
        x,
        y,
        scale=1.0
    ):

        self.x = x
        self.y = y
        self.scale = scale

    def draw(
        self,
        surface,
        health
    ):

        # Tree grows as health improves

        scale = (
            self.scale *
            (0.75 + health *
             0.5)
        )

        trunk_width = int(
            20 * scale
        )

        trunk_height = int(
            85 * scale
        )

        pygame.draw.rect(
            surface,
            BROWN,
            (
                int(
                    self.x -
                    trunk_width /
                    2
                ),
                int(
                    self.y -
                    trunk_height
                ),
                trunk_width,
                trunk_height
            )
        )

        leaf_radius = int(
            50 * scale
        )

        pygame.draw.circle(
            surface,
            DARK_GREEN,
            (
                int(self.x),
                int(
                    self.y -
                    trunk_height
                )
            ),
            leaf_radius
        )

        pygame.draw.circle(
            surface,
            GREEN,
            (
                int(
                    self.x -
                    leaf_radius /
                    2
                ),
                int(
                    self.y -
                    trunk_height /
                    2
                )
            ),
            int(
                leaf_radius *
                0.75
            )
        )

        pygame.draw.circle(
            surface,
            LIGHT_GREEN,
            (
                int(
                    self.x +
                    leaf_radius /
                    2
                ),
                int(
                    self.y -
                    trunk_height /
                    2
                )
            ),
            int(
                leaf_radius *
                0.65
            )
        )


# ============================================================
# PLAYER
# ============================================================

class Player:

    def __init__(
        self,
        x,
        y
    ):

        self.x = x
        self.y = y

        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT

        self.target_x = x

        self.speed = PLAYER_SPEED

        self.bounce = 0

        self.hit_flash = 0

    def update(
        self,
        dt,
        move_left,
        move_right,
        game_width
    ):

        if move_left:

            self.x -= (
                self.speed *
                dt
            )

        if move_right:

            self.x += (
                self.speed *
                dt
            )

        self.x = clamp(
            self.x,
            10,
            game_width -
            self.width -
            10
        )

        self.bounce += (
            dt * 5
        )

        if self.hit_flash > 0:
            self.hit_flash -= dt

    def rect(self):

        return pygame.Rect(
            int(self.x),
            int(self.y),
            self.width,
            self.height
        )

    def draw(self, surface):

        rect = self.rect()

        offset = int(
            math.sin(
                self.bounce
            ) * 3
        )

        # Shadow

        pygame.draw.ellipse(
            surface,
            (
                60,
                100,
                60
            ),
            (
                rect.x + 10,
                rect.bottom - 5,
                rect.width - 20,
                16
            )
        )

        # Basket body

        basket_color = (
            RED
            if self.hit_flash > 0
            else DARK_GREEN
        )

        pygame.draw.rounded_rect(
            surface,
            basket_color,
            (
                rect.x,
                rect.y + offset,
                rect.width,
                rect.height - 10
            ),
            18
        )

        # Basket outline

        pygame.draw.rounded_rect(
            surface,
            WHITE,
            (
                rect.x,
                rect.y + offset,
                rect.width,
                rect.height - 10
            ),
            18,
            4
        )

        # Handle

        pygame.draw.arc(
            surface,
            WHITE,
            (
                rect.x + 20,
                rect.y - 28 + offset,
                rect.width - 40,
                55
            ),
            math.pi,
            2 * math.pi,
            6
        )

        # Label

        image = FONT_SMALL.render(
            "ECO",
            True,
            WHITE
        )

        image_rect = image.get_rect(
            center=(
                rect.centerx,
                rect.centery + offset
            )
        )

        surface.blit(
            image,
            image_rect
        )


# ============================================================
# GAME CLASS
# ============================================================

class EcoCatchers:

    def __init__(self):

        self.state = "menu"

        self.score = 0

        self.high_score = (
            load_high_score()
        )

        self.lives = STARTING_LIVES

        self.time_left = (
            GAME_LENGTH
        )

        self.combo = 1

        self.combo_timer = 0

        self.spawn_timer = 0

        self.objects = []

        self.particles = []

        self.clouds = [
            Cloud(
                100,
                100,
                1.0,
                18
            ),
            Cloud(
                500,
                160,
                0.8,
                12
            ),
            Cloud(
                900,
                90,
                1.2,
                15
            ),
        ]

        self.trees = [
            Tree(
                100,
                HEIGHT - 80,
                1.0
            ),
            Tree(
                220,
                HEIGHT - 75,
                0.8
            ),
            Tree(
                WIDTH - 120,
                HEIGHT - 80,
                1.1
            ),
            Tree(
                WIDTH - 250,
                HEIGHT - 80,
                0.8
            ),
        ]

        self.player = Player(
            WIDTH // 2,
            HEIGHT - 140
        )

        self.running = True

        self.screen_shake = 0

        self.message = ""

        self.message_timer = 0

        self.last_good = None

    # --------------------------------------------------------
    # RESET GAME
    # --------------------------------------------------------

    def reset(self):

        self.score = 0

        self.lives = STARTING_LIVES

        self.time_left = GAME_LENGTH

        self.combo = 1

        self.combo_timer = 0

        self.spawn_timer = 0

        self.objects.clear()

        self.particles.clear()

        self.message = ""

        self.message_timer = 0

        self.screen_shake = 0

        self.player = Player(
            WIDTH // 2,
            HEIGHT - 140
        )

    # --------------------------------------------------------
    # START
    # --------------------------------------------------------

    def start(self):

        self.reset()

        self.state = "playing"

    # --------------------------------------------------------
    # END GAME
    # --------------------------------------------------------

    def end_game(self):

        self.state = "gameover"

        if self.score > self.high_score:

            self.high_score = self.score

            save_high_score(
                self.high_score
            )

    # --------------------------------------------------------
    # PARTICLES
    # --------------------------------------------------------

    def add_particles(
        self,
        x,
        y,
        color,
        amount=12,
        text=None
    ):

        for _ in range(amount):

            if len(self.particles) >= MAX_PARTICLES:
                break

            self.particles.append(
                Particle(
                    x,
                    y,
                    color,
                    text
                )
            )

    # --------------------------------------------------------
    # SPAWN
    # --------------------------------------------------------

    def spawn_object(self):

        # Game gets harder over time

        elapsed = (
            GAME_LENGTH -
            self.time_left
        )

        speed_multiplier = (
            1.0 +
            elapsed * 0.012
        )

        obj = FallingObject(
            WIDTH,
            speed_multiplier
        )

        self.objects.append(obj)

    # --------------------------------------------------------
    # COLLISION
    # --------------------------------------------------------

    def check_collision(
        self,
        object_rect
    ):

        player_rect = (
            self.player.rect()
        )

        # Slightly smaller hitbox
        # makes game feel fairer

        player_rect.inflate_ip(
            -25,
            -15
        )

        object_rect = (
            object_rect.inflate(
                -10,
                -10
            )
        )

        return player_rect.colliderect(
            object_rect
        )

    # --------------------------------------------------------
    # COLLECT
    # --------------------------------------------------------

    def collect_object(
        self,
        obj
    ):

        x = obj.x

        y = obj.y

        if obj.good:

            points = (
                obj.points *
                self.combo
            )

            self.score += points

            self.combo += 1

            self.combo = clamp(
                self.combo,
                1,
                8
            )

            self.combo_timer = 2.5

            self.last_good = obj.name

            self.message = (
                f"+{points}  "
                f"{obj.name}"
            )

            self.message_timer = 1.2

            self.add_particles(
                x,
                y,
                obj.color,
                15,
                f"+{points}"
            )

            # Special combo effect

            if self.combo >= 3:

                self.add_particles(
                    x,
                    y - 25,
                    ORANGE,
                    5,
                    f"COMBO x{self.combo}"
                )

        else:

            self.lives -= obj.damage

            self.lives = max(
                0,
                self.lives
            )

            self.combo = 1

            self.combo_timer = 0

            self.player.hit_flash = 0.4

            self.screen_shake = 0.35

            self.message = (
                f"AVOID {obj.name}!"
            )

            self.message_timer = 1.2

            self.add_particles(
                x,
                y,
                RED,
                20,
                "- LIFE"
            )

            if self.lives <= 0:

                self.end_game()

    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    def update(
        self,
        dt
    ):

        # Background animation

        for cloud in self.clouds:
            cloud.update(dt)

        if self.state != "playing":
            return

        # ----------------------------------------------------
        # TIMER
        # ----------------------------------------------------

        self.time_left -= dt

        if self.time_left <= 0:

            self.time_left = 0

            self.end_game()

            return

        # ----------------------------------------------------
        # COMBO TIMER
        # ----------------------------------------------------

        if self.combo_timer > 0:

            self.combo_timer -= dt

        else:

            self.combo = 1

        # ----------------------------------------------------
        # PLAYER
        # ----------------------------------------------------

        keys = pygame.key.get_pressed()

        move_left = (
            keys[pygame.K_LEFT]
            or
            keys[pygame.K_a]
        )

        move_right = (
            keys[pygame.K_RIGHT]
            or
            keys[pygame.K_d]
        )

        self.player.update(
            dt,
            move_left,
            move_right,
            WIDTH
        )

        # ----------------------------------------------------
        # OBJECT SPAWNING
        # ----------------------------------------------------

        self.spawn_timer += dt

        elapsed = (
            GAME_LENGTH -
            self.time_left
        )

        spawn_rate = max(
            0.28,
            0.80 -
            elapsed * 0.007
        )

        if self.spawn_timer >= spawn_rate:

            self.spawn_object()

            self.spawn_timer = 0

        # ----------------------------------------------------
        # OBJECT MOVEMENT
        # ----------------------------------------------------

        remaining_objects = []

        for obj in self.objects:

            obj.update(dt)

            if self.check_collision(
                obj.rect()
            ):

                self.collect_object(
                    obj
                )

                continue

            if obj.y < HEIGHT + 100:

                remaining_objects.append(
                    obj
                )

        self.objects = (
            remaining_objects
        )

        # ----------------------------------------------------
        # PARTICLES
        # ----------------------------------------------------

        remaining_particles = []

        for particle in self.particles:

            particle.update(dt)

            if particle.life > 0:

                remaining_particles.append(
                    particle
                )

        self.particles = (
            remaining_particles
        )

        # ----------------------------------------------------
        # MESSAGE
        # ----------------------------------------------------

        if self.message_timer > 0:

            self.message_timer -= dt

        # ----------------------------------------------------
        # SCREEN SHAKE
        # ----------------------------------------------------

        if self.screen_shake > 0:

            self.screen_shake -= dt

    # --------------------------------------------------------
    # DRAW BACKGROUND
    # --------------------------------------------------------

    def draw_background(
        self,
        surface
    ):

        # ----------------------------------------------------
        # SKY GRADIENT
        # ----------------------------------------------------

        for y in range(
            HEIGHT
        ):

            ratio = (
                y /
                HEIGHT
            )

            color = (
                int(
                    lerp(
                        SKY_TOP[0],
                        SKY_BOTTOM[0],
                        ratio
                    )
                ),
                int(
                    lerp(
                        SKY_TOP[1],
                        SKY_BOTTOM[1],
                        ratio
                    )
                ),
                int(
                    lerp(
                        SKY_TOP[2],
                        SKY_BOTTOM[2],
                        ratio
                    )
                )
            )

            pygame.draw.line(
                surface,
                color,
                (0, y),
                (WIDTH, y)
            )

        # ----------------------------------------------------
        # SUN
        # ----------------------------------------------------

        pygame.draw.circle(
            surface,
            YELLOW,
            (
                WIDTH - 110,
                100
            ),
            45
        )

        pygame.draw.circle(
            surface,
            (
                255,
                225,
                100
            ),
            (
                WIDTH - 110,
                100
            ),
            55,
            3
        )

        # ----------------------------------------------------
        # CLOUDS
        # ----------------------------------------------------

        for cloud in self.clouds:
            cloud.draw(surface)

        # ----------------------------------------------------
        # HILLS
        # ----------------------------------------------------

        pygame.draw.ellipse(
            surface,
            (
                80,
                180,
                100
            ),
            (
                -200,
                HEIGHT - 280,
                700,
                300
            )
        )

        pygame.draw.ellipse(
            surface,
            (
                60,
                160,
                80
            ),
            (
                400,
                HEIGHT - 240,
                750,
                280
            )
        )

        # ----------------------------------------------------
        # GROUND
        # ----------------------------------------------------

        pygame.draw.rect(
            surface,
            (
                55,
                150,
                70
            ),
            (
                0,
                HEIGHT - 100,
                WIDTH,
                100
            )
        )

        # Grass lines

        for x in range(
            0,
            WIDTH,
            30
        ):

            pygame.draw.line(
                surface,
                (
                    80,
                    180,
                    80
                ),
                (
                    x,
                    HEIGHT - 100
                ),
                (
                    x + 8,
                    HEIGHT - 112
                ),
                3
            )

        # Trees grow based on score

        environment = min(
            1.0,
            self.score / 300
        )

        for tree in self.trees:

            tree.draw(
                surface,
                environment
            )

    # --------------------------------------------------------
    # DRAW HUD
    # --------------------------------------------------------

    def draw_hud(
        self,
        surface
    ):

        # Main HUD background

        pygame.draw.rounded_rect(
            surface,
            (
                255,
                255,
                255
            ),
            (
                20,
                20,
                WIDTH - 40,
                100
            ),
            22
        )

        # Border

        pygame.draw.rounded_rect(
            surface,
            (
                220,
                230,
                225
            ),
            (
                20,
                20,
                WIDTH - 40,
                100
            ),
            22,
            3
        )

        # ----------------------------------------------------
        # SCORE
        # ----------------------------------------------------

        score_label = FONT_SMALL.render(
            "SCORE",
            True,
            GRAY
        )

        surface.blit(
            score_label,
            (
                50,
                35
            )
        )

        score_text = FONT_LARGE.render(
            str(self.score),
            True,
            DARK_GREEN
        )

        surface.blit(
            score_text,
            (
                45,
                55
            )
        )

        # ----------------------------------------------------
        # HIGH SCORE
        # ----------------------------------------------------

        high_label = FONT_SMALL.render(
            "BEST",
            True,
            GRAY
        )

        surface.blit(
            high_label,
            (
                240,
                35
            )
        )

        high_text = FONT_LARGE.render(
            str(
                max(
                    self.high_score,
                    self.score
                )
            ),
            True,
            PURPLE
        )

        surface.blit(
            high_text,
            (
                235,
                55
            )
        )

        # ----------------------------------------------------
        # COMBO
        # ----------------------------------------------------

        combo_label = FONT_SMALL.render(
            "COMBO",
            True,
            GRAY
        )

        surface.blit(
            combo_label,
            (
                420,
                35
            )
        )

        combo_text = FONT_LARGE.render(
            f"x{self.combo}",
            True,
            ORANGE
        )

        surface.blit(
            combo_text,
            (
                420,
                55
            )
        )

        # ----------------------------------------------------
        # LIVES
        # ----------------------------------------------------

        lives_label = FONT_SMALL.render(
            "LIVES",
            True,
            GRAY
        )

        surface.blit(
            lives_label,
            (
                620,
                35
            )
        )

        hearts = "♥ " * self.lives

        lives_text = FONT_MEDIUM.render(
            hearts,
            True,
            RED
        )

        surface.blit(
            lives_text,
            (
                610,
                66
            )
        )

        # ----------------------------------------------------
        # TIMER
        # ----------------------------------------------------

        timer_label = FONT_SMALL.render(
            "TIME",
            True,
            GRAY
        )

        surface.blit(
            timer_label,
            (
                WIDTH - 250,
                35
            )
        )

        timer_color = (
            RED
            if self.time_left <= 10
            else BLUE
        )

        timer_text = FONT_LARGE.render(
            str(
                math.ceil(
                    self.time_left
                )
            ),
            True,
            timer_color
        )

        surface.blit(
            timer_text,
            (
                WIDTH - 250,
                55
            )
        )

        # ----------------------------------------------------
        # TIME BAR
        # ----------------------------------------------------

        bar_x = WIDTH - 160
        bar_y = 65
        bar_width = 100
        bar_height = 15

        pygame.draw.rounded_rect(
            surface,
            LIGHT_GRAY,
            (
                bar_x,
                bar_y,
                bar_width,
                bar_height
            ),
            8
        )

        progress = (
            self.time_left /
            GAME_LENGTH
        )

        pygame.draw.rounded_rect(
            surface,
            (
                GREEN
                if self.time_left > 10
                else RED
            ),
            (
                bar_x,
                bar_y,
                int(
                    bar_width *
                    progress
                ),
                bar_height
            ),
            8
        )

    # --------------------------------------------------------
    # DRAW GAME MESSAGE
    # --------------------------------------------------------

    def draw_message(
        self,
        surface
    ):

        if self.message_timer <= 0:
            return

        image = FONT_MEDIUM.render(
            self.message,
            True,
            WHITE
        )

        padding_x = 25
        padding_y = 12

        box_width = (
            image.get_width() +
            padding_x * 2
        )

        box_height = (
            image.get_height() +
            padding_y * 2
        )

        rect = pygame.Rect(
            WIDTH // 2 -
            box_width // 2,
            135,
            box_width,
            box_height
        )

        pygame.draw.rounded_rect(
            surface,
            DARK_GREEN,
            rect,
            20
        )

        surface.blit(
            image,
            (
                rect.centerx -
                image.get_width() / 2,
                rect.centery -
                image.get_height() / 2
            )
        )

    # --------------------------------------------------------
    # DRAW PLAYING
    # --------------------------------------------------------

    def draw_playing(
        self,
        surface
    ):

        self.draw_background(
            surface
        )

        self.draw_hud(
            surface
        )

        # Falling objects

        for obj in self.objects:
            obj.draw(surface)

        # Player

        self.player.draw(
            surface
        )

        # Particles

        for particle in self.particles:
            particle.draw(surface)

        # Message

        self.draw_message(
            surface
        )

        # Controls hint

        controls = FONT_SMALL.render(
            "← A     MOVE     D →",
            True,
            WHITE
        )

        controls_rect = controls.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT - 30
            )
        )

        # Shadow

        shadow = FONT_SMALL.render(
            "← A     MOVE     D →",
            True,
            DARK_GREEN
        )

        shadow_rect = shadow.get_rect(
            center=(
                WIDTH // 2 + 2,
                HEIGHT - 28
            )
        )

        surface.blit(
            shadow,
            shadow_rect
        )

        surface.blit(
            controls,
            controls_rect
        )

    # --------------------------------------------------------
    # DRAW MENU
    # --------------------------------------------------------

    def draw_menu(
        self,
        surface
    ):

        # Background

        self.draw_background(
            surface
        )

        # Dark overlay

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill(
            (
                0,
                60,
                30,
                130
            )
        )

        surface.blit(
            overlay,
            (
                0,
                0
            )
        )

        # Main card

        card = pygame.Rect(
            WIDTH // 2 - 400,
            70,
            800,
            560
        )

        pygame.draw.rounded_rect(
            surface,
            (
                255,
                255,
                255
            ),
            card,
            35
        )

        # Planet

        pygame.draw.circle(
            surface,
            (
                60,
                175,
                230
            ),
            (
                WIDTH // 2,
                170
            ),
            75
        )

        pygame.draw.circle(
            surface,
            (
                50,
                150,
                70
            ),
            (
                WIDTH // 2 - 25,
                150
            ),
            25
        )

        pygame.draw.circle(
            surface,
            (
                50,
                150,
                70
            ),
            (
                WIDTH // 2 + 35,
                190
            ),
            18
        )

        # Title

        title = FONT_HUGE.render(
            "ECO CATCHERS",
            True,
            DARK_GREEN
        )

        title_rect = title.get_rect(
            center=(
                WIDTH // 2,
                280
            )
        )

        surface.blit(
            title,
            title_rect
        )

        # Subtitle

        subtitle = FONT_MEDIUM.render(
            "Catch the good. Avoid the pollution.",
            True,
            GRAY
        )

        subtitle_rect = subtitle.get_rect(
            center=(
                WIDTH // 2,
                340
            )
        )

        surface.blit(
            subtitle,
            subtitle_rect
        )

        # Instructions

        instructions = [
            "♻  Catch recycling and eco-friendly objects",
            "☠  Avoid pollution and hazardous objects",
            "🔥  Build combos for bigger scores",
            "❤️  You have 3 lives",
        ]

        y = 380

        for line in instructions:

            # Some systems don't have emoji
            # so fallback is automatically
            # handled by text rendering.

            image = FONT_SMALL.render(
                line,
                True,
                BLACK
            )

            rect = image.get_rect(
                center=(
                    WIDTH // 2,
                    y
                )
            )

            surface.blit(
                image,
                rect
            )

            y += 35

        # Start button

        button = pygame.Rect(
            WIDTH // 2 - 150,
            525,
            300,
            65
        )

        pygame.draw.rounded_rect(
            surface,
            DARK_GREEN,
            button,
            20
        )

        pygame.draw.rounded_rect(
            surface,
            GREEN,
            button,
            20,
            4
        )

        button_text = FONT_MEDIUM.render(
            "START GAME",
            True,
            WHITE
        )

        button_rect = (
            button_text.get_rect(
                center=button.center
            )
        )

        surface.blit(
            button_text,
            button_rect
        )

        # Best score

        best = FONT_SMALL.render(
            f"Best Score: {self.high_score}",
            True,
            PURPLE
        )

        best_rect = best.get_rect(
            center=(
                WIDTH // 2,
                610
            )
        )

        surface.blit(
            best,
            best_rect
        )

    # --------------------------------------------------------
    # DRAW GAME OVER
    # --------------------------------------------------------

    def draw_game_over(
        self,
        surface
    ):

        self.draw_background(
            surface
        )

        # Overlay

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill(
            (
                0,
                30,
                20,
                150
            )
        )

        surface.blit(
            overlay,
            (
                0,
                0
            )
        )

        card = pygame.Rect(
            WIDTH // 2 - 350,
            80,
            700,
            530
        )

        pygame.draw.rounded_rect(
            surface,
            WHITE,
            card,
            35
        )

        # Result

        if self.score >= self.high_score:

            title_text = "NEW RECORD!"

            title_color = ORANGE

        else:

            title_text = "GAME OVER"

            title_color = DARK_GREEN

        title = FONT_LARGE.render(
            title_text,
            True,
            title_color
        )

        title_rect = title.get_rect(
            center=(
                WIDTH // 2,
                150
            )
        )

        surface.blit(
            title,
            title_rect
        )

        # Trophy

        trophy = FONT_HUGE.render(
            "★",
            True,
            YELLOW
        )

        trophy_rect = trophy.get_rect(
            center=(
                WIDTH // 2,
                240
            )
        )

        surface.blit(
            trophy,
            trophy_rect
        )

        # Score label

        score_label = FONT_SMALL.render(
            "YOUR ECO SCORE",
            True,
            GRAY
        )

        score_label_rect = score_label.get_rect(
            center=(
                WIDTH // 2,
                310
            )
        )

        surface.blit(
            score_label,
            score_label_rect
        )

        # Score

        score = FONT_HUGE.render(
            str(self.score),
            True,
            DARK_GREEN
        )

        score_rect = score.get_rect(
            center=(
                WIDTH // 2,
                370
            )
        )

        surface.blit(
            score,
            score_rect
        )

        # Best score

        best = FONT_MEDIUM.render(
            f"Best Score: {self.high_score}",
            True,
            PURPLE
        )

        best_rect = best.get_rect(
            center=(
                WIDTH // 2,
                430
            )
        )

        surface.blit(
            best,
            best_rect
        )

        # Button

        button = pygame.Rect(
            WIDTH // 2 - 140,
            480,
            280,
            60
        )

        pygame.draw.rounded_rect(
            surface,
            GREEN,
            button,
            18
        )

        replay = FONT_MEDIUM.render(
            "PLAY AGAIN",
            True,
            WHITE
        )

        replay_rect = replay.get_rect(
            center=button.center
        )

        surface.blit(
            replay,
            replay_rect
        )

        # Hint

        hint = FONT_SMALL.render(
            "Press SPACE to restart",
            True,
            GRAY
        )

        hint_rect = hint.get_rect(
            center=(
                WIDTH // 2,
                570
            )
        )

        surface.blit(
            hint,
            hint_rect
        )

    # --------------------------------------------------------
    # DRAW
    # --------------------------------------------------------

    def draw(self):

        # ----------------------------------------------------
        # SCREEN SHAKE
        # ----------------------------------------------------

        shake_x = 0
        shake_y = 0

        if self.screen_shake > 0:

            shake_x = random.randint(
                -6,
                6
            )

            shake_y = random.randint(
                -6,
                6
            )

        # Temporary surface

        game_surface = pygame.Surface(
            (
                WIDTH,
                HEIGHT
            )
        )

        if self.state == "menu":

            self.draw_menu(
                game_surface
            )

        elif self.state == "playing":

            self.draw_playing(
                game_surface
            )

        elif self.state == "gameover":

            self.draw_game_over(
                game_surface
            )

        # Put surface on screen

        screen.fill(
            BLACK
        )

        screen.blit(
            game_surface,
            (
                shake_x,
                shake_y
            )
        )

        pygame.display.flip()

    # --------------------------------------------------------
    # MOUSE
    # --------------------------------------------------------

    def mouse_start_button(
        self,
        position
    ):

        x, y = position

        button = pygame.Rect(
            WIDTH // 2 - 150,
            525,
            300,
            65
        )

        return button.collidepoint(
            x,
            y
        )

    def mouse_game_over_button(
        self,
        position
    ):

        x, y = position

        button = pygame.Rect(
            WIDTH // 2 - 140,
            480,
            280,
            60
        )

        return button.collidepoint(
            x,
            y
        )

    # --------------------------------------------------------
    # EVENTS
    # --------------------------------------------------------

    def handle_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                self.running = False

            # -----------------------------------------------
            # KEYBOARD
            # -----------------------------------------------

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    self.running = False

                if (
                    event.key ==
                    pygame.K_SPACE
                ):

                    if self.state in (
                        "menu",
                        "gameover"
                    ):

                        self.start()

            # -----------------------------------------------
            # MOUSE
            # -----------------------------------------------

            if event.type == pygame.MOUSEBUTTONDOWN:

                position = event.pos

                if self.state == "menu":

                    if self.mouse_start_button(
                        position
                    ):

                        self.start()

                elif self.state == "gameover":

                    if self.mouse_game_over_button(
                        position
                    ):

                        self.start()

    # --------------------------------------------------------
    # MAIN LOOP
    # --------------------------------------------------------

    def run(self):

        while self.running:

            dt = (
                clock.tick(FPS) /
                1000.0
            )

            # Prevent giant delta
            # after window lag

            dt = min(
                dt,
                0.05
            )

            self.handle_events()

            self.update(
                dt
            )

            self.draw()

        pygame.quit()

        sys.exit()


# ============================================================
# RUN GAME
# ============================================================

if __name__ == "__main__":

    game = EcoCatchers()

    game.run()
