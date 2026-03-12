[Home](../README.md)  
# basestation（旧コーチボックス）

## 概要
**basestationは、RoboCupサッカーロボットの試合を管制するコーチボックス実装です。**

RoboCup MSL（Middle Size League）の試合管制システムとして機能し、RefereeBoxからのゲームコマンドを受信・解析し、5台のプレイヤーロボットへの指令配信、プレイヤーロボットの状態監視、および試合状況の可視化を統合管理します。

### 主な機能
- **RefereeBox通信**: TCP/IPによるゲームコマンド受信
- **ロボット制御**: UDP通信による複数ロボットへの並行制御
- **状態監視**: ロボット位置・姿勢・ボール保持状態のリアルタイム監視
- **3D可視化**: RViz2による試合状況のリアルタイム表示
- **統合管理**: 単一ベースステーションですべての通信・制御を一元化

## システムアーキテクチャ

```
RefereeBox (TCP)
    ↓ (Commands)
    ↓
RefereeBoxClient ─────┐
                      │
                      → ROS2 Topic (/refcmd)
                      │
PlayerController  ←───┘
    ↓ (UDP Commands)
    ↓
[Player1][Player2][Player3][Player4][Player5]
    ↓ (UDP States)
    ↓
PlayerServer
    ↓ (ROS2 Topic /player_states)
    ↓
RViz (3D Visualization)
```

## パッケージ一覧

basestationは以下の4つの専門化パッケージで構成されています：

| パッケージ | 説明 | 役割 | 通信 |
|-----------|------|------|------|
| 📡 [musashi_rqt_refereebox_client](./musashi_rqt_refereebox_client/README.md) | RefereeBox通信管理 | RefereeBoxからのコマンド受信・解析 | TCP/IPv4 |
| 📤 [musashi_rqt_player_controller](./musashi_rqt_player_controller/README.md) | プレイヤーコマンド送信 | ロボットへのコマンド変換・送信 | UDP/IPv4 |
| 📥 [musashi_rqt_player_server](./musashi_rqt_player_server/README.md) | プレイヤーデータ受信 | ロボット状態データの受信・監視 | UDP/IPv4 |
| 🎨 [musashi_rviz](./musashi_rviz/README.md) | 3D可視化 | フィールド・ロボット表示・監視 | ROS2 TF |

## 動作構成

basestationは以下の**2つの独立した画面**で構成されており、両方を起動することで試合の管制と可視化の完全な機能が実現されます。

**⚠️ 重要：両画面を同時に起動する必要があります。どちらか一方だけでは、RefereeBox → basestation → Player への通信パイプラインが構築されず、試合が開始できません。**

| Display | パッケージ | 役割 | 説明 |
|---------|-----------|------|------|
| **RViz** | musashi_rviz | 可視化 | 3Dフィールドビュー。フィールドとプレイヤーの状態をリアルタイムに可視化 |
| **rqt GUI** | rqt plugins | 管制 | コントローラー画面。RefereeBox通信、プレイヤー監視、コマンド送信を管理 |

## 実行方法

### ステップ1: RViz画面起動（フィールド可視化）
```bash
ros2 launch musashi_rviz bringup_launch.py
```
フィールドと5台のプレイヤーロボットが表示されるRViz画面が起動します。  
詳細は [musashi_rviz/README.md](./musashi_rviz/README.md) を参照してください。

### ステップ2: rqt GUI画面起動（コマンド・監視）
```bash
rqt
```
空のrqt GUI画面が起動します。

**プラグインのロード手順:**
1. **Plugins** メニューをクリック
2. **Hibikino-Musashi** カテゴリを展開
3. 以下の3つのプラグインを順番にロード：
   - **RefereeBoxClient** - RefereeBox通信管理
   - **PlayerServer** - プレイヤー状態監視
   - **PlayerController** - プレイヤーコマンド送信

