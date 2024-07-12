# musashi-ros2-humble
本パッケージは Robocup Hibikino-Musashi のROS2用リポジトリになります．
Visual Studioを用いたC++のみの開発に限界を感じてきたため，
レフェリーボックスの仕様変更に合わせて新たなUbuntuベースのHibikino-musashiとすべく，開発を開始する．    

## 開発環境  
- OSディストリビューション: Ubuntu 22.04  
- ROSディストリビューション: ROS2 humble  
- IDE: Visual Studio Code（エディタ）  
- 言語: python，C++  

## コーディング規約（命名規則） 
### python   
PEP8コードスタイルに準拠する．
以下を参照すること．  
`https://peps.python.org/pep-0008/#code-lay-out`  
`https://atmarkit.itmedia.co.jp/ait/articles/2308/08/news020.html`  

## ディレクトリ構成     
<pre>
musashi-ros2-humble（ルートディレクトリ）  
├── README.md
├── basestation
├── behavior
├── hardware
├── localization
├── musashi_description  
├── musashi_msgs
└── perception
</pre>

|Name|Detail|  
|---|---|
|README.md|このファイル|
|basestation|レフェリーボックス・プレイヤーとの通信，GUIを含むパッケージのディレクトリ|
|behavior|ルールベース行動決定，ステートマシン，行動選択のディレクトリ|
|hardware|外部デバイス制御用のディレクトリ|
|localization|自己位置推定用のディレクトリ|
|musashi_description|ロボットモデルを管理するディレクトリ|  
|musashi_msgs|独自メッセージ用のディレクトリ|
|perception|外界認識，知覚系のディレクトリ|

## ビルドコマンド  
- 全パッケージの一括ビルド  
ワークスペースのルートディレクトリで以下を実行する．  
`colcon build --symlink-install`  

- basestation（旧コーチボックス）関連のみビルド  
以下コマンドで関連パッケージの一括ビルド． 
NeoAPIライブラリやMaxonEPOSライブラリを未インストールなPCでbasestationだけ動かしたい場合は便利．   
``colcon build --packages-select musashi_rqt_player_server musashi_rqt_refereebox_client player_controller ``  

## パッケージ作成コマンド例  
- pythonパッケージ  
``ros2 pkg create [package name] --build-type ament_python --dependencies rclpy``  
- C++パッケージ  
``ros2 pkg create [package name] --build-type ament_cmake --dependencies rclcpp``  
- pythonのrqtプラグインパッケージ  
`ros2 pkg create [package name] --build-type ament_python --dependencies rclpy python_qt_binding rqt_gui rqt_gui_py rqt_py_common