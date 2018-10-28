#!/bin/python
"""
This file defines the vulnerable server you will be attacking.
It uses Flask a Python Web Framework to easily setup a web server.
The minimal example in the Flask documentation
(http://flask.pocoo.org/docs/1.0/quickstart/) is more than enough to get you started.

If you have any doubts about certain function calls to imported
modules please refer to their respective documentation within the Python standard library.
"""

from flask import Flask, render_template, abort, request, make_response, url_for
import sqlite3
import xml.etree.ElementTree
import re
import time
import subprocess
import ipaddress

app = Flask(__name__)

# This defines the database the server will use.
USERS_XML = """<?xml version="1.0" encoding="utf-8"?>
<users>
    <user id="0">
        <username>admin</username>
        <name>admin</name>
        <surname>admin</surname>
        <password>7en8aiDoh!</password>
    </user>

    <user id="1">
        <username>dricci</username>
        <name>dian</name>
        <surname>ricci</surname>
        <password>12345</password>
    </user>

    <user id="2">
        <username>amason</username>
        <name>anthony</name>
        <surname>mason</surname>
        <password>gandalf</password>
    </user>
</users>
"""

def initDB():
    """
    Initializes an in-memory database.
    """
    global connection
    connection = sqlite3.connect(":memory:", isolation_level=None, check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE users(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, name TEXT, surname TEXT, password TEXT)")
    cursor.executemany("INSERT INTO users(id, username, name, surname, password) VALUES(NULL, ?, ?, ?, ?)",
                       ((_.findtext("username"),
                         _.findtext("name"),
                         _.findtext("surname"),
                         _.findtext("password"))
                        for _ in xml.etree.ElementTree.fromstring(USERS_XML).findall("user")))
    cursor.execute("CREATE TABLE comments(id INTEGER PRIMARY KEY AUTOINCREMENT, comment TEXT, time TEXT)")

@app.route('/')
def index():
    """
    The index page for the server.
    """
    return render_template('index.html')

@app.route('/command_injection/<level>')
def command_injection(level):
    ip = request.args.get('ip', default='')
    command = 'ping -c 3 '

    if 'low' == level:
        blacklist = []
    elif 'medium' == level:
        blacklist = ['&&', ';']
    elif 'high' == level:
        blacklist = ['&', '|', '$', '`', '&&', '||']
        ip = re.sub(r'\s+?', '', ip)
    elif 'impossible' == level:
        # Not vulnerable
        blacklist = []
        try:
            ip = ipaddress.ip_address(ip).__str__()
        except:
            ip = ''
    else:
        abort(404)

    command += ip

    for b in blacklist:
        command = command.replace(b, '')

    ret = subprocess.run(command, shell=True, stderr=subprocess.STDOUT, stdout = subprocess.PIPE)
    retlines = ret.stdout.splitlines()
    retlines = [ x.decode() for x in retlines ]

    return render_template('command_injection.html', command=command, result=retlines)

@app.route('/sql_injection/<level>/id/<id>')
def sql_injection(level, id):
    if 'low' == level:
        query = "SELECT id, username, name, surname FROM users WHERE id = '{}';".format(id)
    elif 'impossible' == level:
        # Not vulnerable.
        query = "SELECT id, username, name, surname FROM users WHERE id = ?"
    else:
        abort(404)

    cursor = connection.cursor()
    if 'impossible' == level:
        result_rows = cursor.execute(query, [id])
    else:
        result_rows = cursor.execute(query)

    row_list = [r for r in result_rows]

    return render_template('sql_injection.html', row_list=row_list)

@app.route('/xss/<vuln_type>/<level>')
def xss(vuln_type, level):
    content = ""
    cursor = connection.cursor()

    comment = request.args.get('comment', default='')

    if '1' == vuln_type:
        content += "<h3>The Reflected Kind</h3>\n"
        if 'low' == level:
            content += 'Comment:' + comment
        elif 'medium' == level:
            comment = comment.replace('<script>', '')
            content += 'Comment:' + comment
        elif 'high' == level:
            comment = re.sub(r'/<(.*)s(.*)c(.*)r(.*)i(.*)p(.*)t/i', '', comment)
            content += 'Comment:' + comment

    elif '2' == vuln_type:
        content += "<h3>The Stored Kind</h3>\n"

        if request.args.get('comment'):
            if 'low' == level:
                pass
            elif 'medium' == level:
                comment = comment.replace('<script>', '')
                comment = comment.replace('</script>', '')
            elif 'high' == level:
                comment = re.sub(r'/<[a-z]*>/i', '', comment)

            cursor.execute("INSERT INTO comments VALUES(NULL, '%s', '%s')" % (comment, time.ctime()))

        cursor.execute("SELECT id, comment, time FROM comments")
        content += "<div><span>Comment(s):</span></div><table><thead><th>id</th><th>comment</th><th>time</th></thead>%s</table>" % ("".join("<tr>%s</tr>" % "".join("<td>%s</td>" % ("-" if _ is None else _) for _ in row) for row in cursor.fetchall()))
        content += '<br/><a href="/xss/2" onclick="document.location=\'/xss/2?comment=\'+prompt(\'Please leave a coment\'); return false">Click Here to leave a comment</a>'
    elif '3' == vuln_type:
        content += "<h3>The DOM Kind</h3>\n"
        lang = request.args.get('lang', default='en')

        if 'low' == level:
            pass
        elif 'medium' == level:
            lang = 'en' if '<script' in lang else lang
        elif 'high' == level:
            lang = lang if lang in ['fr', 'en', 'es', 'de'] else 'en'


    resp = make_response(render_template('xss.html', body=content))
    resp.set_cookie('username', 'CookieMonster')

    # The passwords here are base64 encoded.
    if '1' == vuln_type:
        resp.set_cookie('password', 'TWUgd2FudCBjb29raWUh')
    elif '2' == vuln_type:
        resp.set_cookie('password', 'TWUgZWF0IGNvb2tpZSE=')
    elif '3' == vuln_type:
        resp.set_cookie('password', 'T20gbm9tIG5vbSBub20h')

    return resp

@app.route('/csrf_src')
def csrf_src():
    """
    You can use this endpoint to mount your CSRF attacks.
    """
    content = '<h3>Cross-Site Request Forgery Source</h3>\n'
    content += 'Query: ' + request.args.get('query', default='')

    return render_template('csrf.html', body=content)

@app.route('/csrf_target', defaults={'level':None})
@app.route('/csrf_target/<level>')
def csrf_target(level):
    """
    This is the target endpoint you will need to attack using CSRF.
    """
    content = '<h3>Cross-Site Request Forgery Target</h3>\n'
    cursor = connection.cursor()
    comment = request.args.get('comment', default='')

    if comment:
        if 'low' == level or not level:
            pass
        elif 'medium' == level:
            if 'csrf_target' not in request.referrer:
                abort(404)

        cursor.execute("INSERT INTO comments VALUES(NULL, '%s', '%s')" % (comment, time.ctime()))

    cursor.execute("SELECT id, comment, time FROM comments")
    content += "<div><span>Comment(s):</span></div><table><thead><th>id</th><th>comment</th><th>time</th></thead>%s</table>" % ("".join("<tr>%s</tr>" % "".join("<td>%s</td>" % ("-" if _ is None else _) for _ in row) for row in cursor.fetchall()))

    return render_template('csrf.html', body=content)


if __name__ == '__main__':
    initDB()
    app.run(port=1337)
