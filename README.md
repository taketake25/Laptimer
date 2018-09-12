# Laptimer

関西合同ロボコン2018のために作られた、ライントレーサ用のラップタイマーです。
https://github.com/baoboa/pyqt5/blob/master/examples/widgets/digitalclock.py
のプログラムを改造しました。

動作環境は以下の通りです。
・Raspberry Pi 2 (タイマー処理、GUIに使用)
  PyQt5(GUI)とsmbus(i2c)のライブラリを使用しています。
・Nucleo F030R8  (フォトトランジスタの値をi2cでRaspiに送信(Slaveとして))
  mbedの環境にて開発しました。
  frequencyは400kHzに変更したほうがいいでしょう。
  Raspiから's'を受信で、センサー1の結果を0/1で、
  Raspiから'g'を受信で、センサー1の結果を0/1で返信するだけです。
  しきい値は適当に調節してください。

タイマーの機能は以下の通りです。
・3分間の時間制限で、3回までのラップの時間計測 //時間制限はまだ未実装
・
・csvファイルから出場機体のデータ入力、および別csvファイルへの出力
  読み込むデータは現在、[選手番号、所属団体、選手名、機体名]を
  次のような形式でデータが保存していることを想定しています。
  utf-8なので、もちろん日本語で使用できます。
    0 ｜dummy｜dummy｜dummy ｜dummy  //1,1の数値にゴミが入るため、ダミー行
    1 ｜ABC団｜Jacky｜hoge--｜dummy
    2 ｜BCD研｜Cheng｜foobar｜dummy
    … ｜  …  ｜  …  ｜  …   ｜  …
    15｜OPQ興｜Buyan｜himitu｜dummy
    -1｜dummy｜dummy｜dummy ｜dummy  //最終行以降、データがない領域でエラーより、ダミー行たくさん...
    -1｜dummy｜dummy｜dummy ｜dummy
    -1｜dummy｜dummy｜dummy ｜dummy

RaspiのためのADCが身近になかったので、Nucleoで値を取っていますが、所持している方はそっちでやったほうが楽でしょう。

読み込めるCSVファイルの文字コードはunicodeです。
Excelで作成したCSVファイルを、Visual Studio Codeなどを用いて、「utf-8 with BOM」形式で保存し、WinSCPやFTPPPなどでRasPiのほうに転送しましょう。
