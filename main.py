from flask import Flask, request, render_template 
from werkzeug.utils import secure_filename
import requests
import json
app = Flask(__name__)

couchHost = "http://admin:password@127.0.0.1:5984/databasename"

def getLatestRevision(host, docid):
  req = requests.get(host + '/' + docid)
  resp = json.loads(req.text)
  if '_rev' in resp:
    revisionId = resp['_rev']
  else:
    revisionId = None
  return revisionId

@app.route("/")
def form():
  return render_template("form.html")

@app.route("/", methods=["POST"])
def process():
  shopName = request.form['shopname'].replace(' ', '')
  # post to couchbase to create doc id
  payload = {}
  payload['shopname'] = shopName
  payload['items'] = {}
  #Text items
  for item in request.form.items():
    print("Name: {} Value: {}".format(item[0], item[1]))
    payload['items'][item[0]] = item[1]

  #Put initial doc to Couchdb
  docid = shopName 
  revisionId = getLatestRevision(couchHost, docid)
  revision = '' if revisionId is None else "?rev=" + revisionId
  req = requests.put(couchHost + '/' + docid + revision, json=payload)
  # get revision id
  response = json.loads(req.text)
  revisionId = response['rev']
  
  # Submit Binary items as attachements
  for item in request.files: 
    file = request.files[item] #octec stream
    if file.filename != "":
      filename = secure_filename(file.filename)
      #files = {filename : file.read()}
      import pdb;pdb.set_trace()
      headers = {'Content-Type': file.mimetype}
      req = requests.put(couchHost + '/' + shopName + '/' + filename + '?rev=' + revisionId, data=file.read(),
            headers=headers)
      response = json.loads(req.text)
      revisionId = response['rev']
  return "ok"
