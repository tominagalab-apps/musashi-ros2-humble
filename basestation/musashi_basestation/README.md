[← Back to basestation](../README.md)

# musashi_basestation

## 概要

**musashi_basestationは、RoboCup MSL basestationの統合launch packageです。**

RefereeBoxClient、PlayerServer、PlayerController、および musashi_rviz の4つのコンポーネントを、単一の統合launch fileで起動します。これにより、複雑なコンポーネント配置を簡潔にし、運用時の起動手順を大幅に簡略化できます。

### 主な機能
- **統合起動**: 全basestation関連コンポーネントの一括立ち上げ
- **複数ウィンドウ起動**: 各コンポーネント（rqt×3、RViz）を別ウィンドウで起動
- **自動ロード**: 保存済みrqt設定ファイルの自動ロード対応
- **簡単セットアップ**: 1つのコマンドで全ての管制システムが起動

## ディレクトリ構成

```
musashi_basestation/
├── README.md (このファイル)
├── package.xml
├── setup.py
├── setup.cfg
├── config/ (rqt設定ファイル) ────────────────┐
│   ├── rqt_basestation_plugins.rqt  │
│   └── rqt_player_control.rqt       │
├── launch/ (統合launch file)       │
│   └── bringup.launch.py            │
├── resource/                       │
│   └── musashi_basestation          │
├── src/                             │
│   └── musashi_basestation/         │
│       └── __init__.py              │
└── test/                           │
    └── test_*.py                    │
                                    │
起動時に自動ロード ←────────────────────┘
```

## 使用方法

### 基本的な起動（推奨）

```bash
ros2 launch musashi_basestation bringup.launch.py
```

このコマンド一つで、以下の処理が実行されます：

1. **RefereeBoxClient** (rqt plugin) ← TCP/IP: RefereeBox通信
2. **PlayerServer** (rqt plugin)   ← UDP: プレイヤー状態受信
3. **PlayerController** (rqt plugin) ← UDP: プレイヤーコマンド送信
4. **RViz** (from musashi_rviz)    ← TF: フィールド可視化

各コンポーネントは**独立した専用ウィンドウ**で起動されます。

### 起動後の画面配置

```
┌────────────────────────────────────┐
│  RViz (フィールド可視化)              │
│  [フィールド]                         │
│  [プレイヤー位置表示]                  │
└────────────────────────────────────┘

┌─────────────────────┬──────────────────┬──────────────────┐
│ RefereeBoxClient    │ PlayerServer     │ PlayerController │
│ [接続管理]          │ [受信管理]        │ [送信管理]        │
│ [コマンドログ]      │ [プレイヤーログ]  │ [コマンド監視]    │
└─────────────────────┴──────────────────┴──────────────────┘
```

## Launch ファイル詳細

### bringup.launch.py

**トップレベルの統合launch file** ─ 通常こちらを起動します

#### 起動するコンポーネント

| # | コンポーネント | パッケージ | 役割 | ウィンドウ |
|----|-------------|-----------|------|--------|
| 1 | RefereeBoxClient | musashi_rqt_refereebox_client | RefereeBox通信 | 独立ウィンドウ |
| 2 | PlayerServer | musashi_rqt_player_server | プレイヤー状態受信 | 独立ウィンドウ |
| 3 | PlayerController | musashi_rqt_player_controller | プレイヤーコマンド送信 | 独立ウィンドウ |
| 4 | RViz + フィールド | musashi_rviz | フィールド・ロボット可視化 | 独立ウィンドウ |

#### 処理フロー

```python
# Launch Description 構成要素

└─ LaunchDescription([ 
    ├─ ExecuteProcess (RefereeBoxClient) 
    │  └─ cmd: ['rqt', '-s', 'musashi_rqt_refereebox_client.RqtRefereeBoxClient']
    │
    ├─ ExecuteProcess (PlayerServer)
    │  └─ cmd: ['rqt', '--standalone', 'musashi_rqt_player_server']
    │
    ├─ ExecuteProcess (PlayerController)
    │  └─ cmd: ['rqt', '--standalone', 'musashi_rqt_player_controller']
    │
    └─ IncludeLaunchDescription (musashi_rviz bringup)
       └─ 'musashi_rviz/launch/bringup_launch.py'
])
```

