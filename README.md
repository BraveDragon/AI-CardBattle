# AI-CardBattle

一人用カードゲームです。
強化学習について勉強したので、自分が長く使用しているUnityと組み合わせて何かゲームを作れないかと思い作成しました。
AIにはUnity ML-Agentsを利用しました。
さらに、Unity ML-Agents Python Low Level APIとChainerを利用して自作した強化学習のAIを学習させてみました。
また、Dockerについても勉強したので、WebGLビルドをプレイするためのDockerコンテナを生成するためのDockerfileを作成し、リポジトリに追加しました。

## ＜内容＞

- Assetsフォルダ：ゲーム作成に使用したファイルが入っています。

- CardBattleフォルダ：AIの学習用環境が入っています。

- CardBattle_Linuxフォルダ：完成済みゲームのLinuxビルドです。

- CardBattle_Macフォルダ：完成済みゲームのMacビルドです。

- CardBattle_WebGLフォルダ：完成済みゲームのWebGLビルドです。

- CardBattle_Showフォルダ：完成済みゲームのWindowsビルドです。

- Dockerfile：完成済みゲームのWebGLビルドをプレイするためのDockerコンテナを生成します。詳しいプレイ方法は「プロジェクトのビルド・AIの学習方法.md」をご覧ください。

## ＜使用したライブラリ・ツール＞

Unity : 2019.3.15f1 

Unity ML-Agents : Release 3  

Python : Python 3.7.7

chainer : 6.7.0

cupy : 7.5.0 (CUDAのバージョン : 10.2)

## 実際のプレイ動画

![Demoplay](https://github.com/BraveDragon/AI-CardBattle/blob/master/DemoPlay.gif)

## ＜ゲームの遊び方＞

「ゲームの遊び方.md」をご覧ください。

## ＜プロジェクトのビルド・AIの学習方法＞

「プロジェクトのビルド・AIの学習方法.md」をご覧ください。

## ＜今後の課題＞

自作した強化学習のAIを学習させることはできましたが、そのAIをゲーム本体に組み込むことがどうしてもできなかったので、今回はML-Agentsが提供しているAIを組み込みました。

今後は自作した強化学習のAIをゲーム本体への組み込むことが課題です。

また、自作した強化学習のAIの学習はWindows環境下でしか行っていないので、他の環境下での検証も時間があればやってみたいです。

## ＜ライセンス＞

このプログラムにはApache License 2.0のライセンスが設定されています。

利用の際にはこのリポジトリに含まれている「LICENSE」ファイルとApache License 2.0のライセンス条文

(URL: http://www.apache.org/licenses/LICENSE-2.0 )をよく読んで、ライセンスに従ってご利用ください。

This Repository includes the work that is distributed in the Apache License 2.0.

Apache License 2.0のライセンス条文：

URL: http://www.apache.org/licenses/LICENSE-2.0

### Unity ML-Agents

Apache License 2.0

Copyright 2017 Unity Technologies

Apache License 2.0のライセンス条文：

URL: http://www.apache.org/licenses/LICENSE-2.0

