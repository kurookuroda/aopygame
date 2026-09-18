import os
import sys
import pygame
from palette import PYXEL_PALETTE
from input_manager import InputManager
from sound_manager import SoundManager

# ===== 設定 =====
FONT_CONFIG = {
    10: "PixelMplus10-Regular.ttf",
    12: "PixelMplus12-Regular.ttf",
}
FONT_SIZE_DEFAULT = 12

SCREEN_W = 256
SCREEN_H = 256

BOX_X = 8
BOX_Y = 8
BOX_W = 240
BOX_H = 240
PADDING = 8
FOOTER_H = 16
MAX_TEXT_W = BOX_W - PADDING * 2

CHAR_INTERVAL = 2
FAST_INTERVAL = 1
FILE_PATH = "aozora_14.txt"

SOUND_CONFIG = {
    'talk':        "beep_talk.wav",
    'talk_space':  "beep_space.wav",
    'talk_fast':   "beep_fast.wav",
    'talk_faster': "beep_faster.wav",
}


def load_paragraphs(path):
    """テキストファイルを読み込み、段落（行）のリストを返す。"""
    if not os.path.exists(path):
        return ["（ファイルが見つかりません）"]
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    return raw.splitlines()


def wrap_paragraphs(paragraphs, font, max_w):
    """段落リストを折り返して行リストにする。"""
    wrapped = []
    for para in paragraphs:
        if para == "":
            wrapped.append("")
            continue
        line = ""
        for ch in para:
            test = line + ch
            if font:
                test_w = font.size(test)[0]
            else:
                test_w = len(test) * 8
            if test_w > max_w:
                if line:
                    wrapped.append(line)
                    line = ch
                else:
                    wrapped.append(ch)
                    line = ""
            else:
                line = test
        if line:
            wrapped.append(line)
    return wrapped


def paginate(lines, rows_per_page):
    """行リストをページ（行のリストのリスト）に分割する。"""
    return [lines[i:i + rows_per_page] for i in range(0, len(lines), rows_per_page)]