#### rqtプラグイン起動方式

各rqtコンポーネントは以下の形式で起動されます：

```bash
rqt -s musashi_rqt_<package>.rqt_<package>.Rqt<Component>
```

- `-s` フラグ: 指定したpluginのみをロード
- `<package>`: rqtプラグインを実装したパッケージ
- `Rqt<Component>`: プラグインクラス名

### 設定ファイル

#### config/rqt_basestation_plugins.rqt

保存済みrqt設定ファイル。複数のrqtプラグインを統一のウィンドウにロードする設定が含まれます。

**利用方法**:
```bash
# 既存設定ファイルをロードして起動（オプション）
rqt --standalone musashi_rqt_refereebox_client.plugin.RefereeBoxClientPlugin \
    --standalone musashi_rqt_player_server.plugin.PlayerServerPlugin \
    --standalone musashi_rqt_player_controller.plugin.PlayerControllerPlugin
```

#### config/rqt_player_control.rqt

プレイヤー制御に特化した設定ファイル。PlayerController のみをロード。

## 実行オプション

現在のlaunch fileは固定パラメータ（5プレイヤー、標準設定）で実行されます。

### カスタマイズ例

**デモ環境（3プレイヤー）での起動**:

launch ファイルを一時的に修正するか、以下の手順で対応：

```bash
# 方法1: musashi_rviz の player_num パラメータを変更
ros2 launch musashi_rviz bringup_launch.py player_num:=3

# 方法2: bringup.launch.py を修正
# （下記「カスタマイズ方法」セクション参照）
```

## ディレクトリ詳細説明

### launch/

```
launch/
└── bringup.launch.py
    ├─ Import: LaunchDescription, ExecuteProcess, IncludeLaunchDescription
    ├─ RefereeBoxClient 起動
    ├─ PlayerServer 起動
    ├─ PlayerController 起動
    └─ musashi_rviz::bringup_launch.py を include
```

### config/

rqtプラグイン複数起動時の設定・配置情報を保存

```
config/
├── rqt_basestation_plugins.rqt
│   └── 複数rqtプラグインの統一窓配置設定
└── rqt_player_control.rqt
    └── PlayerController 単独起動時の設定
```

### resource/

ROSパッケージインデックス用リソース（通常は空）

```
resource/
└── musashi_basestation
    └── （パッケージマーカーファイル）
```

### src/musashi_basestation/

Python パッケージディレクトリ（現在は空）

```
src/musashi_basestation/
└── __init__.py （空ファイル）
```

将来的には、basestationのユーティリティ関数をここに実装予定

### test/

パッケージのテストファイル（copyright, linting）

```
test/
└── test_*.py
    ├── test_copyright.py （ライセンスヘッダチェック）
    ├── test_flake8.py （PEP8準拠チェック）
    └── test_pep257.py （docstring規約チェック）
```

## トラブルシューティング

### 起動時のよくある問題

#### 問題1: "Cannot find package musashi_rqt_refereebox_client"

**原因**: 依存パッケージがビルドされていない

**対策**:
```bash
cd ~/ros2_ws
colcon build --packages-select musashi_rqt_refereebox_client \
                                musashi_rqt_player_server \
                                musashi_rqt_player_controller \
                                musashi_rviz
```

#### 問題2: ウィンドウが起動されない、またはすぐに終了する

**原因**: rqt環境の不具合またはdisplayサーバーの接続エラー

**対策**:
```bash
# DISPLAY 変数の確認
echo $DISPLAY

# X11 フォワーディング設定（リモート接続時）
export DISPLAY=:0

# rqt単体で起動テスト
rqt

# launch ファイルをverboseで実行
ros2 launch musashi_basestation bringup.launch.py --log-level debug
```

