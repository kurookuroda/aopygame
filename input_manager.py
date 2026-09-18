import pygame

# キー対応表（Pyxel の定数名 → Pygame のキーコード）
KEY_MAP = {
    'Z':        pygame.K_z,
    'X':        pygame.K_x,
    'RETURN':   pygame.K_RETURN,
    'SPACE':    pygame.K_SPACE,
    'UP':       pygame.K_UP,
    'DOWN':     pygame.K_DOWN,
    'R':        pygame.K_r,
    'F':        pygame.K_f,
    'Q':        pygame.K_q,
    'ESCAPE':   pygame.K_ESCAPE,
}


class InputManager:
    """Pyxel の btn / btnp に相当する入力管理クラス。

    btn : キーが現在押下中かどうか
    btnp: キー前フレームでは押されておらず、今フレームで初めて押されたか

    マウスの左クリック（MOUSE_LEFT）は MOUSEBUTTONDOWN イベントを捕捉して
    btnp 相当の動作を実現する。
    """

    def __init__(self):
        self.prev_keys = {}
        self.curr_keys = {}
        self.mouse_click = False  # MOUSEBUTTONDOWN 検出用
        self.joysticks = []
        self._init_joysticks()

    def _init_joysticks(self):
        for i in range(pygame.joystick.get_count()):
            try:
                js = pygame.joystick.Joystick(i)
                js.init()
                self.joysticks.append(js)
            except pygame.error:
                pass

    def handle_event(self, event):
        """pygame.event.get() で取得したイベントを渡す。"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.mouse_click = True

    def update(self):
        self.prev_keys = self.curr_keys.copy()
        keys = pygame.key.get_pressed()
        self.curr_keys = {}

        # キーボード
        for name, keycode in KEY_MAP.items():
            self.curr_keys[name] = keys[keycode]

        # マウス（押下中状態）
        mouse = pygame.mouse.get_pressed()
        self.curr_keys['MOUSE_LEFT'] = mouse[0]

        # ゲームパッド
        self._update_gamepad()

    def _update_gamepad(self):
        if not self.joysticks:
            for name in ['PAD_A', 'PAD_B', 'PAD_X', 'PAD_SELECT',
                         'PAD_START', 'PAD_UP', 'PAD_DOWN']:
                self.curr_keys[name] = False
            return

        js = self.joysticks[0]
        self.curr_keys['PAD_A'] = js.get_button(0)
        self.curr_keys['PAD_B'] = js.get_button(1)
        self.curr_keys['PAD_X'] = js.get_button(2)
        self.curr_keys['PAD_SELECT'] = js.get_button(6) if js.get_numbuttons() > 6 else False
        self.curr_keys['PAD_START'] = js.get_button(7) if js.get_numbuttons() > 7 else False

        # Hat (D-Pad)
        if js.get_numhats() > 0:
            hat = js.get_hat(0)
            self.curr_keys['PAD_UP'] = hat[1] == 1
            self.curr_keys['PAD_DOWN'] = hat[1] == -1
        else:
            self.curr_keys['PAD_UP'] = False
            self.curr_keys['PAD_DOWN'] = False

    def btn(self, key):
        """Pyxel の btn と同等。"""
        return self.curr_keys.get(key, False)

    def btnp(self, key):
        """Pyxel の btnp と同等。"""
        if key == 'MOUSE_LEFT':
            result = self.mouse_click
            self.mouse_click = False
            return result
        return self.curr_keys.get(key, False) and not self.prev_keys.get(key, False)
