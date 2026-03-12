[← Back to basestation](../README.md)

# musashi_rqt_player_controller

## 概要
**各プレイヤーロボットへのコマンド送信を管理するrqtプラグインパッケージです。**

basestationの重要なアクチュエータハブとして機能し、RefereeBoxから受け取ったゲームコマンドと内部の戦術判断をプレイヤー固有のフォーマットに変換し、UDP通信で5台のプレイヤーロボットに送信します。RefereeBoxコマンド、キックオフ位置指示、ロボット個別指令などを統合管理し、試合を一元的に制御します。

### 主な機能
- **コマンド変換**: RefereeBoxコマンドをプレイヤーフォーマットに変換
- **UDP送信**: 複数ロボットへの並行送信
- **コマンド送信**:
  - 全ロボット向けコマンド
  - ロボット個別指令（位置移動、キック指示など）
  - 戦術コマンド
- **リアルタイム制御**: GUIからの直接指令も対応
- **通信ログ**: 送信コマンドの履歴管理

## ノード

### rqt_player_controller
各プレイヤーへのコマンド送信を担当するrqtプラグインノードです。

#### 実行方法

**方法1: rqt GUI内でプラグインとして実行（推奨）**
```bash
rqt
```
rqt GUIが起動したら、Plugins → Hibikino-Musashi → PlayerController を選択してロードします。

**方法2: スタンドアローン実行**
```bash
ros2 run musashi_rqt_player_controller player_controller
```

#### サブスクライブ
| topic | message type | description |
|-------|--------------|-------------|
| `/refcmd` | `musashi_msgs.RefereeCmd` | RefereeBoxから受信したコマンド |

## basestation → Player間の通信仕様

### コマンド送信フロー

```
RefereeBox Command
    ↓
RefereeBoxClient (受信・解析)
    ↓
PlayerController (変換・制御)
    ↓
Player Robot (UDP送信)
```

### basestation → Player（送信コマンド詳細）

RefereeBoxから送られてきたコマンドに基づいて、各プレイヤーへコマンドを送信します。この時、Hibikino-Musashi内で取り決められたコマンドフォーマットに変換して送る必要があります。

#### コマンド形式

**基本形式**: 単一行のテキスト形式（改行またはNULL終端）

```
<command>[,<arg1>[,<arg2>,...]]
```

#### 対応コマンド一覧

| RefereeBox | Player向け | 引数 | 説明 | 例 |
|-----------|----------|------|------|-----|
| `START` | `START` | なし | 試合開始 | `START` |
| `STOP` | `STOP` | なし | 試合停止 | `STOP` |
| `DROP_BALL` | `DROP_BALL` | なし | ボールドロップ | `DROP_BALL` |
| `KICKOFF` | `KICKOFF_POSITION` | `target_x`, `target_y` | キックオフ位置移動 | `KICKOFF_POSITION,3.0,0.0` |
| `FREEKICK` | `FREEKICK_POSITION` | `target_x`, `target_y` | フリーキック位置移動 | `FREEKICK_POSITION,2.0,1.5` |
| `GOALKICK` | `GOALKICK_POSITION` | `target_x`, `target_y` | ゴールキック位置移動 | `GOALKICK_POSITION,-8.0,0.0` |
| `THROWIN` | `THROWIN_POSITION` | `target_x`, `target_y` | スロー・イン位置移動 | `THROWIN_POSITION,0.0,5.2` |
| `CORNER` | `CORNER_POSITION` | `target_x`, `target_y` | コーナーキック位置移動 | `CORNER_POSITION,7.5,4.5` |
| `PENALTY` | `PENALTY_POSITION` | `target_x`, `target_y` | ペナルティキック位置移動 | `PENALTY_POSITION,-8.0,0.0` |
| `PARK` | `PARK_POSITION` | `target_x`, `target_y` | 駐車位置移動 | `PARK_POSITION,-6.0,0.0` |
| (GUI) | `MOVETO` | `target_x`, `target_y`, `target_angle` | 目標位置への移動 | `MOVETO,2.0,3.0,1.57` |
| (GUI) | `KICK` | `power` | ボールキック | `KICK,5.0` |
| (GUI) | `PASS` | `target_x`, `target_y` | ボール パス | `PASS,4.0,2.0` |
| (GUI) | `BALL_HOLD` | `0`/`1` | ボール保持フラグ | `BALL_HOLD,1` |

