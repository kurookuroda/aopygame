
---

## 配布済みファイル（Pygame ローカル用）

以下の6ファイルがすでに配布済みです。

| ファイル | 役割 |
|----------|------|
| `main.py` | エントリーポイント |
| `reader.py` | App クラス（メインアプリケーション） |
| `input_manager.py` | Pyxel の btn/btnp 互換入力管理 |
| `sound_manager.py` | WAV/OGG 効果音管理 |
| `palette.py` | Pyxel 16色パレット定義 |
| `requirements.txt` | `pygame>=2.5.0` |

---

## ディレクトリ構成

```
aozora-reader/
├── main.py                    # エントリーポイント
├── reader.py                  # App クラス
├── input_manager.py           # 入力管理
├── sound_manager.py           # 効果音管理
├── palette.py                 # 色定義
├── requirements.txt           # Python 依存
├── PixelMplus10-Regular.ttf   # フォント（任意）
├── PixelMplus12-Regular.ttf   # フォント（任意）
├── aozora_416.txt             # 表示テキスト
├── beep_talk.wav              # 効果音（任意）
├── beep_space.wav             # 効果音（任意）
├── beep_fast.wav              # 効果音（任意）
└── beep_faster.wav            # 効果音（任意）
```

---

## 実行までの手順

### Step 1: 依存インストール

```bash
pip install -r requirements.txt
```

Linux の場合、pygame のビルドに SDL2 開発ライブラリが必要です：

```bash
# Ubuntu / Debian
sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev

# Fedora
sudo dnf install SDL2-devel SDL2_image-devel SDL2_mixer-devel SDL2_ttf-devel

# macOS
brew install sdl2 sdl2_image sdl2_mixer sdl2_ttf
```

### Step 2: アセットを配置

- `PixelMplus10-Regular.ttf` / `PixelMplus12-Regular.ttf`（任意、ない場合はシステムフォントにフォールバック）
- `aozora_416.txt`（任意、ない場合は「ファイルが見つかりません」と表示）
- `beep_*.wav`（任意、ない場合は無音で動作）

### Step 3: 実行

```bash
python3 main.py
```

---

## GitHub リポジトリ作成

### 方法A: コマンドライン

```bash
cd aozora-reader
git init
git add .
git commit -m "Initial commit: Aozora Reader Pygame"
gh repo create aozora-reader --public --source=. --push
```

### 方法B: 手動（ウェブ）

1. https://github.com/new で `aozora-reader` を作成
2. ファイルをドラッグ＆ドロップでアップロード

---

## 操作方法

| キー | 動作 |
|------|------|
| `RETURN` / `↓` / マウス左クリック | 次へ進む |
| `↑` | 前のページに戻る |
| `SPACE`（長押し） | 高速タイピング |
| `↓ + Z` | さらに高速 |
| `↓ + X` | 超高速 |
| `F` | フォントサイズ切り替え |
| `R` | 最初から再読み込み |
| `Q` / `ESC` | 終了 |

---
