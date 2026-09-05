"""
Deliberately vulnerable sample app - used ONLY as a scan target to prove out
the CI/CD security pipeline. Do not deploy this anywhere real.

Known intentional vulnerabilities (for pipeline validation / discussion):
  1. SQL injection in /user       - string-concatenated query (CWE-89)
  2. Command injection in /ping   - unsanitised shell call (CWE-78)
  3. Hardcoded secret             - fake API key below (for secrets-scan demo)
  4. Insecure deserialization     - pickle.loads on user input (CWE-502)
  5. Debug mode enabled           - Flask debug=True in prod-shaped entrypoint
"""

import os
import pickle
import sqlite3
import subprocess

from flask import Flask, request

app = Flask(__name__)

# --- (3) Intentional hardcoded secret for Gitleaks/secrets-scan demo ---------
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"  # noqa: intentional test fixture


def get_db():
    conn = sqlite3.connect("app.db")
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER, name TEXT)")
    return conn


@app.route("/user")
def get_user():
    # --- (1) SQL injection: user input concatenated directly into query ---
    user_id = request.args.get("id", "")
    conn = get_db()
    query = "SELECT id, name FROM users WHERE id = '" + user_id + "'"
    cursor = conn.execute(query)
    return {"rows": cursor.fetchall()}


@app.route("/ping")
def ping():
    # --- (2) Command injection: host passed straight to the shell ---------
    host = request.args.get("host", "127.0.0.1")
    result = subprocess.run(f"ping -c 1 {host}", shell=True, capture_output=True)
    return result.stdout


@app.route("/load-session", methods=["POST"])
def load_session():
    # --- (4) Insecure deserialization of untrusted input -------------------
    data = request.get_data()
    session = pickle.loads(data)
    return {"session": str(session)}


if __name__ == "__main__":
    # --- (5) Debug mode should never be on in a shipped entrypoint ---------
    app.run(host="0.0.0.0", port=5000, debug=True)