**重要な初期化手順:**
1. RefereeBoxClient で接続設定を確認
2. PlayerServer でBind IP・Portを設定後、**Start** ボタンをクリック
3. チーム情報、プレイヤーIPアドレスを全て確認
4. その後、RefereeBox から "START" コマンドを送信

## ディレクトリ構成（詳細版）

```
basestation/
├── README.md (このファイル)
│
├── musashi_basestation/
│   ├── README.md
│   ├── package.xml (launch パッケージ本体)
│   ├── setup.py
│   ├── setup.cfg
│   ├── config/ (rqt 設定ファイル)
│   │   ├── rqt_basestation_plugins.rqt
│   │   └── rqt_player_control.rqt
│   ├── launch/ (全体 launch ファイル)
│   │   └── rqt_basestation.launch.py
│   ├── resource/
│   │   └── musashi_basestation
│   ├── src/
│   │   └── musashi_basestation/
│   └── test/
│
├── musashi_rqt_refereebox_client/
│   ├── README.md
│   ├── package.xml
│   ├── plugin.xml (rqt プラグイン定義)
│   ├── setup.py
│   ├── setup.cfg
│   ├── scripts/
│   │   └── refereebox_client (アントリポイント)
│   ├── resource/
│   │   ├── musashi_rqt_refereebox_client
│   │   └── refereebox_client.ui (Qt UI)
│   ├── src/
│   │   └── musashi_rqt_refereebox_client/
│   │       ├── __init__.py
│   │       ├── rqt_refereebox_client.py (rqt プラグイン本体)
│   │       ├── refbox_client.py (TCP 通信実装)
│   │       └── json_log.py (コマンドログ)
│   └── test/ (著作権・PEP8 チェック)
│
├── musashi_rqt_player_controller/
│   ├── README.md
│   ├── package.xml
│   ├── plugin.xml (rqt プラグイン定義)
│   ├── setup.py
│   ├── setup.cfg
│   ├── scripts/
│   │   └── player_controller (エントリポイント)
│   ├── resource/
│   │   ├── musashi_rqt_player_controller
│   │   └── player_controller.ui (Qt UI)
│   ├── src/
│   │   └── musashi_rqt_player_controller/
│   │       ├── __init__.py
│   │       └── rqt_player_controller.py (rqt プラグイン本体)
│   └── test/
│
├── musashi_rqt_player_server/
│   ├── README.md
│   ├── package.xml
│   ├── plugin.xml (rqt プラグイン定義)
│   ├── setup.py
│   ├── setup.cfg
│   ├── scripts/
│   │   └── player_server (エントリポイント)
│   ├── resource/
│   │   ├── musashi_rqt_player_server
│   │   └── player_server.ui (Qt UI)
│   ├── src/
│   │   └── musashi_rqt_player_server/
│   │       ├── __init__.py
│   │       ├── rqt_player_server.py (rqt プラグイン本体)
│   │       └── player_server.py (UDP 受信実装)
│   └── test/
│
└── musashi_rviz/
    ├── README.md
    ├── package.xml
    ├── setup.py
    ├── setup.cfg
    ├── launch/ (起動ファイル)
    │   ├── bringup_launch.py (メイン起動)
    │   ├── team_spawn_launch.py (マルチロボット)
    │   └── player_spawn_launch.py (個別ロボット)
    ├── config/ (フィールド設定)
    │   ├── field_parameters.yaml (本番環境)
    │   ├── field_parameters_demo.yaml (デモ環境)
    │   └── rviz/ (RViz2 設定ファイル)
    │       └── config.rviz
    ├── meshes/ (オプション: ロボット・フィールドメッシュ)
    ├── musashi_rviz/ (Python パッケージ)
    │   ├── __init__.py
    │   ├── node_field_publisher.py (フィールド TF 配信)
    │   └── node_sample01_tf_publisher.py (ロボット位置 TF 配信)
    ├── resource/
    │   └── musashi_rviz
    └── test/
```

