import os
from flask import Flask, request, session, redirect, send_file, make_response
from flask_socketio import SocketIO
from osvkit import useful, bootstrap
import datetime
import re


app = Flask(__name__)
app.secret_key = b"secret!"
sock = SocketIO(app)
bootstrap.Load_Bootstrap(app)
idhuriwake = []
@app.route("/")
def page_index():
    if not "ID" in list(session.keys()):
        session["ID"] = useful.RandomID(8)
        
    return useful.fOpen("HTML/index.html").replace("{{ BBSLIST }}", useful.fOpen("bbslist.txt"))


@app.route("/bbs/<bbsname>/")
def page_bbs(bbsname):
    if not "ID" in list(session.keys()):
        session["ID"] = useful.RandomID(8)
        
        
    bbs_config = useful.json_load(f"BBS/{bbsname}/config.json")
    bbs_dat = useful.json_load(f"BBS/{bbsname}/dat.json")
    thread = bbs_config["BBS_thread"]
    name = bbs_config["BBS_name"]
    desc = bbs_config["BBS_description"]
    if request.args.get("mode","new") == "old":
        thread.reverse()
        print(thread)
    
    if request.args.get("mode","new") == "res":
        tlist = []
        for i in thread:
            Thread_c = int(bbs_dat[i["ID"]]["count"])
            tlist.append({"Title":i["Title"],"Count":Thread_c,"ID":i["ID"]})
        sorted_list = sorted(tlist,key=lambda x: x["Count"])
        for j in sorted_list:
            del j["Count"]
        print(sorted_list)
        thread = sorted_list
    text = useful.BBS_base(bbsname, name, desc, thread).replace("{{ BBS }}",bbsname)

    return text


@app.route("/<bbsID>/<threadID>/")
def page_thread(bbsID,threadID):
    if not "ID" in list(session.keys()):
        session["ID"] = useful.RandomID(8)
        
    json_dat = useful.json_load(f"bbs/{bbsID}/dat.json")
    if session["ID"] in json_dat[threadID]["aku"]:
        return "アクセスできぬい"
    else:
        tex = useful.Thread_base(bbsID,threadID).replace("{{ HN }}",request.cookies.get("HN",""))
        if json_dat[threadID].get("Kakolog","0") == "1":
            tex = tex.replace("<!-- ThreadDG -->","<div class='fixed-top' style='height:5%; width:100%; color:white; background-color:red'>このスレはアーカイブされました</div>")
        return tex


@sock.on("Post_Thread")
def Post_Thread(data):
    bbsname = data["BBS"]

    title = useful.XSSGuard(data["Title"])
    name = useful.XSSGuard(data["Name"])
    text = useful.XSSGuard(data["Message"]).replace("\n","<br>　　")
    text = re.sub(r"(https?://\S+) ",r"<a href='\1' target='_blank'>\1</a>",text)
    text = re.sub(r"!Img:\"(.+)\"",r"<img src='\1'></a>",text)
    Thread_ID = useful.RandomID(12)
    
    bbs_dat = useful.json_load(f"BBS/{bbsname}/dat.json")
    bbs_config = useful.json_load(f"BBS/{bbsname}/config.json")

    bbs_config["BBS_thread"].append({"Title":title,"ID":Thread_ID})
    if not "ID" in list(session.keys()):
        session["ID"] = useful.RandomID(8)
    IDs = session.get("ID","???")
    if "!NoneID" in title or "!NoneID" in text:
        IDs = "とくめいさん"
    
    if "!EnableIP" in title or "!EnableIP" in text:
        IDs = request.remote_addr
    if "!EnableWatchoi" in title or "!EnableWatchoi" in text:
        IDs = f"{'-'.join(request.remote_addr.split(':')[0:3])}】"
        
    bbs_config["count"] = "1"
    if name == "":
        name = "名無しさん@OSV-Nおめでとう"
    session["HN"] = name
    bbs_dat[Thread_ID] = {"Title":title,"dat":[],"count":"1","aku":[]}
    now = datetime.datetime.now()
    response = f"<a onclick='addAnker(1)'>1</a>:<b style='color:green'>{name}</b> {now.year}/{now.month}/{now.day} {now.hour}:{now.minute}:{now.second}.{now.microsecond} ID:{IDs}<br>　　{text}<br><br>\n"
    bbs_dat[Thread_ID]["dat"].append(response)
    useful.json_write(bbs_dat,f"BBS/{bbsname}/dat.json")
    useful.json_write(bbs_config,f"BBS/{bbsname}/config.json")


