import json, os, hmac, hashlib, time, base64
import boto3

s3 = boto3.client("s3")
BUCKET = os.environ["MENU_BUCKET"]
MENU_KEY = os.environ.get("MENU_KEY", "data/menu.json")
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]
TOKEN_SECRET = os.environ["TOKEN_SECRET"].encode()
TOKEN_TTL = int(os.environ.get("TOKEN_TTL", "43200"))  # 12h


def resp(status, body, headers=None):
    # CORS is configured on the Function URL — do not set ACAO here (duplicates break browsers)
    h = {"Content-Type": "application/json"}
    if headers:
        h.update(headers)
    return {"statusCode": status, "headers": h, "body": json.dumps(body)}


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def sign_token(exp: int) -> str:
    payload = b64url(json.dumps({"exp": exp}).encode())
    sig = b64url(hmac.new(TOKEN_SECRET, payload.encode(), hashlib.sha256).digest())
    return f"{payload}.{sig}"


def verify_token(token: str) -> bool:
    try:
        payload, sig = token.split(".", 1)
        expect = b64url(hmac.new(TOKEN_SECRET, payload.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(sig, expect):
            return False
        pad = "=" * (-len(payload) % 4)
        data = json.loads(base64.urlsafe_b64decode(payload + pad))
        return int(data.get("exp", 0)) >= int(time.time())
    except Exception:
        return False


def auth_ok(event) -> bool:
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    auth = headers.get("authorization") or ""
    if auth.lower().startswith("bearer "):
        return verify_token(auth.split(" ", 1)[1].strip())
    return False


def get_menu():
    obj = s3.get_object(Bucket=BUCKET, Key=MENU_KEY)
    return json.loads(obj["Body"].read().decode())


def put_menu(data):
    body = json.dumps(data, indent=2).encode()
    s3.put_object(
        Bucket=BUCKET,
        Key=MENU_KEY,
        Body=body,
        ContentType="application/json; charset=utf-8",
        CacheControl="no-cache, max-age=0, must-revalidate",
    )
    dist = os.environ.get("CLOUDFRONT_DIST_ID")
    if dist:
        try:
            cf = boto3.client("cloudfront")
            cf.create_invalidation(
                DistributionId=dist,
                InvalidationBatch={
                    "Paths": {"Quantity": 2, "Items": ["/data/menu.json", "/data/*"]},
                    "CallerReference": f"menu-{int(time.time())}",
                },
            )
        except Exception as e:
            print("invalidation failed:", e)


def lambda_handler(event, context):
    method = (event.get("requestContext", {}).get("http", {}) or {}).get("method") or event.get("httpMethod") or "GET"
    path = (event.get("requestContext", {}).get("http", {}) or {}).get("path") or event.get("rawPath") or "/"
    if method == "OPTIONS":
        return resp(200, {"ok": True})

    # Normalize path
    path = path.rstrip("/") or "/"
    if path.endswith("/login"):
        route = "login"
    elif path.endswith("/menu"):
        route = "menu"
    elif path in ("", "/"):
        route = "health"
    else:
        route = path.split("/")[-1]

    try:
        if route == "health" and method == "GET":
            return resp(200, {"ok": True, "service": "mts-cms"})

        if route == "login" and method == "POST":
            body = json.loads(event.get("body") or "{}")
            if not hmac.compare_digest(str(body.get("password") or ""), ADMIN_PASSWORD):
                return resp(401, {"error": "Invalid password"})
            token = sign_token(int(time.time()) + TOKEN_TTL)
            return resp(200, {"token": token, "expiresIn": TOKEN_TTL})

        if route == "menu" and method == "GET":
            return resp(200, get_menu())

        if route == "menu" and method == "PUT":
            if not auth_ok(event):
                return resp(401, {"error": "Unauthorized"})
            data = json.loads(event.get("body") or "{}")
            if not isinstance(data, dict) or "categories" not in data:
                return resp(400, {"error": "Body must include categories"})
            put_menu(data)
            return resp(200, {"ok": True, "updatedAt": data.get("updatedAt")})

        return resp(404, {"error": "Not found"})
    except Exception as e:
        msg = str(e)
        if "NoSuchKey" in msg or "Not Found" in msg:
            if route == "menu" and method == "GET":
                return resp(200, {"categories": [], "updatedAt": None})
            return resp(404, {"error": "menu.json missing"})
        return resp(500, {"error": msg})