### 重要ファイルの説明

| ファイル | パッケージ | 説明 |
|---------|----------|------|
| `rqt_player_server.py` | musashi_rqt_player_server | rqt プラグイン・UDP 受信ロジック分離予定 |
| `player_server.py` | musashi_rqt_player_server | CSV フォーマットパース実装 |
| `refbox_client.py` | musashi_rqt_refereebox_client | TCP ソケット・JSON パース実装 |
| `bringup_launch.py` | musashi_rviz | 全体の初期化・RViz2 起動 |
| `field_parameters.yaml` | musashi_rviz | MSL フィールド寸法定義 |

## パッケージの詳細仕様

### 1. musashi_rqt_refereebox_client

**役割**: RoboCup MSL RefereeBoxとのTCP通信を管理する

#### 通信仕様
- **通信方式**: TCP/IPv4（ブロッキング型）
- **通信相手**: RoboCup MSL RefereeBox サーバー
- **コマンド形式**: JSON + NULL終端（`\0`）

#### 実装細部
- NULL終端文字對応：複数メッセージの連結や部分受信に堅牢対応
- サポートされるコマンド：
  - **全体コマンド**: START, STOP, DROP_BALL, HALF_TIME, END_GAME, GAME_OVER, PARK, RESET
  - **チーム別コマンド**: WELCOME, KICKOFF, FREEKICK, GOALKICK, THROWIN, CORNER, PENALTY 等

#### パッケージ構成
- `rqt_refereebox_client.py` - rqtプラグイン（GUI）
- `refbox_client.py` - TCP通信実装
- `json_log.py` - 受信ログ管理
- `refereebox_client.ui` - Qt UIファイル

#### 出力
- ROS2トピック `/refcmd` (`musashi_msgs/RefereeCmd`)

### 2. musashi_rqt_player_controller

**役割**: RefereeBoxコマンドをプレイヤー向けフォーマットに変換し、UDP送信する

#### 基本動作
- `/refcmd` トピックをサブスクライブしてRefereeBoxコマンドを受け取る
- コマンドを各ロボット固有のフォーマットに変換
- UDP/IPv4通信で5台のプレイヤーロボットに送信

#### 対応するコマンド変換例
| RefereeBox | Player向け | 説明 |
|-----------|----------|------|
| START | START | 試合開始 |
| STOP | STOP | 試合停止 |
| KICKOFF | KICKOFF_POSITION | キックオフ位置移動 |
| FREEKICK | FREEKICK_POSITION | フリーキック位置 |
| GOALKICK | GOALKICK_POSITION | ゴールキック位置 |
| THROWIN | THROWIN_POSITION | スロー・イン位置 |
| CORNER | CORNER_POSITION | コーナーキック位置 |
| PENALTY | PENALTY_POSITION | ペナルティキック位置 |
| DROP_BALL | DROP_BALL | ボールドロップ |

#### サポート機能
- **ロボット別制御**: 5台のロボット（#1～#5）への個別指令対応
- **ロール定義**: ALPHA(1), BETA(2), GAMMA(3), DELTA(4), GOALIE(5)
- **GUIからの直接指令**: rqtプラグイン経由での手動コマンド送信
- **通信ログ**: 送受信ユレッジ履歴の表示

#### パッケージ構成
- `rqt_player_controller.py` - rqtプラグイン（GUI）
- `player_controller.ui` - Qt UIファイル

#### 通信プロトコル
- **プロトコル**: UDP/IPv4
- **受信ポート**: 各ロボット固有（設定ファイルで指定）
- **通信周期**: ~100ms

### 3. musashi_rqt_player_server

**役割**: プレイヤーロボットからの状態データ受信・集約し、ROS2トピックで配信

#### 基本動作
- UDP サーバーを起動し、5台のプレイヤーから状態データを受信
- カンマ区切り形式（CSV）のテキストデータをパース
- ROS2メッセージ形式に変換し、`/player_states` トピックに配信