@sock.on("Post")
def Post(data):
    bbsname = data["BBS"]

    bbs_dat = useful.json_load(f"BBS/{bbsname}/dat.json")
    global session
    if not "ID" in list(session.keys()):
        session["ID"] = useful.RandomID(8)
        
    name = useful.XSSGuard(data["Name"])
    text = useful.XSSGuard(data["Message"]).replace("\n","<br>　　")
    text = re.sub(r"(https?://\S+) ",r"<a href='\1' target='_blank'>\1</a>",text)
    text = re.sub(r"!Img:\"(.+)\"",r"<img src='\1'></a>",text)
    for i in re.findall(r"\!Number:\"([0-9]+)\"",text):
        if int(i)<=65 and len(re.findall(r"\!Number:\"([0-9]+)\"",text))<11:
            text = text.replace(f"!Number:\"{i}\"",f"<b style='color:red;'>{useful.RandomID(int(i))}</b>",1)
    akukin = re.findall(r"!aku:\"([0-9]+)\"",text)
    if len(akukin)>0:
        for i in akukin:
            i = int(i)
            aku_tex = bbs_dat[data["Thread"]]["dat"][i-1]
            id = re.findall(r"ID:[a-zA-Z0-9]{8}",aku_tex)
            if len(bbs_dat[data["Thread"]]["aku"]) < 10:
                bbs_dat[data["Thread"]]["aku"].append(id[0].replace("ID:",""))  
                text+=f"<br>　　<font color='red'>★アク禁:≻≻{i}</font>"
            else:
                text+=f"<br>　　<font color='red'>★アク禁:失敗(10人以上アク禁はできぬ)</font>"

    
    kaijo = re.findall(r"!kaijo:\"([0-9]+)\"",text)
    if len(kaijo)>0:
        for i in kaijo:
            i = int(i)
            kaijo_tex = bbs_dat[data["Thread"]]["dat"][i-1]
            id = re.findall(r"ID:[a-zA-Z0-9]{8}",kaijo_tex)
            akl = bbs_dat[data["Thread"]]["aku"]
            try:
                del bbs_dat[data["Thread"]]["aku"][akl.index(id[0].replace("ID:",""))] 
                text+=f"<br>　　<font color='blue'>★アク禁解除:≻≻{i}</font>"
            except:
                text+=f"<br>　　<font color='red'>★エラー</font>"

    IDs = session.get('ID','???')
    aku=not IDs in bbs_dat[data["Thread"]]["aku"]
    if "!NoneID" in bbs_dat[data["Thread"]]["Title"] or "!NoneID" in bbs_dat[data["Thread"]]["dat"][0]:
        IDs = "とくめいさん"
        aku = False
    if "!EnableIP" in bbs_dat[data["Thread"]]["Title"] or "!EnableIP" in bbs_dat[data["Thread"]]["dat"][0]:
        IDs = request.remote_addr
        aku = not IDs in bbs_dat[data["Thread"]]["aku"]

    if "!EnableWatchoi" in bbs_dat[data["Thread"]]["Title"] or "!EnableWatchoi" in bbs_dat[data["Thread"]]["dat"][0]:
        IDs = f"{'-'.join(request.remote_addr.split(':')[0:3])}"
        aku = not IDs in bbs_dat[data["Thread"]]["aku"]

    
    if len(re.findall(r"[ぁ-ンー0-9a-zA-Z一-鿿ｱ-ﾝ]+", text)) > 0 and aku and bbs_dat[data["Thread"]].get("Kakolog","0") == "0":
        c, bbs_dat = useful.count(bbs_dat,data["Thread"])

        bbs_config = useful.json_load(f"BBS/{bbsname}/config.json")

        if name == "":
            name = "名無しさん"
        if name == "!session":
            name = request.cookies.get("HN","<font color='red'>名前のCookieがありません</font>")

        now = datetime.datetime.now()
        response = f"<a onclick='addAnker({c})'>{c}</a>:<b style='color:green'>{name}</b> {now.year}/{now.month}/{now.day} {now.hour}:{now.minute}:{now.second} ID:{IDs}<br>　　{text}<br><br>\n"
        bbs_dat[data["Thread"]]["dat"].append(response)
        useful.json_write(bbs_dat,f"BBS/{bbsname}/dat.json")
        useful.json_write(bbs_config,f"BBS/{bbsname}/config.json")
        log = useful.fOpen("UsersLog.dat")
        useful.fWrite("UsersLog.dat",log+f"{request.remote_addr} {now.year}/{now.month}/{now.day} {now.hour}:{now.minute}:{now.second} "+text.replace('<br>　　','\\n')+"\n")
        sock.emit(f"Update-{bbsname}-{data['Thread']}","\n".join(bbs_dat[data["Thread"]]["dat"]))


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


