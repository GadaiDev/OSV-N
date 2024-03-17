# 最新情報
 - もうOSV-Nのソースコードはzipにしてまとめます。releaseにあると思います

# OSVを運営する方法
とりあえず箇条書き
 - Python3.10.0を入れる。
 - Flask 3.0.2とFlask 5.3.6を入れる。
 - Linuxコマンド:「pip install flask flask-socketio」
 - Windowsコマンド:「py -m pip install flask flask-socketio」
 - Macコマンド:Mac触ったことないです。知らない。
# ソースコードのエラー
Windows以外は大体最初に「IPConfig」ってコマンドが見つからない的なのが出ると思います。<br>
`print(os.system("ipconfig"))`<br>って書いてある行だけ消しましょう。
Windows向けに作られてるので、Windows使ってる人は心配しなくて大丈夫です。

## ソースコードが読みにくい
ごめんなさい。