#### 受信データフォーマット（CSV形式）

**フォーマット**:
```
color,id,action,state,ball_distance,ball_angle,goal_distance,goal_angle,
mygoal_distance,mygoal_angle,pos_x,pos_y,pos_angle,role,haveBall,
target_x,target_y,target_angle,obs_distance,obs_angle
```

**データ仕様**(20フィールド)：

| # | フィールド | 型 | 説明 | 単位 |
|---|----------|----|----|------|
| 1 | color | int | チームカラー (CYAN=1, MAGENTA=0) | - |
| 2 | id | int | ロボットID | 1～5 |
| 3 | action | int | ロボット動作状態 | 定数値 |
| 4 | state | int | ロボット内部状態 | 定数値 |
| 5 | ball_distance | float | ボール直線距離 | m |
| 6 | ball_angle | float | ボール方角 | rad |
| 7 | goal_distance | float | 敵ゴール直線距離 | m |
| 8 | goal_angle | float | 敵ゴール方角 | rad |
| 9 | mygoal_distance | float | 自ゴール直線距離 | m |
| 10 | mygoal_angle | float | 自ゴール方角 | rad |
| 11 | pos_x | float | X座標（フィールド座標系） | m |
| 12 | pos_y | float | Y座標（フィールド座標系） | m |
| 13 | pos_angle | float | ロボット姿勢角度 | rad |
| 14 | role | int | ロボールロール (ALPHA=1, BETA=2...) | - |
| 15 | haveBall | int | ボール保持フラグ | 0/1 |
| 16 | target_x | float | 目標X座標 | m |
| 17 | target_y | float | 目標Y座標 | m |
| 18 | target_angle | float | 目標姿勢角度 | rad |
| 19 | obs_distance | float | 障害物直線距離 | m |
| 20 | obs_angle | float | 障害物方角 | rad |

#### パッケージ構成
- `rqt_player_server.py` - rqtプラグイン（GUI）
- `player_server.py` - UDP受信実装・パース処理
- `player_server.ui` - Qt UIファイル

#### GUI機能
- **Start/Stopボタン**: UDP受信サーバーの制御（自動起動しない）
- **Bind IP設定**: バインドするネットワークインターフェースの指定
- **Port設定**: リッスンするUDPポート番号の指定
- **受信ログ**: 各ロボットからの受信状態・時刻表示

#### 出力
- ROS2トピック `/player_states` (`musashi_msgs/PlayerStates`)

#### 通信仕様
- **プロトコル**: UDP サーバー（リッスン側）
- **デフォルトPort**: 設定により変更可能
- **通信周期**: 各ロボットから ~100ms 周期で送信

### 4. musashi_rviz

**役割**: フィールドとロボットの3D可視化

#### 実装内容
- **フィールド可視化**: MSL標準フィールド寸法をTFフレームで配信
- **ロボット可視化**: `/player_states` トピックから各ロボットのTFフレームを生成

#### Launch ファイル
| ファイル | 説明 | 用途 |
|---------|------|------|
| `bringup_launch.py` | トップレベルlaunch | メイン起動ファイル（推奨） |
| `team_spawn_launch.py` | マルチロボットlaunch | 複数ロボットのTF生成 |
| `player_spawn_launch.py` | 個別ロボットlaunch | 単一ロボットのTF生成 |

#### ノード
- `node_field_publisher.py` - フィールド情報TF配信
- `node_sample01_tf_publisher.py` - ロボット位置TF配信（サンプル実装）

#### パラメータ
- `player_num` - プレイヤー数（デフォルト: 5）
- `config_type` - フィールド設定タイプ（standard/demo、デフォルト: standard）