@app.route("/Name-Set", methods=["GET","POST"])
def page_nameset():
    if request.method == "GET":
        return useful.fOpen("HTML/Name.html")
    else:
        resp = make_response(useful.fOpen("HTML/Name.html"))
        resp.set_cookie("HN",request.form.get("Name","名無し"))
        return resp

@app.route("/Admin/News", methods=["GET","POST"])
def page_News():
    if request.method == "GET":
        return useful.fOpen("HTML/News.html")
    else:
        sock.emit("News",request.form.get("Text"))
        return useful.fOpen("HTML/News.html")


@app.route("/favicon.ico")
def favicon():
    return send_file("favicon.ico")


@app.route("/BBSMake",methods=["POST"])
def BBSMake():
    id = useful.XSSGuard(request.form.get("BBS_ID"))
    name = useful.XSSGuard(request.form.get("BBS_NAME"))
    text = request.form.get("BBS_DESC")
    if os.path.exists(f"BBS/{id}"):
        return "掲示板IDがかぶっています"
    else:
        os.mkdir(f"BBS/{id}")
        x = {
            "BBS_name": name,
            "BBS_description": text,
            "BBS_thread": []
        }
        useful.json_write(x,f"BBS/{id}/config.json")
        x = {
        }
        useful.json_write(x,f"BBS/{id}/dat.json")
        open("bbslist.txt","a",encoding="Utf-8").write(f"<a href='bbs/{id}/'>{name}</a>\n")
        return redirect(f"/bbs/{id}/")


@sock.on("ResDelete")
def ResDelete(data:dict):
    IDs = session["ID"]
    bbs_dat = useful.json_load(f"BBS/{data['BBS']}/dat.json")
    text = bbs_dat[data["Thread"]]["dat"][int(data.get("Number","1"))-1]
    
    if len(re.findall(r"ID:[a-zA-Z0-9]{8}",text))>0:
        if re.findall(r"ID:[a-zA-Z0-9]{8}",text)[0] == "ID:"+IDs:
            text = re.sub(r"(<a onclick='addAnker\([0-9]+\)'>[0-9]+</a>:<b style='color:green'>.+</b> [0-9]+/[0-9]+/[0-9]+ [0-9]+:[0-9]+:[0-9]+ ID:[a-zA-Z0-9]{8})<br>　　.+<br><br>\n",r"\1<br>　　<font color='red'>投稿者により削除されました</font><br><br>\n",text)
            bbs_dat[data["Thread"]]["dat"][int(data.get("Number","0"))-1] = text
            useful.json_write(bbs_dat,f"BBS/{data['BBS']}/dat.json")
            sock.emit(f"Update-{data['BBS']}-{data['Thread']}","\n".join(bbs_dat[data["Thread"]]["dat"]))


print(os.system("ipconfig"))
sock.run(app,"2001:268:d6b4:8bf3:fc43:bfaf:c558:a194",80,debug=True,use_reloader=True,allow_unsafe_werkzeug=True)
