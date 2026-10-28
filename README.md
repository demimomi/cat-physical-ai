# 日本語のお願いで動く猫型ロボット
Physical AI応用1 最終課題
作成者：demimomi

## 概要
学習済みAIが日本語のお願いから行き先を選び、猫型の車輪ロボットがGazebo上で指定順に移動します。

## 必要な環境
Ubuntu 22.04、ROS 2 Humble、Gazebo Fortress、Python 3.10。
ROSパッケージ：ros-humble-desktop、ros-humble-ros-gz。

以下のコマンドは、このREADMEがあるフォルダで実行します。

## AI環境の準備
```bash
sudo apt install -y python3-venv
python3 -m venv ~/cat_ai_env
~/cat_ai_env/bin/python -m pip install --upgrade pip
~/cat_ai_env/bin/python -m pip install -r requirements-lock.txt --extra-index-url https://download.pytorch.org/whl/cpu
```
初回実行時はAIモデルをダウンロードするため、インターネット接続が必要です。

## 起動方法
Ubuntuのターミナルを3つ開き、それぞれこのフォルダへ移動します。

### 1：Gazebo
```bash
bash start_cat.sh
```
Gazeboが開いたら、▶を押してシミュレーションを開始します。

### 2：ROSとGazeboの通信
```bash
source /opt/ros/humble/setup.bash
ros2 run ros_gz_bridge parameter_bridge \
'/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist' \
'/model/demoRobot/odometry@nav_msgs/msg/Odometry[ignition.msgs.Odometry'
```
このターミナルは動かしたままにします。

### 3：AIへのお願い
```bash
source /opt/ros/humble/setup.bash
~/cat_ai_env/bin/python cat_ai.py
```
入力例：
窓から外を見たい、それから何か食べたい、最後にベッドで休みたい

実行結果：
窓辺 → ごはん → 寝床

判定だけを試す場合：
```bash
~/cat_ai_env/bin/python cat_ai.py --dry-run
```
各プログラムはCtrl+Cで終了します。

## AIの役割
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2をCPUで使用します。
入力文と行き先ごとの例文をベクトル化し、コサイン類似度から行き先を選びます。追加学習は行っていません。
類似度は正解確率ではありません。文章の分割と移動制御にはルールを使用しています。

## 工夫と制約
猫の耳や顔、しっぽを追加し、ごはん・窓辺・寝床の目印を配置しました。
言い換えたお願いと、行き先の順序変更による移動を確認しました。
対応する行き先は3か所です。否定や複雑な指示の理解、障害物回避には対応していません。
猫の外観を持つ車輪ロボットであり、四足歩行は行いません。

## 参考・ライセンス
元のロボット：
https://github.com/OsawaKousei/2DRoboPrac_ws

参考記事：
https://qiita.com/N622/items/9d89f77d85d9da0af29e

AIモデル：
https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

元リポジトリのLICENSEを同梱しています。
