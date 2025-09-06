# pipeline/notifier.py
import os, base64, mimetypes, msal, requests

CACHE_PATH = ".msal_cache.json"

def _load_cache():
    cache = msal.SerializableTokenCache()
    if os.path.exists(CACHE_PATH):
        cache.deserialize(open(CACHE_PATH, "r", encoding="utf-8").read())
    return cache

def _save_cache(cache):
    if cache.has_state_changed:
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            f.write(cache.serialize())

def _get_token(client_id, authority, scopes):
    cache = _load_cache()
    app = msal.PublicClientApplication(client_id=client_id, authority=authority, token_cache=cache)
    result = app.acquire_token_silent(scopes, account=None)
    if not result:
        flow = app.initiate_device_flow(scopes=scopes)
        print("\nGo to:", flow["verification_uri"])
        print("Code:", flow["user_code"])
        result = app.acquire_token_by_device_flow(flow)
    _save_cache(cache)
    if "access_token" not in result:
        raise RuntimeError(f"Auth failed: {result}")
    return result["access_token"]

def _make_attachment(path):
    with open(path, "rb") as f:
        data = f.read()
    ctype, _ = mimetypes.guess_type(path)
    return {
        "@odata.type": "#microsoft.graph.fileAttachment",
        "name": os.path.basename(path),
        "contentType": ctype or "application/octet-stream",
        "contentBytes": base64.b64encode(data).decode("utf-8"),
    }

def send_email_graph(cfg):
    mail = cfg.get("email", {})
    if not mail.get("enabled"): 
        print("Email disabled."); return
    if mail.get("method", "graph").lower() != "graph":
        print("Not using Graph."); return

    token = _get_token(
        mail["graph_client_id"],
        mail.get("graph_authority", "https://login.microsoftonline.com/consumers"),
        ["Mail.Send"]
    )
    msg = {
        "message": {
            "subject": mail.get("subject", "Compliance KPIs"),
            "body": {"contentType": "Text", "content": mail.get("body", "See attachment.")},
            "toRecipients": [{"emailAddress": {"address": r}} for r in mail.get("to", [])],
            "attachments": [_make_attachment(p) for p in mail.get("attach", []) if os.path.exists(p)],
        },
        "saveToSentItems": True,
    }
    r = requests.post(
        "https://graph.microsoft.com/v1.0/me/sendMail",
        headers={"Authorization": f"Bearer {token}"},
        json=msg, timeout=30
    )
    print("✅ Email sent!" if r.status_code == 202 else f"❌ Error: {r.status_code} {r.text}")