#### TFフレーム階層
```
map
└── field (フィールド基準フレーム)
    ├── player1
    │   └── base_link (ロボット本体)
    ├── player2
    │   └── base_link
    ├── player3
    │   └── base_link
    ├── player4
    │   └── base_link
    └── player5
        └── base_link
```

## 最近の実装状況

### 通信層（RefereeBoxClient）
- ✅ TCP接続の堅牢化完了
- ✅ NULL終端文字対応で部分受信・複数メッセージ連結に対応
- ✅ JSON形式コマンド解析完了
- ✅ 全コマンド・チーム別コマンド分離対応

### 制御層（PlayerController）
- ✅ RefereeBoxコマンドからPlayer形式への変換処理実装
- ✅ ロボット個別制御コマンドサポート
- ⏳ **未実装**: 戦術コマンド（カスタムコマンド）対応

### センサー層（PlayerServer）
- ✅ UDP受信バッファの堅牢化
- ✅ CSV形式データのパース実装
- ✅ Start/Stopボタンでの受信制御
- ✅ マルチインターフェース対応（Bind IP設定）
- ⏳ **未実装**: バイナリ通信形式への移行予定

### 可視化層（musashi_rviz）
- ✅ `player_num` パラメータでロボット数を動的設定
- ✅ TFフレーム階層の標準化
- ⏳ **ロードマップ**: プレイヤー画像・メッシュの追加

## 運用時のベストプラクティス

### 推奨起動順序
1. **RViz** を先に起動 (`ros2 launch musashi_rviz bringup_launch.py`)
2. その後 **rqt** を起動 (`rqt`)
3. rqtプラグインを以下の順番でロード：
   - **PlayerServer** ← 最初にロード
   - **RefereeBoxClient** ← その次
   - **PlayerController** ← 最後

**理由**: PlayerServerからのデータを他のコンポーネントが参照するため

### 試合前のチェックリスト

#### ネットワーク環境確認
- [ ] RefereeBox PC の IP・ポート番号を把握
- [ ] basestation PC の Network Interface を確認 (`ip addr show`)
- [ ] 全プレイヤーロボット（5台）の IP アドレスリスト確認
- [ ] ネットワーク接続性を事前確認 (`ping` で各装置を確認)

#### GUI起動後の初期化手順
```
1. PlayerServer プラグインがロードされたら：
   - Bind IP を設定（バインド対象の NIC を指定）
   - Port を設定（デフォルト: 9000 など、設定に応じて）
   - [Start] ボタンクリック → 受信開始
   - "Listening on 0.0.0.0:9000" などのメッセージを確認

2. RefereeBoxClient プラグインがロードされたら：
   - RefereeBox IP アドレス、ポート番号を設定
   - [Connect] ボタンクリック → 接続確立
   - "Connected to RefereeBox" メッセージを確認

3. PlayerController プラグインがロードされたら：
   - チーム設定（CYAN/MAGENTA）確認
   - 各プレイヤーの IP・ポート設定確認
   - 全プレイヤーのオンライン状態を UI で確認

4. 最終確認：
   - RViz でフィールド上に 5 台のロボットが表示されているか確認
   - 各ロボットの位置情報がリアルタイム更新されているか確認
```

### 試合開始フロー
```
RefereeBox [START コマンド送信]
    ↓
RefereeBoxClient [/refcmd トピック配信]
    ↓
PlayerController [各ロボットへ START コマンド UDP 送信]
    ↓
PlayerServer [ロボット状態データを /player_states で配信継続]
    ↓
RViz [フィールド上に現在状態を表示]
```

### 一般的なトラブルシューティング

#### 1. PlayerServer がロボット通信を受信できない

**症状**: PlayerServer のログに "No data received from robots" など