#### 問題3: RVizが起動されるが、他のrqtウィンドウが見えない

**原因**: ウィンドウマネージャーの設定、またはデュアルディスプレイ問題

**対策**:
```bash
# 各コンポーネント用にセパレートターミナルから起動
# ターミナル1
ros2 launch musashi_rviz bringup_launch.py

# ターミナル2
rqt -s musashi_rqt_refereebox_client.plugin.RefereeBoxClientPlugin

# ターミナル3
rqt -s musashi_rqt_player_server.plugin.PlayerServerPlugin

# ターミナル4
rqt -s musashi_rqt_player_controller.plugin.PlayerControllerPlugin
```

### デバッグモード

```bash
# Launch ファイルを詳細ログで実行
ros2 launch musashi_basestation bringup.launch.py \
    --log-level debug
```

## カスタマイズ方法

### パラメータの追加

launch ファイルにパラメータを追加する例：

```python
# bringup.launch.py を以下のように修正

from launch import LaunchDescription, LaunchContext
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    
    # プレイヤー数パラメータを追加
    player_num = LaunchConfiguration('player_num', default='5')
    
    return LaunchDescription([
        # ... (既存の ProcessExecute)
        
        # musashi_rviz に player_num を渡す
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    get_package_share_directory('musashi_rviz'),
                    'launch',
                    'bringup_launch.py'
                )
            ),
            launch_arguments={
                'player_num': player_num  # パラメータを渡す
            }
        )
    ])
```

### 起動順序の管理

launch ファイルで起動順序を制御する場合、`Event` ハンドラーを使用：

```python
from launch.event_handlers import OnExecutionComplete

OnExecutionComplete(
    target_action=refbox_client_action,
    on_completion=player_server_action
)
```

## 関連パッケージ

| パッケージ | 説明 | 起動タイミング |
|----------|------|-------------|
| [musashi_rqt_refereebox_client](../musashi_rqt_refereebox_client/README.md) | RefereeBox通信 | launch実行時 |
| [musashi_rqt_player_server](../musashi_rqt_player_server/README.md) | プレイヤー状態受信 | launch実行時 |
| [musashi_rqt_player_controller](../musashi_rqt_player_controller/README.md) | プレイヤーコマンド送信 | launch実行時 |
| [musashi_rviz](../musashi_rviz/README.md) | フィールド可視化 | launch実行時 |

## 依存関係

### ビルド・実行依存
```
- ROS2 Humble
- rqt_gui (rqt frameworkの本体)
- rviz2 (3D可視化フレームワーク)
```

### パッケージ間依存
```
musashi_basestation
├─ musashi_rqt_refereebox_client
├─ musashi_rqt_player_server
├─ musashi_rqt_player_controller
└─ musashi_rviz
```

## ビルド・テスト

### ビルド

```bash
cd ~/ros2_ws
colcon build --packages-select musashi_basestation
```

### テスト実行

```bash
# パッケージテストの実行
colcon test --packages-select musashi_basestation

# テスト結果の確認
colcon test-result --all
```

## バージョン情報

| バージョン | リリース日 | 説明 |
|----------|----------|------|
| 0.0.0 | 2026-01-XX | 初版：統合launch packageとして実装 |

## ライセンス

TODO（package.xmlのライセンス項目を参照）

## メンテナンス

- 主要開発者: Hibikino-Musashi チーム
- メンテナンス: `todo@todo.todo` （TODO: 連絡先更新推奨）

---

**参考**: 詳細な操作手順は [basestation/README.md](../README.md) を参照してください。

## 共通定数の一元管理

チームカラーや役割（MAGENTA, CYAN, ALPHA, BETA, GAMMA, DELTA, GOALIE など）の定数は、
`musashi_basestation/src/musashi_basestation/common/constants.py` にて一元管理しています。
他のbasestation配下パッケージからも `from musashi_basestation.common.constants import ...` で参照できます。

- 2026年3月：定数の共通化・一元管理を実施
