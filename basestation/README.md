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

## クイックスタート

### 推奨: 統合Launch Package を使用

**全コンポーネントを一括起動：**
```bash
ros2 launch musashi_basestation rqt_basestation.launch.py
```

このコマンド一つで以下の4つが自動起動されます：
- **RViz** (フィールド可視化)
- **RefereeBoxClient** (RefereeBox通信)
- **PlayerServer** (プレイヤー状態受信)
- **PlayerController** (プレイヤーコマンド送信)

詳細は [musashi_basestation/README.md](./musashi_basestation/README.md) を参照してください。

### 手動起動（トラブルシューティング用）

コンポーネントを個別に起動する場合、[トラブルシューティング](#トラブルシューティング) セクションの「問題3: ウィンドウが起動されない場合」を参照してください

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

## パッケージ詳細リファレンス

詳細な仕様は各パッケージのREADMEを参照してください：

- **[musashi_basestation](./musashi_basestation/README.md)** - 統合Launch Package
- **[musashi_rqt_refereebox_client](./musashi_rqt_refereebox_client/README.md)** - RefereeBox TCP通信
  - コマンド一覧、通信仕様、JSON形式詳細
- **[musashi_rqt_player_controller](./musashi_rqt_player_controller/README.md)** - プレイヤーコマンド送信
  - コマンド変換テーブル、UDP通信仕様
- **[musashi_rqt_player_server](./musashi_rqt_player_server/README.md)** - プレイヤーデータ受信
  - CSV形式フォーマット（20フィールド）、ネットワーク設定
- **[musashi_rviz](./musashi_rviz/README.md)** - フィールド可視化
  - launch詳細、TFフレーム階層、パラメータ

### クイックリファレンス：コマンド変換

| RefereeBox | Player向け | 説明 |
|-----------|----------|------|
| START | START | 試合開始 |
| STOP | STOP | 試合停止 |
| KICKOFF | KICKOFF_POSITION | キックオフ位置移動 |
| GOALKICK | GOALKICK_POSITION | ゴールキック位置 |
| FREEKICK | FREEKICK_POSITION | フリーキック位置 |
| THROWIN | THROWIN_POSITION | スロー・イン位置 |
| CORNER | CORNER_POSITION | コーナーキック位置 |
| PENALTY | PENALTY_POSITION | ペナルティキック位置 |
| DROP_BALL | DROP_BALL | ボールドロップ |

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

### 試合前のチェックリスト

#### ネットワーク環境確認（統合Launch後）
- [ ] RefereeBox PC の IP・ポート番号を把握
- [ ] basestation PC の Network Interface を確認 (`ip addr show`)
- [ ] 全プレイヤーロボット（5台）の IP アドレスリスト確認
- [ ] ネットワーク接続性を事前確認 (`ping` で各装置を確認)

#### GUI起動後の初期化手順

Launch起動後、以下のGUI設定・確認を実施します：

**PlayerServer タブ:**
- Bind IP、Port を確認（またはカスタマイズ）
- [Start] ボタンクリック → UDP受信開始

**RefereeBoxClient タブ:**
- RefereeBox IP・ポート番号を設定
- [Connect] ボタン → 接続確立

**PlayerController タブ:**
- チーム設定、各プレイヤーIP・ポートを確認
- 全プレイヤーのオンライン状態確認

**RViz確認:**
- フィールド上に 5 台のロボットが表示されているか確認
- 各ロボット位置がリアルタイム更新されているか確認

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

## ROS2 トピック一覧

| トピック | メッセージ型 | 発行元 | 購読元 | 説明 |
|---------|-----------|------|------|------|
| `/refcmd` | `musashi_msgs/RefereeCmd` | RefereeBoxClient | PlayerController | RefereeBox → basestation |
| `/player_states` | `musashi_msgs/PlayerStates` | PlayerServer | PlayerController, RViz | プレイヤー状態情報 |

詳細なメッセージ構造は各パッケージREADMEを参照してください。

## 必要なツール

- **ROS2 Humble** - メインミドルウェア
- **rqt** - GUI フレームワーク
- **RViz2** - 3D可視化エンジン
- ネットワーク診断: `ping`, `netstat`, `nc` (netcat) など

## 拡張・開発について

### コマンド対応やロボット数変更

詳細は各パッケージのREADMEを参照してください：
- 新規コマンド対応 → [musashi_rqt_player_controller/README.md](./musashi_rqt_player_controller/README.md#開発拡張ガイド)
- ロボット数変更 → [musashi_rviz/README.md](./musashi_rviz/README.md#実行方法)
- バイナリ通信移行予定 → [musashi_rqt_player_server/README.md](./musashi_rqt_player_server/README.md)

## 参考資料

- [RoboCup MSL 公式ルール](https://robocupssl.github.io/ssl-rules/)
- [ROS2 Humble 公式ドキュメント](https://docs.ros.org/en/humble/)
- Hibikino-Musashi チーム Wiki (内部)

## テスト用RefereeBoxサーバ（dummy_refbox_server.py）の使い方

rqt_refereebox_clientアプリの動作確認やデバッグ用に、TCP通信を模擬するダミーサーバを用意しています。

### 使い方
1. サーバ起動

```sh
cd basestation/musashi_rqt_refereebox_client/test
python3 dummy_refbox_server.py
```

2. クライアント（rqt_refereebox_client等）から接続
   - サーバ側で「Client connected from ...」と表示されれば接続成功

3. 任意のタイミングでJSONコマンド送信
   - サーバ側CUIで以下のように入力
   ```
   {"command": "START", "targetTeam": "CYAN"}
   ```
   - 入力したJSONがそのままクライアントへ送信されます
   - 'exit' と入力するとサーバを終了します

4. クライアントからの受信データもサーバ側に表示されます