**対策**:
```bash
# 1. Bind IP 設定を確認
ip addr show              # 利用可能なネットワークインターフェース表示
ifconfig                  # または ifconfig コマンド

# 2. ファイアウォール確認（UDP ポート開放）
sudo ufw allow 9000/udp   # または対応ポート
sudo ufw reload

# 3. ロボット側からの疎通確認
nc -ul 0.0.0.0 9000      # netcat でリッスン確認

# 4. ロボット側ネットワーク設定確認
ssh robot@<robot-ip>
ping <basestation-ip>     # basestation への ping が通るか確認
```

#### 2. RefereeBoxClient が RefereeBox に接続できない

**症状**: RefereeBoxClient 画面に "Connection Failed" など

**対策**:
```bash
# 1. RefereeBox が起動しているか確認
ping <referee-box-ip>

# 2. RefereeBox のポート設定を確認（通常 TCP/3000 など）
netstat -an | grep 3000   # RefereeBox ポート確認

# 3. basestation から接続テスト
telnet <referee-box-ip> 3000

# 4. コマンドフォーマット確認
# RefereeBox がバイナリ送信かテキスト送信かレコード
# （バイナリの場合、JSON ラップされていない可能性）
```

#### 3. PlayerController がプレイヤーへコマンドを送信できない

**症状**: プレイヤーが RefereeBox 指令に応答しない

**対策**:
```bash
# 1. Player 側のリッスンポート確認
ssh robot@<robot-ip>
netstat -ul | grep 9999   # または対応ポート

# 2. basestation から Player への UDP 疎通確認
echo "TEST" | nc -u <player-ip> 9999

# 3. コマンドフォーマット確認
# Player 側で期待されるコマンド形式をログで確認
# （RefereeBox → Player 変換が正しいか）

# 4. PlayerController のコマンド送信ログを確認
# rqt 画面の "Command Log" を確認
```

#### 4. RViz にロボットが表示されない、またはロボット位置が更新されない

**症状**: RViz 画面に 5 台のロボットが表示されない

**対策**:
```bash
# 1. /player_states トピック確認
ros2 topic list | grep player_states

# 2. トピックの内容確認
ros2 topic echo /player_states   # リアルタイムデータ表示

# 3. TF フレーム確認
ros2 run tf2_tools view_frames    # TF ツリー表示

# 4. NodeGraph で疎通確認
# rqt 上の [Plugins] → [ROS Integration] → [Node Graph] 
# で PlayerServer → RViz の接続を視認
```

#### 5. 通信は確立されているが、ロボットが動作しない

**症状**: RBOXコマンドが "START" でも、ロボットが移動しない

**対策**:
```bash
# 1. ロボット側ログ確認
ssh robot@<robot-ip>
tail -f ~/ros_ws/log/*.log    # ロボット側 ROS ログ確認

# 2. コマンドフォーマット検証
# PlayerController で送信されたコマンドが、
# ロボット が期待するフォーマットか確認

# 3. コマンド変換ロジック確認
# RefereeBox コマンド (例: "KICKOFF") が
# Player フォーマット (例: "KICKOFF_POSITION") に正しく変換されているか確認
```

## 設定ファイルリファレンス

### PlayerServer 設定例
```
Bind IP: 0.0.0.0        # すべてのインターフェースをリッスン
Port: 9000              # UDP リッスンポート
```

### RefereeBoxClient 接続設定例
```
RefereeBox IP: 192.168.1.100
RefereeBox Port: 3000   # RoboCup MSL 標準ポート
```

### PlayerController ロボット設定例
```
Team Color: CYAN (1)
Player #1 IP: 192.168.1.11, Port: 9999
Player #2 IP: 192.168.1.12, Port: 9999
Player #3 IP: 192.168.1.13, Port: 9999
Player #4 IP: 192.168.1.14, Port: 9999
Player #5 IP: 192.168.1.15, Port: 9999
```

## 開発・拡張ガイド

### 新しいコマンド対応の追加（PlayerController）

新しい RefereeBox コマンドに対応する場合：

