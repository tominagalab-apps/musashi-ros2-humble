[← Back to basestation](../README.md)

# musashi_rqt_player_server

## 概要
**各プレイヤーロボットからのデータ受信を管理するrqtプラグインパッケージです。**

basestationの重要なセンサーハブとして機能し、5台のプレイヤーロボットからUDP通信で受信した状態データを処理・集約します。各ロボットの位置、向き、ボール認識、障害物検知などの情報を一元管理し、ROS2トピック`/player_states`で配信します。

### 主な機能
- **UDP通信**: 複数ロボットからの並行通信受け取り
- **データ解析**: カンマ区切り形式のロボット状態データをパース
- **リアルタイム集約**: 全ロボットの状態を`PlayerStates`メッセージに集約
- **マルチインターフェース対応**: 複数ネットワークインターフェース環境に対応
- **GUI制御**: Start/Stopボタンによる明示的な通信制御

## ノード

### rqt_player_server
各プレイヤーからのデータ受信を担当するrqtプラグインノードです。

#### 実行方法

**方法1: rqt GUI内でプラグインとして実行（推奨）**
```bash
rqt
```
rqt GUIが起動したら、Plugins → Hibikino-Musashi → PlayerServer を選択してロードします。

**方法2: スタンドアローン実行**
```bash
ros2 run musashi_rqt_player_server player_server
```

#### パブリッシュ
| topic | message type | description |
|-------|--------------|-------------|
| `/player_states` | `musashi_msgs.PlayerStates` | 全プレイヤーの状態 |

## BaseStation → Player間の通信仕様

BasestationはPlayerControllerを介して、各プレイヤーロボットへコマンドを送信します。

### コマンド送信フロー

```
RefereeBox (TCP)
    ↓ (RefereeCmd)
RefereeBoxClient
    ↓ (ROS2 /refcmd Topic)
PlayerController
    ↓ (UDP Command)
Player Robot
```

### BaseStation → Player（送信コマンド）

PlayerControllerが、RefereeBoxコマンド（`/refcmd` トピック）を受け取り、各プレイヤーロボット向けにUDP形式でテキストコマンドを送信します。

#### コマンド形式

**基本형식**: 単一行のテキスト形式（改行またはNULL終端）

```
<command>[,<arg1>[,<arg2>,...]]
```

#### 対応コマンド一覧

| コマンド | 引数 | 説明 | 例 |
|---------|------|------|-----|
| `START` | なし | 試合開始指令 | `START` |
| `STOP` | なし | 試合停止指令 | `STOP` |
| `DROP_BALL` | なし | ボールドロップ | `DROP_BALL` |
| `KICKOFF_POSITION` | `target_x`, `target_y` | キックオフ位置移動 | `KICKOFF_POSITION,3.0,0.0` |
| `FREEKICK_POSITION` | `target_x`, `target_y` | フリーキック位置移動 | `FREEKICK_POSITION,2.0,1.5` |
| `GOALKICK_POSITION` | `target_x`, `target_y` | ゴールキック位置移動 | `GOALKICK_POSITION,-8.0,0.0` |
| `THROWIN_POSITION` | `target_x`, `target_y` | スロー・イン位置移動 | `THROWIN_POSITION,0.0,5.2` |
| `CORNER_POSITION` | `target_x`, `target_y` | コーナーキック位置移動 | `CORNER_POSITION,7.5,4.5` |
| `PENALTY_POSITION` | `target_x`, `target_y` | ペナルティキック位置移動 | `PENALTY_POSITION,-8.0,0.0` |
| `PARK_POSITION` | `target_x`, `target_y` | 駐車位置移動 | `PARK_POSITION,-6.0,0.0` |
| `MOVETO` | `target_x`, `target_y`, `target_angle` | 目標位置への移動 | `MOVETO,2.0,3.0,1.57` |
| `KICK` | `power` | ボールキック (パワー指定) | `KICK,5.0` |
| `PASS` | `target_x`, `target_y` | ボール パス | `PASS,4.0,2.0` |
| `BALL_HOLD` | `0`/`1` | ボール保持フラグ (0=解放, 1=保持) | `BALL_HOLD,1` |

#### コマンド詳細

**座標系**: フィールド座標系（単位: メートル）
- X軸: 長軸方向（-8.0～8.0m、敵ゴール方向が正）
- Y軸: 短軸方向（-5.25～5.25m）
- 角度: ラジアン（-π～π）

**プレイヤー指定方法**:
- RefereeBoxコマンドは全プレイヤーに同一コマンドを送信
- GUI経由でロボット個別指令を送信する場合は、ロボットID（#1～#5）を指定

#### 送信仕様

| 項目 | 値 |
|------|-----|
| プロトコル | UDP/IPv4 |
| 送信先ポート | 各ロボット設定ポート（通常 9999 など） |
| データ形式 | テキスト（Shift-JIS, UTF-8, またはASCII） |
| 終端文字 | NULL（`\0`）または改行（`\n`） |
| 送信周期 | RefereeBoxコマンド受信時は即座、GUI指令時は UI操作時 |
| タイムアウト | 3秒以上応答がない場合は接続喪失と判定 |

