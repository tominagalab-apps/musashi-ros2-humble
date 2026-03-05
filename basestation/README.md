[Home](../README.md)  
# basestation（旧コーチボックス）  
コーチボックス関係のパッケージを配置しているディレクトリです．  
basestationは以下の二つの画面で構成されている．両方の画面を起動することで試合の状態が可視化される．  
なお，**両画面を出さない限りRefereeBox->basestation->playerへのコマンド通信がされず試合ができないので注意すること**    

|Display|Description|  
|---|---|
|rviz|rviz上に3Dでフィールドおよびプレイヤーを表示する画面．試合中の状態を可視化する．|  
|rqt|GUI画面．レフェリーボックスとの通信や，各プレイヤーとの通信を担当する．| 

## 実行方法  
### rviz画面  
以下をターミナルで実行することで設定済みのrviz2が起動する．

```bash
ros2 launch musashi_rviz bringup_launch.py
```

[bringup_launch.py](./musashi_rviz/launch/bringup_launch.py) はトップレベルの launch で、
フィールド表示ノード・RViz を起動し、プレイヤー分の `player_spawn_launch.py` を含む `team_spawn_launch.py` を起動します。

プレイヤー数を変更したい場合は `team_spawn_launch.py` の `player_num` 引数を使います（デフォルトは 5）。例:

```bash
ros2 launch musashi_rviz team_spawn_launch.py player_num:=3
```

各プレイヤーのフレームプレフィックスは内部で `player1/`, `player2/` のように設定されます。
### rqt画面  
以下をターミナルで実行する．  
`rqt`  
空のrqt_gui画面が出るはずなので，左上の"Plugins"から以下の三つのプラグインをロードする．  
1. Hibikino-Musashiの**RefereeBoxClient**  
1. Hibikino-Musashiの**PlayerServer**  
1. Hibikino-Musashiの**PlayerController**  

#### 重要な変更点（最近の更新）
- `PlayerServer` プラグインに **Start / Stop** ボタンを追加しました。起動時に自動でサーバを立ち上げず、GUI から明示的に開始・停止できます。
- `PlayerServer` の UI に **Bind IP (Own IP)** と **Port** 入力欄を追加しました。複数インターフェース環境ではここでバインド先を指定してください。
- `musashi_rviz` の起動引数 `player_num` を導入しました（デフォルトは 5）。RViz 側のプレイヤー数と `PlayerServer` の送受信は一致させてください。
- RefereeBox クライアントは受信バッファを実装し、NULL 終端（`\0`）でメッセージを区切ってパースするよう改善しました。部分受信や複数メッセージの連結に対して堅牢になっています。

これらにより、運用時に以下を意識してください：
- `PlayerServer` を使う場合はまず GUI 上で `Start` を押してからプレイヤーとの通信を開始してください。
- RefereeBox サーバはメッセージ末尾に `\0` を付与して送信する想定です（互換性のためクライアント側は `\0` を許容します）。

## ディレクトリ構成  
<pre>
basestation
├── README.md
├── musashi_rqt_player_controller
├── musashi_rqt_player_server
├── musashi_rqt_refereebox_client
└── musashi_rviz
</pre>

## パッケージリスト  
|Package name|Description|
|---|---|
|musashi_rqt_player_controller|各プレイヤーへのデータ送信を行うパッケージ．rqtプラグインとして開発している|
|musashi_rqt_player_server|各プレイヤーからのデータ受信を行うパッケージ．rqtプラグインとして開発している|  
|musashi_rqt_refereebox_client|レフェリーボックスと通信を行うパッケージ．rqtプラグインとして開発している|  
|musashi_rviz|試合の状態を確認するrviz画面を構成するためのパッケージ|

## RefereeBoxとCoachBox間通信について
RefereeBoxとはTCPで送受信を行います．
### RefereeBox→basestation
レフェリーボックスからはゲームコマンドが送られてきます．  
#### コマンドフォーマット詳細  
- RefereeBoxからはJSON形式の文字列データがバイナリデータで送られてくる．  
- JSON形式は次のようになる    
```
{
  command: {コマンド文字列}
  targetTeam: {ターゲットチーム文字列}
}
```
- 上記の文字列の末尾には終端を表す'\0'がつけられて送られてきます．
- {コマンド文字列}には"WELCOME"や"START"などの文字列が入ります．  
- {ターゲットチーム文字列}には"224.16.32.*"で各チームに割り振られているIPアドレスの文字列データが入ります．あるいは __空（""）__ の場合があります． 
  - 空（""）の場合は試合中の両チーム宛に送っていることを意味するコマンドになります．  
  （例）commandが"START"や"DROP_BALL"ではtargetTeamは空です．  
  - ターゲットチーム文字列（"224.16.32.*"）が入っている場合は，そのチームにするコマンドになります．  
  （例）commandが"KICKOFF"で，targetTeamが"224.16.32.44"の場合は，チームHibikino-Musashiがキックオフであることを意味するので，自チームのキックオフポジションに移動し，"START"コマンドを待機する必要がある． 