#### 座標系・単位

| 項目 | 範囲 | 単位 | 説明 |
|------|------|------|------|
| **X座標** | -8.0～8.0 | m | フィールド長軸。敵ゴール方向が正 |
| **Y座標** | -5.25～5.25 | m | フィールド短軸。左側が負 |
| **角度** | -π～π | rad | ロボット姿勢。右向きが 0 |
| **パワー** | 0～10 | - | キック力（0=最小、10=最大） |

#### 送信仕様

| 項目 | 値 | 説明 |
|------|-----|------|
| **プロトコル** | UDP/IPv4 | 無接続型、低遅延 |
| **送信先ポート** | 9999 (標準) | ロボット側リッスンポート |
| **データ形式** | UTF-8 テキスト | 改行またはNULL終端 |
| **送信タイミング** | 即座 | RefereeBox コマンド受信直後 |
| **同期方式** | ベストエフォート | 再送なし（ロボット側で検証） |
| **送信対象** | 全ロボット | #1～#5 に同一コマンド送信 |

#### ロボット個別指令（GUI経由）

PlayerController の GUI からロボット固有の指令を送信する場合：

```python
# 疑似コード例
def send_command_to_player(player_id: int, command: str):
    """
    特定ロボットへコマンド送信
    Args:
        player_id (int): 1～5
        command (str): "MOVETO,x,y,angle" など
    """
    robot_ip = self.get_player_ip(player_id)
    robot_port = self.get_player_port(player_id)
    sock.sendto(command.encode('utf-8'), (robot_ip, robot_port))
```

#### エラーハンドリング

プレイヤーロボット側での処理：

| 状況 | ロボット動作 |
|------|-----------|
| **コマンド受信成功** | 指定動作を実行、状態パケット送信 |
| **パース エラー** | エラーログ出力、以前の状態保持 |
| **範囲外パラメータ** | クリップまたは拒否、ログ出力 |
| **連続して受信なし** | 3秒後にコマンド待機状態に遷移 |

## UI機能

rqtプラグインとしてロードすると、以下のGUI機能が利用可能です：

### コマンド送信
- **全ロボット向けコマンド**: 複数ロボットへの統一コマンド送信（RefereeBox経由）
- **ロボット個別指令**: 特定ロボット（#1～#5）への個別指令（GUI経由）
  - 直接移動: `MOVETO <x> <y> <angle>`
  - キック: `KICK <power>`
  - パス: `PASS <target_x> <target_y>`
  - ボール保持: `BALL_HOLD <0|1>`
- **位置移動指示**: キックオフ位置、ゴールキック位置など戦術位置の指定

### 表示・ログ
- **コマンド送信ログ**: 送信したコマンドの履歴表示（タイムスタンプ付き）
- **ロボット状態表示**: 各ロボットの現在状態（オンライン/オフライン）
- **通信統計**: 送受信パケット数、遅延情報

## ディレクトリ構成

```
musashi_rqt_player_controller/
├── README.md
├── package.xml
├── plugin.xml
├── resource/
│   └── musashi_rqt_player_controller
├── scripts/
│   └── player_controller
├── setup.cfg
├── setup.py
├── src/
│   └── musashi_rqt_player_controller/
│       ├── __init__.py
│       └── rqt_player_controller.py
└── test/
    ├── test_copyright.py
    ├── test_flake8.py
    └── test_pep257.py
```

## 依存関係

- `rclpy`: ROS2 Pythonクライアント
- `python_qt_binding`: Qtバインディング
- `rqt_gui`: rqt GUIフレームワーク
- `musashi_msgs`: カスタムメッセージ定義