class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Aozora Reader (Pygame)")
        self.clock = pygame.time.Clock()
        self.input = InputManager()
        self.sound = SoundManager(SOUND_CONFIG)
        self.frame_count = 0

        # フォント読み込み
        self.fonts = {}
        for size, path in FONT_CONFIG.items():
            self.fonts[size] = self._load_font(path, size)

        self.paragraphs = load_paragraphs(FILE_PATH)

        self.current_size = int(FONT_SIZE_DEFAULT)
        self.font = self._get_font(self.current_size)
        self.line_height = self.current_size + 6

        self._rebuild_pages()

        self.page_index = 0
        self.revealed = 0
        self.timer = 0
        self.page_done = False
        self.skip_cooldown = 0

    def _load_font(self, path, size):
        """フォントファイルを読み込む。無い場合はシステムフォントで代替。"""
        if os.path.exists(path):
            return pygame.font.Font(path, size)

        candidates = [
            "notosanscjkjp",
            "notosansmono",
            "meiryo",
            "yugothic",
            "hiragino sans gb",
            "msmincho",
            "msgothic",
            "monospace",
        ]
        for name in candidates:
            try:
                font = pygame.font.SysFont(name, size)
                if font:
                    return font
            except Exception:
                pass
        return pygame.font.Font(None, size)

    def _get_font(self, size):
        return self.fonts.get(int(size))

    def _rebuild_pages(self):
        self.font = self._get_font(self.current_size)
        self.line_height = int(self.current_size) + 6
        rows_per_page = max(1, (BOX_H - PADDING * 2 - FOOTER_H) // self.line_height)

        wrapped = wrap_paragraphs(self.paragraphs, self.font, MAX_TEXT_W)
        self.pages = paginate(wrapped, rows_per_page)

    def reset(self):
        self.page_index = 0
        self.revealed = 0
        self.timer = 0
        self.page_done = False
        self.skip_cooldown = 0

    def toggle_font_size(self):
        sizes = sorted(FONT_CONFIG.keys())
        idx = sizes.index(int(self.current_size))
        new_size = sizes[(idx + 1) % len(sizes)]

        self.current_size = int(new_size)
        self._rebuild_pages()

        if self.page_index >= len(self.pages):
            self.page_index = max(0, len(self.pages) - 1)

        self.revealed = 0
        self.timer = 0
        self.page_done = False
        self.skip_cooldown = 5

    @property
    def current_page_text(self):
        if 0 <= self.page_index < len(self.pages):
            return "\n".join(self.pages[self.page_index])
        return ""

    def _down_alone_pressed(self):
        down = self.input.btnp('DOWN') or self.input.btnp('PAD_DOWN')
        a_held = self.input.btn('Z') or self.input.btn('PAD_A')
        b_held = self.input.btn('X') or self.input.btn('PAD_B')
        return down and not (a_held or b_held)

    def _skip_pressed(self):
        return (
            self.input.btnp('RETURN')
            or self.input.btnp('MOUSE_LEFT')
            or self._down_alone_pressed()
        )

    def _back_pressed(self):
        return self.input.btnp('UP') or self.input.btnp('PAD_UP')

    def _next_pressed(self):
        return (
            self._down_alone_pressed()
            or self.input.btnp('RETURN')
            or self.input.btnp('MOUSE_LEFT')
        )

    def _super_speed_combo(self):
        down = self.input.btn('DOWN') or self.input.btn('PAD_DOWN')
        b_btn = self.input.btn('X') or self.input.btn('PAD_B')
        return down and b_btn

    def _speed_combo(self):
        down = self.input.btn('DOWN') or self.input.btn('PAD_DOWN')
        a_btn = self.input.btn('Z') or self.input.btn('PAD_A')
        return down and a_btn

    def _space_held(self):
        return self.input.btn('SPACE')

    def _reset_pressed(self):
        return self.input.btnp('R') or self.input.btnp('PAD_SELECT') or self.input.btnp('PAD_START')

    def _font_toggle_pressed(self):
        return self.input.btnp('F') or self.input.btnp('PAD_X')

    def _get_typing_speed(self):
        if self._super_speed_combo():
            return 0, 3
        if self._speed_combo():
            return 0, 1
        if self._space_held():
            return FAST_INTERVAL, 1
        return CHAR_INTERVAL, 1

    def _play_talk_sound(self, interval, chars_per_tick):
        if not self.sound.enabled:
            return
        if interval == 0 and chars_per_tick >= 3:
            self.sound.play('talk_faster')
        elif interval == 0 and chars_per_tick == 1:
            self.sound.play('talk_fast')
        elif interval == FAST_INTERVAL:
            self.sound.play('talk_space')
        else:
            self.sound.play('talk')

    def update(self):
        self.frame_count += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            self.input.handle_event(event)

        self.input.update()

        if self.input.btnp('Q') or self.input.btnp('ESCAPE'):
            pygame.quit()
            sys.exit()

        if self._reset_pressed():
            self.reset()
            return

        if self._font_toggle_pressed():
            self.toggle_font_size()
            return

        if self._back_pressed():
            if self.page_index >= len(self.pages):
                if self.pages:
                    self.page_index = len(self.pages) - 1
                    self.revealed = len(self.current_page_text)
                    self.page_done = True
                    self.skip_cooldown = 5
                return
            if self.page_index > 0:
                self.page_index -= 1
                self.revealed = len(self.current_page_text)
                self.page_done = True
                self.skip_cooldown = 5
            return

        if self.skip_cooldown > 0:
            self.skip_cooldown -= 1
            return

        if self.page_index >= len(self.pages):
            return

        text = self.current_page_text

        if not self.page_done:
            if self._skip_pressed():
                self.revealed = len(text)
                self.page_done = True
                self.skip_cooldown = 8
                return

            interval, chars_per_tick = self._get_typing_speed()

            self.timer += 1
            if self.timer >= interval:
                self.timer = 0
                advanced = False

                for _ in range(chars_per_tick):
                    while self.revealed < len(text) and text[self.revealed] == "\n":
                        self.revealed += 1
                    if self.revealed < len(text):
                        self.revealed += 1
                        advanced = True

                if advanced:
                    self._play_talk_sound(interval, chars_per_tick)

                if self.revealed >= len(text):
                    self.revealed = len(text)
                    self.page_done = True
                    self.skip_cooldown = 5
        else:
            if self._next_pressed():
                self.page_index += 1
                self.revealed = 0
                self.timer = 0
                self.page_done = False

    def draw(self):
        self.screen.fill(PYXEL_PALETTE[0])

        pygame.draw.rect(
            self.screen, PYXEL_PALETTE[1],
            (BOX_X + 1, BOX_Y + 1, BOX_W - 2, BOX_H - 2)
        )
        pygame.draw.rect(
            self.screen, PYXEL_PALETTE[7],
            (BOX_X, BOX_Y, BOX_W, BOX_H), width=1
        )

        if self.page_index >= len(self.pages):
            self._draw_text(BOX_X + PADDING, BOX_Y + PADDING, "-- 読了 --", 7)
            self._draw_ui()
            pygame.display.flip()
            return

        text = self.current_page_text
        shown = text[:self.revealed]
        for i, line in enumerate(shown.split("\n")):
            y = BOX_Y + PADDING + i * self.line_height
            self._draw_text(BOX_X + PADDING, y, line, 7)

        if self.page_done and self.frame_count % 30 < 15:
            self._draw_text(BOX_X + BOX_W - 14, BOX_Y + BOX_H - 12, "▼", 7)

        self._draw_ui()
        pygame.display.flip()

    def _draw_text(self, x, y, text, color_index):
        color = PYXEL_PALETTE[color_index]
        surf = self.font.render(text, False, color)
        self.screen.blit(surf, (x, y))

    def _draw_ui(self):
        if not self.pages:
            return

        total = len(self.pages)
        current = min(self.page_index + 1, total)
        page_label = f"{current}/{total}"
        font_label = f"{int(self.current_size)}px"

        footer_y = BOX_Y + BOX_H - PADDING - self.current_size

        label_w = self.font.size(page_label)[0]
        x = BOX_X + BOX_W - PADDING - label_w
        self._draw_text(x, footer_y, page_label, 5)
        self._draw_text(BOX_X + PADDING, footer_y, font_label, 5)

    def run(self):
        while True:
            self.update()
            self.draw()
            self.clock.tick(60)