1. `musashi_rqt_player_controller/src/musashi_rqt_player_controller/rqt_player_controller.py` でコマンド定数を追加
2. `player_states_callback()` メソッドでコマンド変換ロジック実装
3. UDP 送信形式に変換してプレイヤーに送信
4. 動作確認後、README.md の対応コマンド一覧に追加記載

### ロボット/プレイヤー数の変更（musashi_rviz）

デフォルト 5 台から異なるプレイヤー数に対応する場合：

```bash
# 例: 3 台で起動
ros2 launch musashi_rviz bringup_launch.py player_num:=3
```

PlayerServer は自動的に受信対象をスケーリングします。

### バイナリ通信への移行（PlayerServer）

現在のテキスト（CSV）形式からバイナリ形式への移行予定：

**変更点**:
- CSV パース処理 → バイナリアンパック処理に変更
- 通信速度が大幅向上（テスト環境で 10 倍高速化を期待）
- データ構造は変わらず（前後互換性を保つ予定）

### カスタムコマンドの実装（PlayerController）

RoboCup ルールで定義されていないカスタムコマンドを追加する場合：

1. RefereeBox 側で新規コマンド定義
2. PlayerController で解析・変換ロジック実装
3. Player 側で対応するコマンドハンドラ実装
4. 各パッケージの README に仕様記載

## API リファレンス

### ROS2 メッセージ型

#### `/refcmd` (musashi_msgs.RefereeCmd)
RefereeBox から受信したコマンド

```python
# メッセージ構造（予想）
command: str        # "START", "STOP", "KICKOFF" など
targetTeam: str     # "224.16.32.44" または "" (全体)
```

#### `/player_states` (musashi_msgs.PlayerStates)
全プレイヤーの状態集約

```python
# メッセージ構造（予想）
players: List[PlayerState]  # 5 台のロボット状態
```

#### PlayerState (musashi_msgs.PlayerState)
個別プレイヤーの状態

```python
# メッセージ構造（予想）
color: int          # CYAN=1, MAGENTA=0
id: int             # 1～5
action: int         # アクション定数値
state: int          # 状態定数値
ball_distance: float
ball_angle: float
goal_distance: float
goal_angle: float
mygoal_distance: float
mygoal_angle: float
pos_x: float        # m
pos_y: float        # m
pos_angle: float    # rad
role: int           # ロール定数値
haveBall: int       # 0/1
target_x: float     # m
target_y: float     # m
target_angle: float # rad
obs_distance: float
obs_angle: float
```

## 依存関係

### ビルド・実行依存
```
- ROS2 Humble
- rclpy (ROS2 Python クライアント)
- rqt_gui (rqt GUI フレームワーク)
- rqt_gui_py (rqt Python プラグインサポート)
- python_qt_binding (Qt バインディング)
- tf2_ros (TF ブロードキャスト/リスン)
- musashi_msgs (カスタムメッセージ型)
- geometry_msgs (標準幾何学メッセージ型)
```

### ネットワーク環境
```
- RefereeBox サーバー (TCP 接続)
- プレイヤーロボット ×5 台 (UDP 通信)
- ROS2 DDS ミドルウェア (複数PC 通信用)
```

## 参考資料・関連ドキュメント

### 外部リンク
- [RoboCup MSL League Rules](https://robocupssl.github.io/ssl-rules/)
- [ROS2 Documentation](https://docs.ros.org/en/humble/)
- [rqt Framework](https://docs.ros.org/en/humble/Tutorials/Intermediate/RQt/Using-Rqt-Console.html)

### 内部参考
- [musashi_player Communication 仕様](../../musashi_player/communication)
- [musashi_msgs メッセージ定義](../../musashi_msgs)
- [basestation 各パッケージ README](./README.md)

## 変更履歴

### Version 0.0.0 (初版)
- basestationの基本構成確定
- RefereeBoxClient TCP 通信実装
- PlayerController コマンド変換実装
- PlayerServer UDP 受信実装
- musashi_rviz 3D 可視化実装