#### コマンド文字列一覧  
レフェリーボックスからは以下のコマンド文字列が送られてきます．  
|command|targetTeam|  
|-------|----------|  
|"START"|""|  
|"STOP"|""|  
|"DROP_BALL"|""|  
|"HALF_TIME"|""|  
|"END_GAME"|""|  
|"GAME_OVER"|""|  
|"PARK"|""|  
|"FIRST_HALF"|""|  
|"SECOND_HALF"|""|  
|"FIRST_HALF_OVERTIME"|""|
|"SECOND_HALF_OVERTIME"|""|
|"RESET"|""|
|"WELCOME"|"224.16.32.*"|
|"KICKOFF"|"224.16.32.*"|
|"FREEKICK"|"224.16.32.*"|
|"GOALKICK"|"224.16.32.*"|
|"THROWIN"|"224.16.32.*"|
|"CORNER"|"224.16.32.*"|
|"PENALTY"|"224.16.32.*"|
|"GOAL"|"224.16.32.*"|
|"REPAIR"|"224.16.32.*"|
|"YELLOW_CARD"|"224.16.32.*"|
|"DOUBLE_YELLO"W|"224.16.32.*"|
|"RED_CARD"|"224.16.32.*"|
|"SUBSTITUTION"|"224.16.32.*"|
|"IS_ALIVE"|"224.16.32.*"|

### basestation→RefereeBox
basestationはRefereeBoxに所定のjson形式のログファイルを周期的に送信しなければならない．  
送信時における通信仕様の詳細は[MSL_WMDataStruct](https://msl.robocup.org/wp-content/uploads/2018/08/MSL_WMDataStruct.pdf)を参照すること．  
#### 送信データの概要
以下のデータを指定のjson形式で送る必要がある.  
- 全ロボットのデータ 
  - ID（1~5の整数）
  - 現在姿勢（x[m], y[m], theta[rad]）
  - 目標姿勢（x[m], y[m], theta[rad]）
  - バッテリー残量[%]
  - ボール保持（0:未保持, 1:保持）
- ボールのデータ
  - ワールド座標系におけるボール位置（x[m], y[m], z[m]）
  - 

## CoachBoxとPlayer間の通信について  
CoachBoxとPlayerはUDPで通信を行っています．  
- 具体的な通信処理については"musashi_player/communication/communication.cpp"を参照してください．  
  - UDPの受信処理については"recv"関数で行われています．  
  - UDPの送信処理については"send"関数で行われています．  
### CoachBox→Playerへの通信  
CoachBoxはRefereeBoxから送られてきたコマンドに基づいて，各プレイヤーへコマンドを送信します．  
この時，Hibikino-Musashi内で取り決められたコマンドフォーマットに変換して送る必要があります．  
#### 通信フォーマット  
...
### Player→CoachBoxへの通信  
各プレイヤーからは各プレイヤーの状態データが格納された文字列データが送られてくる．  
（※バイナリデータになっていないことに注意）  
#### 通信フォーマット　　
カンマ（","）区切りで以下の順に整数文字が入った文字列で送られてくる  

|index|value|detail|
|-----|-----|-----| 
|1|color|チームカラー．CYANなら0，MAGENTAなら1|
|2|id|ロボットのID|
|3|action|ロボットのアクション（Action名前空間の定数値）|
|4|state|ロボットのステート（State名前空間の定数値）|
|5|ball.distance|ボールとの直線距離|
|6|ball.angle|ボールの角度|
|7|goal.distance|ゴールとの直線距離|
|8|goal.angle|ゴールの角度|
|9|myGoal.distance|自身のゴールとの直線距離|
|10|myGoal.angle|自身のゴールの角度|
|11|position.x|自己位置x座標|
|12|position.y|自己位置y座標|
|13|position.angle|姿勢θ|
|14|role|ロボットのロール（Role名前空間の定数値）|
|15|haveBall|ボール保持の有無|
|16|moveto_position.x|ロボットの目標x座標|
|17|moveto_position.y|ロボットの目標y座標|
|18|moveto_position.angle|ロボットの目標姿勢θ|
|19|obstacle.distance|障害物までの直線距離|
|20|obstacle.angle|障害物の角度|

コーチボックス側では，受信後に”,”でsplitして文字列から整数値への変換が必要になる．  
一つの変数が何文字なのかは","でsplitするまでわからない．  
__いずれバイナリデータで送受信する方法に修正し通信速度の高速化を図る必要がある__  

## 実装したい機能  
- キッカー差動ボタン  
- コンパス校正開始ボタン  
- パーティクル再配布ボタン  
- RoleとColorの可視化   