#### マルチロボット対応

PlayerControllerは全5台のロボットへ同一コマンドを送信：

```python
# 疑似コード例
for player_id in range(1, 6):
    send_command_to_robot(player_id, command_string)
```

#### コマンド送信の例

```
RefereeBox から "KICKOFF" コマンド受信
    ↓
PlayerController で以下に変換：
    KICKOFF_POSITION,3.0,0.0
    ↓
各プレイヤーロボット（#1～#5）へ UDP送信
    ↓
プレイヤーロボットが受け取り、指定位置へ移動開始
```

### 将来の改善予定

- **バイナリコマンド形式への移行**: テキスト形式からバイナリ形式へ移行予定
- **タイムスタンプ付与**: コマンドに時刻情報を付与してタイミング制御の精度向上
- **確認応答（ACK）機構**: ロボット側からの受信確認メッセージ実装予定

## Player → basestation間の通信仕様

各プレイヤーロボットからはUDPで**カンマ（`,`）区切りのテキスト形式**で状態データが送信されます。

#### フォーマット詳細
```
color,id,action,state,ball_distance,ball_angle,goal_distance,goal_angle,mygoal_distance,mygoal_angle,pos_x,pos_y,pos_angle,role,haveBall,target_x,target_y,target_angle,obs_distance,obs_angle
```

#### データ仕様表

| # | フィールド | 説明 | 単位/値 |
|---|-----------|------|--------|
| 1 | `color` | チームカラー | CYAN: 0, MAGENTA: 1 |
| 2 | `id` | ロボットID | 1～5 |
| 3 | `action` | ロボットのアクション | Action定数値 |
| 4 | `state` | ロボットの状態 | State定数値 |
| 5 | `ball_distance` | ボールとの直線距離 | [m] |
| 6 | `ball_angle` | ボールの角度 | [rad] |
| 7 | `goal_distance` | ゴールとの直線距離 | [m] |
| 8 | `goal_angle` | ゴールの角度 | [rad] |
| 9 | `mygoal_distance` | 自身のゴールとの直線距離 | [m] |
| 10 | `mygoal_angle` | 自身のゴールの角度 | [rad] |
| 11 | `pos_x` | 自己位置X座標 | [m] |
| 12 | `pos_y` | 自己位置Y座標 | [m] |
| 13 | `pos_angle` | ロボット姿勢 | [rad] |
| 14 | `role` | ロボットのロール | Role定数値 |
| 15 | `haveBall` | ボール保持の有無 | 0: 未保持, 1: 保持 |
| 16 | `target_x` | 目標X座標 | [m] |
| 17 | `target_y` | 目標Y座標 | [m] |
| 18 | `target_angle` | 目標姿勢 | [rad] |
| 19 | `obs_distance` | 障害物までの直線距離 | [m] |
| 20 | `obs_angle` | 障害物の角度 | [rad] |

#### 受信処理
- **パース方法**: カンマ（`,`）で分割して処理
- **データ型変換**: 受信後に文字列を整数値/浮動小数点値に変換
- **可変長対応**: フィールドの文字数は固定ではないため、分割後の長さを確認してから変換

### 今後の改善予定
現在のテキスト形式からバイナリデータへの移行を計画しており、通信速度の大幅な向上が期待できます。

## UI機能

rqtプラグインとしてロードすると、以下のGUI機能が利用可能です：

### サーバ制御
- **Start/Stopボタン**: UDP通信サーバの明示的な開始・停止
- **自動起動なし**: 起動時には通信を開始せず、GUIからの指示で開始

### ネットワーク設定
- **Bind IP（Own IP）入力欄**: バインドするIPアドレスを指定
- **Port入力欄**: バインドするポート番号を指定
- **マルチインターフェース対応**: 複数ネットワークインターフェース環境に対応

### 状態表示
- **受信状態表示**: 各プレイヤーからのデータ受信状態
- **接続ログ**: 接続・切断イベント、受信データのログ表示
- **受信統計**: パケット数、フレームレート、遅延情報

## ディレクトリ構成

```
musashi_rqt_player_server/
├── README.md
├── package.xml
├── plugin.xml
├── resource/
│   └── musashi_rqt_player_server
├── scripts/
│   └── player_server
├── setup.cfg
├── setup.py
├── src/
│   └── musashi_rqt_player_server/
│       ├── __init__.py
│       ├── player_server.py
│       └── rqt_player_server.py
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

## 最近の更新
- **PlayerServer**: GUI上で明示的な **Start / Stop** ボタンを追加
- **PlayerServer**: **Bind IP** と **Port** 入力欄で複数インターフェース対応が可能に

## 共通定数の一元管理

チームカラーや役割（MAGENTA, CYAN, ALPHA, BETA, GAMMA, DELTA, GOALIE など）の定数は、
`musashi_basestation/common/constants.py` にて一元管理されています。
本パッケージでも `from musashi_basestation.common.constants import ...` で参照しています。

- 2026年3月：定数の共通化・一元管理を実施
