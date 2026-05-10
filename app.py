from flask import Flask, jsonify, render_template_string
import os
import socket
import time

app = Flask(__name__)


def _mask(s: str, keep_last: int = 4) -> str:
    if not s:
        return ""
    if len(s) <= keep_last:
        return "*" * len(s)
    return ("*" * (len(s) - keep_last)) + s[-keep_last:]


PAGE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Flask AWS Monitor</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
      body { background: #0b1220; color: #e8eefc; }
      .card { background: #0f1a33; border: 1px solid rgba(255,255,255,.08); }
      .muted { color: rgba(232,238,252,.75); }
      code { color: #d9b8ff; }
      .badge-ok { background: #1f8a4c; }
      .badge-warn { background: #b7791f; }
    </style>
  </head>
  <body>
    <div class="container py-4">
      <div class="d-flex align-items-center justify-content-between mb-3">
        <div>
          <h1 class="h3 mb-1">Flask AWS Monitor</h1>
          <div class="muted">Kubernetes/Helm demo dashboard</div>
        </div>
        <div class="text-end">
          <div class="muted small">Server time</div>
          <div class="fw-semibold">{{ now }}</div>
        </div>
      </div>

      <div class="row g-3">
        <div class="col-md-6">
          <div class="card p-3 h-100">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <div class="fw-semibold">Runtime</div>
              <span class="badge {{ 'badge-ok' if health_ok else 'badge-warn' }}">
                {{ 'Healthy' if health_ok else 'Degraded' }}
              </span>
            </div>
            <div class="muted">Pod/Container</div>
            <div><span class="muted">Hostname:</span> <code>{{ hostname }}</code></div>
            <div><span class="muted">IP:</span> <code>{{ ip }}</code></div>
            <div class="mt-3">
              <a class="btn btn-sm btn-outline-light" href="/api/status">View JSON status</a>
              <a class="btn btn-sm btn-outline-light" href="/healthz">Health check</a>
            </div>
          </div>
        </div>

        <div class="col-md-6">
          <div class="card p-3 h-100">
            <div class="fw-semibold mb-2">AWS Environment Variables</div>
            <div class="muted small mb-2">For the assignment, Helm injects these into the container.</div>

            <div class="d-flex justify-content-between">
              <div><span class="muted">AWS_ACCESS_KEY_ID</span></div>
              <div>
                {% if aws_access_key_id %}
                  <code>{{ aws_access_key_id_masked }}</code>
                {% else %}
                  <span class="badge badge-warn">Not set</span>
                {% endif %}
              </div>
            </div>

            <div class="d-flex justify-content-between mt-2">
              <div><span class="muted">AWS_SECRET_ACCESS_KEY</span></div>
              <div>
                {% if aws_secret_access_key %}
                  <code>{{ aws_secret_access_key_masked }}</code>
                {% else %}
                  <span class="badge badge-warn">Not set</span>
                {% endif %}
              </div>
            </div>

            <div class="mt-3 muted small">
              Tip: set them via <code>helm upgrade --set aws.accessKey=... --set aws.secretKey=...</code>
            </div>
          </div>
        </div>
      </div>

      <div class="mt-4 muted small">
        Assignment check: app is listening on <code>:5001</code> and served through a Kubernetes Service.
      </div>
    </div>
  </body>
</html>
"""


@app.get("/")
def home():
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    return render_template_string(
        PAGE,
        now=time.strftime("%Y-%m-%d %H:%M:%S"),
        hostname=hostname,
        ip=ip,
        health_ok=True,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_access_key_id_masked=_mask(aws_access_key_id),
        aws_secret_access_key_masked=_mask(aws_secret_access_key),
    )


@app.get("/healthz")
def healthz():
    return "ok", 200


@app.get("/api/status")
def api_status():
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    return jsonify(
        {
            "ok": True,
            "hostname": socket.gethostname(),
            "aws_access_key_id_set": bool(aws_access_key_id),
            "aws_secret_access_key_set": bool(aws_secret_access_key),
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
