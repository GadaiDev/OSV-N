from flask import Flask, send_file

def bs_js(fname):
    return send_file(f"Static/bootstrap-5.3.0-dist/js/{fname}")


def bs_css(fname):
    return send_file(f"Static/bootstrap-5.3.0-dist/css/{fname}")


def Load_Bootstrap(app:Flask):   
    app.add_url_rule("/Bootstrap/js/<fname>",view_func=bs_js)
    app.add_url_rule("/Bootstrap/css/<fname>",view_func=bs_css)
    