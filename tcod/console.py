import sys, platform
import os.path
from warnings import warn
from MapChunk import Player

linux_path = '/home/millejoh/Documents/libtcod/python/'
win_path = 'c:/Users/E341194/Applications/libtcod-1.5.2/python/'

try:
    from IPython import embed_kernel
except ImportError:
    pass

if platform.system() == 'Linux':
    root_dir = b'/home/millejoh/Documents/libtcod/'
    if linux_path not in sys.path:
        sys.path.append(linux_path)
elif platform.system() == 'Windows':
    root_dir = b'c:/Users/E341194/Applications/libtcod-1.5.2/'
    if win_path not in sys.path:
        sys.path.append(win_path)

try:
    import libtcodpy as tcod
except:
    print('I am running on {0} and I cannot find tcodpy.'.format(platform.system()))

root_console = 0 # This means NULL for you C folk.
default_font = os.path.join(root_dir, b'data/fonts/consolas10x10_gs_tc.png')

key_dispatch_table = {}

# Make a subclass of Tuple?
class ConsoleCell(object):
    """Represent a console cell as a 3-element tuple: symbol (or character), foreground color,
and background color."""
    def __init__(self, symbol=' ', foreground=None, background=None):
        self.symbol = symbol
        self.foreground = foreground
        self.background = background

    def __repr__(self):
        return 'ConsoleCell({0},{1},{2})'.format(self.symbol, self.foreground, self.background)

class Console(object):
    def __init__(self, width, height):
        self.width = width
        self.heigh = height
        self._c = tcod.console_new(width, height)

    def __del__(self):
        tcod.console_delete(self._c)

    def __len__(self):
        return self.width*self.height

    def __getitem__(self, index):
        if isinstance(index, slice):
            raise TypeError('Console objects do not support slices. Yet.')
        x, y = index
        if x > self.width or x < 0 or y > self.height or y < 0:
            raise IndexError('Attempt to access cell ({0}, {1}), which is out of range. Console size is ({2}, {3}).'.format(x, y, self.width, self.height))

        return (chr(tcod.console_get_char(self._c, x, y)),
                tcod.console_get_char_foreground(self._c, x, y),
                tcod.console_get_char_background(self._c, x, y))
    
    def __setitem__(self, index, cell):
        if isinstance(index, slice):
            raise TypeError('Console objects do not support slices. Yet.')
        x, y = index
        if x > self.width or x < 0 or y > self.height or y < 0:
            raise IndexError('Attempt to access cell ({0}, {1}), which is out of range. Console size is ({2}, {3}).'.format(x, y, self.width, self.height))
        
        if cell is tuple and len(cell) > 3:
            symbol, foreground, background = cell
        elif cell is not tuple:
            symbol = cell
            foreground = self.foreground
            background = self.background
        else:
            symbol = cell[0]
            foreground = self.foreground
            background = self.background

        tcod.console_put_char_ex(self._c, x, y, symbol, foreground, background)

    @property
    def keyboard_repeat(self):
        return self._keyrepeat

    @keyboard_repeat.setter
    def keyboard_repeat(self, val):
        self._keyrepeat = val
        tcod.console_set_keyboard_repeat(self._c, *val)

    @property
    def background(self):
        return tcod.console_get_default_background(self._c)

    @background.setter
    def background(self, color):
        tcod.console_set_default_background(self._c, color)

    @property
    def foreground(self):
        return tcod.console_get_default_foreground(self._c)

    @foreground.setter
    def foreground(self, color):
        tcod.console_set_default_foreground(self._c, color)

    @property
    def alignment(self):
        return tcod.console_get_alignment(self._c)

    @alignment.setter
    def alignment(self, alignment):
        tcod.console_set_alignment(self._c, alignment)

    @property
    def background_flag(self):
        tcod.console_get_background_flag(self._c)

    @background_flag.setter
    def background_flag(self, flag):
        tcod.console_set_background_flag(self._c, flag)

    @property
    def window_closed(self):
        return tcod.console_is_window_closed()

    def put_cell(self, x, y, sym, flag=tcod.BKGND_NONE):
        tcod.console_put_char(self._c, x, y, sym, flag)

    def write(self, x, y, fmt):
        tcod.console_print(self._c, x, y, fmt)

    def write_rect(self, x, y, w, h, fmt):
        tcod.console_print_rect(self._c, x, y, w, h, fmt)

    def get_text_height(self, x, y, w, h, fmt):
        return tcod.console_get_height_rect(self._c, x, y, w, h, fmt)

    def draw_rect(self, x, y, w, h, clear=False, flag=tcod.BKGND_NONE):
        tcod.console_rect(self._c, x, y, w, h, clear, flag)

    def hline(self, x, y, length, flag=tcod.BKGND_NONE):
        tcod.console_hline(self._c, x, y, length, flag)

    def vline(self, x, y, length, flag=tcod.BKGND_NONE):
        tcod.console_vline(self._c, x, y, length, flag)
    
    def frame(self, x, y, w, h, text, clear=True, flag=tcod.BKGND_NONE):
        tcod.console_print_frame(self._c, x, y, w, h, clear, flag, text)

    def clear(self):
        tcod.console_clear(self._c)

class RootConsole(Console):
    active_root = None

    def __init__(self, width=80, height=50, title=b'Stage', background = tcod.darker_sepia, font_file=default_font, datax='', fullscreen=False, renderer=tcod.RENDERER_GLSL, max_fps=30):
        if RootConsole.active_root:
            warn('Root console already initialized. Any parameters supplied with call are being ignored.')
        else:
            if os.path.exists(font_file):
                tcod.console_set_custom_font(font_file, tcod.FONT_LAYOUT_TCOD |
                                             tcod.FONT_TYPE_GREYSCALE)
            else:
                raise OSError("Font file {0} not found.".format(font_file))

            tcod.console_init_root(width, height, title,
                                   fullscreen, renderer)
            tcod.sys_set_fps(max_fps)
            self._c = root_console
            self.width = width
            self.height = height
            self.title = title
            self.fullscreen = fullscreen
            self.renderer = renderer
            self.end_game = False
            self.max_fps = max_fps
            self.background = background
            RootConsole.active_root = self

    def flush(self):
        tcod.console_flush()

    def handle_events(self):
        mouse, key = tcod.Mouse(), tcod.Key()
        tcod.sys_check_for_event(tcod.EVENT_ANY, key, mouse)
        return key, mouse
    
    def run(self):

        while (not self.end_game) and (not tcod.console_is_window_closed()):
            key, mouse = self.handle_events()
            self.handle_keys(key)
            if key.vk == tcod.KEY_ESCAPE:
                tcod.console_clear(root_console)
                tcod.console_print(root_console, 0, 0, "Exiting...")
                tcod.console_flush()
                break
            tcod.console_clear(root_console)
            tcod.console_print(root_console, 0, 0, "Current key pressed is {0}.".format(key.vk))
            tcod.console_print(root_console, 0, 1, "Cursor at ({0}, {1}).".format(mouse.cx, mouse.cy))
            tcod.console_flush()



def gui_loop():
    credits_end = False
    key = tcod.Key()
    mouse = tcod.Mouse()

    while not tcod.console_is_window_closed():
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse)
        tcod.console_set_default_foreground(0, tcod.white)
        if not credits_end:
            credits_end = tcod.console_credits_render(60, 43, 0)
        
        tcod.console_print(0, 0, 1, "Key pressed:{0!a}".format(key.c))
        tcod.console_flush()

        

