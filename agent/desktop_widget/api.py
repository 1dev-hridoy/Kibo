import json
from urllib import request, error


class KiboAPI:
    def __init__(self, base_url):
        self.base = base_url.rstrip("/")
        self.token = None

    def _req(self, path, method="GET", data=None):
        url = f"{self.base}{path}"
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["X-Auth-Token"] = self.token
        body = json.dumps(data).encode() if data else None
        req = request.Request(url, data=body, headers=headers, method=method)
        try:
            with request.urlopen(req, timeout=3) as resp:
                return json.loads(resp.read().decode())
        except error.HTTPError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    def get_status(self):
        return self._req("/api/status")

    def get_model(self):
        return self._req("/api/model")

    def chat(self, message):
        return self._req("/api/chat", "POST", {"message": message})