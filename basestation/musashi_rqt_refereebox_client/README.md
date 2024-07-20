# musashi_rqt_refereebox_client
レフェリーボックスとTCP通信を行うrqtプラグインパッケージである
## ノード    
### rqt_refereebox_client 
レフェリーボックスと通信を行うrqtプラグインノードである  
#### 実行方法  
colconビルド完了後，以下でrqtプラグインノードが起動する（スタンドアローン実行）．  
`ros2 run musashi_rqt_refereebox_client refereebox_client`  
#### パブリッシュ    
|topic|message type|description|
|---|---|---|
/refcmd | musashi_msgs.RefereeCmd | レフェリーボックスから受信したコマンド |
||||
#### サブスクライブ  
|topic|message type|description|
|---|---|---|
/player_states | musashi_msgs.PlayerStates | 全プレイヤーの状態 |
||||
## フォルダ構造  
<pre>
refereebox_client（このフォルダ）
├── resource
├── scripts
├── src
└── test
</pre>
