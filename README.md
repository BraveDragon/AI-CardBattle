# AI-CardBattle

一人用カードゲームです。
強化学習について勉強したので、自分が長く使用しているUnityと組み合わせて何かゲームを作れないかと思い作成しました。
AIにはUnity ML-Agentsを利用しました。
さらに、Unity ML-Agents Python Low Level APIとChainerを利用して自作した強化学習のAIを学習させてみました。

## ＜内容＞

- Assetsフォルダ：ゲーム作成に使用したファイルが入っています。

- CardBattleフォルダ：AIの学習用環境が入っています。

- CardBattle_Linuxフォルダ：完成済みゲームのLinuxビルドです。

- CardBattle_Macフォルダ：完成済みゲームのMacビルドです。

- CardBattle_WebGLフォルダ：完成済みゲームのWebGLビルドです。

- CardBattle_Showフォルダ：完成済みゲームのWindowsビルドです。

## ＜使用したライブラリ・ツール＞

Unity : 2019.3.15f1 

Unity ML-Agents : Release 3  

Python : Python 3.7.7

chainer : 6.7.0

cupy : 7.5.0 (CUDAのバージョン : 10.2)

## 実際のプレイ動画

## ＜ゲームの遊び方＞

「ゲームの遊び方.md」をご覧ください。

## ＜プロジェクトのビルド方法＞

「プロジェクトのビルド方法.md」をご覧ください。

## ＜今後の課題＞

自作した強化学習のAIを学習させることはできましたが、そのAIをゲーム本体に組み込むことがどうしてもできませんでした。

今後はAIのゲーム本体への組み込みが課題です。

また、自作した強化学習のAIの学習はWindows環境下でしか行っていないので、他の環境下での検証も時間があればやってみたいです。

## ＜ライセンス＞

This Repository includes the work that is distributed in the Apache License 2.0.

Apache License 2.0のライセンス条文：

URL: http://www.apache.org/licenses/LICENSE-2.0

### Unity ML-Agents

Apache License 2.0

Copyright 2017 Unity Technologies

Apache License 2.0のライセンス条文：

URL: http://www.apache.org/licenses/LICENSE-2.0

