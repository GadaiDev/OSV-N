from flask import Flask, request, session, redirect, send_file
from flask_socketio import SocketIO
from osvkit import useful, bootstrap
import datetime
import socket
import re

print(socket.getaddrinfo(socket.gethostname(),80))

app = Flask(__name__)
app.secret_key = b"secret!"
sock = SocketIO(app)
bootstrap.Load_Bootstrap(app)


@app.route("/")
def page_index():
    if not "ID" in list(session.keys()):
        session["ID"] = useful.RandomID(8)
    return useful.fOpen("HTML/index.html")


@app.route("/bbs/<bbsname>/")
def page_bbs(bbsname):
    if not "ID" in list(session.keys()):
        session["ID"] = useful.RandomID(8)
    bbs_config = useful.json_load(f"BBS/{bbsname}/config.json")
    name = bbs_config["BBS_name"]
    desc = bbs_config["BBS_description"]
    thread = bbs_config["BBS_thread"]
    return useful.BBS_base(bbsname, name, desc, thread).replace("{{ BBS }}",bbsname)


@app.route("/<bbsID>/<threadID>/")
def page_thread(bbsID,threadID):
    if not "ID" in list(session.keys()):
        session["ID"] = useful.RandomID(8)
    return useful.Thread_base(bbsID,threadID).replace("{{ HN }}",session.get("HN",""))


@sock.on("Post_Thread")
def Post_Thread(data):
    bbsname = data["BBS"]

    title = useful.XSSGuard(data["Title"])
    name = useful.XSSGuard(data["Name"])
    text = useful.XSSGuard(data["Message"]).replace("\n","<br>　　")
    
    Thread_ID = useful.RandomID(12)

    bbs_dat = useful.json_load(f"BBS/{bbsname}/dat.json")
    bbs_config = useful.json_load(f"BBS/{bbsname}/config.json")

    bbs_config["BBS_thread"].append({"Title":title,"ID":Thread_ID})
    if not "ID" in list(session.keys()):
        session["ID"] = useful.RandomID(8)
    bbs_config["count"] = "1"
    if name == "":
        name == "名無しさん@OSV-Nおめでとう"
    session["HN"] = name
    bbs_dat[Thread_ID] = {"Title":title,"dat":[],"count":"1"}
    now = datetime.datetime.now()
    response = f"<a onclick='addAnker(1)'>1</a>:<b style='color:green'>{name}</b> {now.year}/{now.month}/{now.day} {now.hour}:{now.minute}:{now.second}.{now.microsecond} ID:{session.get('ID','???')}<br>　　{text}<br><br>\n"
    bbs_dat[Thread_ID]["dat"].append(response)
    useful.json_write(bbs_dat,f"BBS/{bbsname}/dat.json")
    useful.json_write(bbs_config,f"BBS/{bbsname}/config.json")


@sock.on("Post")
def Post(data):
    global session
    if not "ID" in list(session.keys()):
        session["ID"] = useful.RandomID(8)
    bbsname = data["BBS"]
    name = useful.XSSGuard(data["Name"])
    text = useful.XSSGuard(data["Message"]).replace("\n","<br>　　")
    text = re.sub(r"(https?://\S+) ",r"<a href='\1' >\1</a>",text)
    text = re.sub(r"!Img:\"(.+)\"",r"<img src='\1'></a>",text)
    if len(re.findall(r"[ぁ-ンー0-9a-zA-Z一-鿿ｱ-ﾝ]+", text)) > 0:
        c = useful.count(f"BBS/{bbsname}/dat.json",data["Thread"])

        bbs_dat = useful.json_load(f"BBS/{bbsname}/dat.json")
        bbs_config = useful.json_load(f"BBS/{bbsname}/config.json")

        if name == "":
            name = "名無しさん@OSV-Nおめでとう"
        session["HN"] = name

        now = datetime.datetime.now()
        response = f"<a onclick='addAnker({c})'>{c}</a>:<b style='color:green'>{name}</b> {now.year}/{now.month}/{now.day} {now.hour}:{now.minute}:{now.second}.{now.microsecond} ID:{session.get('ID','???')}<br>　　{text}<br><br>\n"
        bbs_dat[data["Thread"]]["dat"].append(response)
        useful.json_write(bbs_dat,f"BBS/{bbsname}/dat.json")
        useful.json_write(bbs_config,f"BBS/{bbsname}/config.json")
        sock.emit(f"Update-{bbsname}-{data['Thread']}","\n".join(bbs_dat[data["Thread"]]["dat"]))

@app.route("/Shop")


@app.route("/ssv")
def ssv():
    print(session.items())
    return str(session.items())


@app.route("/FileUP")
def FUP():
    return useful.fOpen("HTML/file.html")

@app.route("/File-Upload/", methods=["POST"])
def FUpload():
    f = request.files.get("File")
    a = f.filename.split(".")
    a.reverse()
    end_dot = a[0].lower()
    ids = useful.RandomID(12)
    fname = "File/"+ids+"."+end_dot
    f.save(fname)
    if end_dot in ["jpg","png","jpeg","gif","bmp"]:
        return f"コピペ:　　!Img:\"http://g2channel.dynv6.net/{fname}\""
    else:
        return f"ファイル:　　http://g2channel.dynv6.net/{fname}"
    
@app.route("/File/<fname>")
def files2(fname):
    return send_file("File/"+fname)


sock.run(app,"::",80,debug=True,allow_unsafe_werkzeug=True)