"""Engine constants and configuration."""
import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DATA_DIR = os.path.join(BASE_DIR, "data")
SAVES_DIR = os.path.join(BASE_DIR, "saves")

# Display
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Adventure Game"

# Player identity (used as default speaker/actor in scripts and dialogues)
PLAYER_ID = "player"

# Player movement (pixels per second)
WALK_SPEED = 180
RUN_SPEED = 340

# Animation
ANIM_FPS = 8  # Frames per second for character animation

# Depth scaling defaults
DEFAULT_HORIZON_Y = 200
DEFAULT_GROUND_Y = 680
DEFAULT_MIN_SCALE = 0.4
DEFAULT_MAX_SCALE = 1.0

# Camera
CAMERA_SMOOTHING = 5.0  # Higher = snappier follow
CAMERA_DEAD_ZONE = 50   # Pixels from center before camera moves

# UI
INVENTORY_HEIGHT = 80
INVENTORY_SLOT_SIZE = 64
INVENTORY_SLIDE_SPEED = 400  # Pixels per second

# Speech bubbles
SPEECH_FONT_SIZE = 20
SPEECH_SHOUT_FONT_SIZE = 24
SPEECH_TYPEWRITER_SPEED = 40  # Characters per second
SPEECH_PADDING = 12
SPEECH_MAX_WIDTH = 300
SPEECH_POINTER_SIZE = 12

# Fonts (filenames in assets/fonts/)
FONT_NORMAL = "adventure.ttf"
FONT_SHOUT = "adventure_shout.ttf"

# Radial menu
RADIAL_RADIUS = 60
RADIAL_ICON_SIZE = 32

# Transitions
FADE_DURATION = 0.5  # Seconds for fade in/out

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_SPEECH_BG = (255, 255, 240)
COLOR_SPEECH_BORDER = (40, 40, 40)
COLOR_INVENTORY_BG = (45, 35, 25, 220)
COLOR_INVENTORY_SLOT = (80, 65, 50)
COLOR_INVENTORY_HIGHLIGHT = (200, 170, 100)
COLOR_MENU_BG = (50, 40, 30, 230)
COLOR_MENU_TEXT = (240, 220, 180)
COLOR_MENU_HIGHLIGHT = (255, 200, 80)
COLOR_DIALOGUE_BG = (0, 0, 0, 180)
COLOR_DIALOGUE_CHOICE = (240, 220, 180)
COLOR_DIALOGUE_HOVER = (255, 200, 80)

# Magenta colorkey for sprite sheets
COLORKEY_MAGENTA = (255, 0, 255)

# Sprite scaling
PLAYER_SPRITE_SCALE = 0.295   # Scale for real player walk sprites
COMPANION_SPRITE_SCALE = 0.18  # Scale for real companion walk sprites
PLACEHOLDER_SCALE = 2          # Scale for placeholder character sprites

# Double-click detection
DOUBLE_CLICK_TIME = 0.35  # Seconds

# Companion character
COMPANION_FOLLOW_DISTANCE = 70
COMPANION_FOLLOW_SPEED_MULT = 1.1  # Slightly faster to catch up

# Sound
MUSIC_VOLUME = 0.5
SFX_VOLUME = 0.7
MUSIC_FADEOUT_MS = 1000
