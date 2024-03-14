from flask import Flask
import json
import random
import string
def fOpen(fname):
    return open(fname, "r", 
                encoding="utf-8").read()


def fWrite(fname, data):
    open(fname, "w", 
                encoding="utf-8").write(data)


def fObject(fname,m):
    return open(fname, m, encoding="utf-8")


def BBS_base(bbs_id,bbs_name, bbs_description, Thread_List):

    bbs_ThreadList = []
    a = json_load(f"BBS/{bbs_id}/dat.json")
    for i in Thread_List:
        Thread_Title = i["Title"]
        Thread_ID = i["ID"]
        Thread_c = a[i["ID"]]["count"]
        bbs_ThreadList.append(f"<a href='/{bbs_id}/{Thread_ID}/'>{Thread_Title}({Thread_c})</a><br>")

    base = fOpen("HTML/bbs.html")
    base = base.replace("{{ BBS_Name }}", bbs_name)
    base = base.replace("{{ BBS_Description }}", bbs_description)
    base = base.replace("{{ ThreadList }}", "\n".join(bbs_ThreadList))
    return base

def Thread_base(bbs_name, Thread_Name):
    
    json_dat = json_load(f"bbs/{bbs_name}/dat.json")
    thread_title = json_dat[Thread_Name]["Title"]
    thread_dat = "\n".join(json_dat[Thread_Name]["dat"])

    base = fOpen("HTML/Thread.html")
    base = base.replace("{{ Thread_Title }}",thread_title)
    base = base.replace("{{ Thread_Dat }}",thread_dat)    
    base = base.replace("{{ BBS }}",bbs_name)
    base = base.replace("{{ Thread }}",Thread_Name)
    
    return base


def RandomID(length):
    return "".join(random.choices(string.ascii_letters+string.digits,k=length))


def json_load(fname):
    return json.load(fObject(fname,"r"))


def json_write(obj, fname):
   json.dump(obj, fObject(fname,"w"), ensure_ascii = False, indent=4)


def XSSGuard(text):
    return text.replace(">","≻").replace("<","≺")


def count(fname,key):
    jsons = json_load(fname)
    jsons[key]["count"] = str(int(jsons[key]["count"])+1)
    json_write(jsons,fname)
    return jsons[key]["count"]
