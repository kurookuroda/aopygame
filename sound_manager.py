import os
import pygame


class SoundManager:
    """タイピング音を wav / ogg / mp3 ファイルから読み込んで再生。

    ファイルが存在しない場合は無音で動作する。
    pygame.mixer が初期化できない場合も無音で動作する。
    """

    def __init__(self, config):
        """
        Args:
            config: {名前: ファイルパス} の辞書。
                    例: {'talk': 'beep_talk.wav', ...}
        """
        self.enabled = False
        self.sounds = {}
        self.config = config
        self._init()

    def _init(self):
        # mixer の初期化確認
        if pygame.mixer.get_init() is None:
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            except Exception:
                return  # 無音で動作

        self._load_sounds()
        self.enabled = bool(self.sounds)

    def _load_sounds(self):
        """設定されたファイルパスからウンドを読み込む。"""
        for name, path in self.config.items():
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                except pygame.error:
                    pass  # 読み込み失敗は無視

    def play(self, name):
        if self.enabled and name in self.sounds:
            self.sounds[name].play()
