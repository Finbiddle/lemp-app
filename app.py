# Flask app for raccoon-powered SQL service
from flask import Flask, jsonify
import mysql.connector
import subprocess
import os

app = Flask(__name__)

DB_CONFIG = {
    "host": "localhost",
    "user": "raccoon",
    "password": "raccoonmaster",
    "database": "lemppadb",
}

MAX_COMMITS = 5

def get_mysql_time():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT NOW();")
    (now_val,) = cursor.fetchone()
    cursor.close()
    conn.close()
    return str(now_val)


def get_git_commits():
    try:
        repo_path = os.path.dirname(os.path.abspath(__file__))

        # Muoto: hash|message|date (YYYY-MM-DD)
        output = subprocess.check_output(
            [
                "git",
                "-C",
                repo_path,
                "log",
                f"-{MAX_COMMITS}",
                "--pretty=format:%h|%s|%ad",
                "--date=short",
            ],
            stderr=subprocess.STDOUT,
        ).decode("utf-8", errors="replace")

        commits = []
        for line in output.strip().splitlines():
            parts = line.split("|", 2)
            if len(parts) == 3:
                commit_hash, msg, date = parts
                commits.append(
                    {
                        "hash": commit_hash.strip(),
                        "msg": msg.strip(),
                        "date": date.strip(),
                    }
                )
        return commits
    except Exception:
        return []


@app.route("/")
def home():
    commits = get_git_commits()

    if commits:
        commits_rows = "".join(
            f"<tr>"
            f"<td>{c['hash']}</td>"
            f"<td>{c['msg']}</td>"
            f"<td>{c['date']}</td>"
            f"</tr>"
            for c in commits
        )
    else:
        commits_rows = (
            "<tr><td colspan='3' style='color:#777;'>"
            "Ei committeja löytynyt (tai git ei käytettävissä palvelimella)"
            "</td></tr>"
        )

    return f"""
    <html>
      <head>
        <meta charset="utf-8">
        <title>RaccoonSQL -server</title>
        <style>
          body {{
            font-family: Arial, sans-serif;
            background-color: #f9f9f9;
            color: #333;
            text-align: center;
          }}
          h1 {{
            margin-top: 40px;
            font-size: 2.5em;
          }}
          h2 {{
            margin-top: 10px;
            font-size: 1.5em;
          }}
          #clock {{
            font-size: 2em;
            color: #204ecf;
            margin: 20px 0 40px 0;
          }}
          table {{
            margin: 0 auto;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 0.9em;
          }}
          th, td {{
            border: 1px solid #ddd;
            padding: 6px 10px;
          }}
          th {{
            background-color: #eee;
          }}
          footer {{
            margin-top: 40px;
            font-size: 0.85em;
            color: #777;
          }}
          a {{
            color: #204ecf;
            text-decoration: none;
          }}
          a:hover {{
            text-decoration: underline;
          }}
        </style>
        <script>
          async function updateTime() {{
            try {{
              const r = await fetch('/time');
              const data = await r.json();
              document.getElementById('clock').innerText = data.time;
            }} catch (e) {{
              document.getElementById('clock').innerText = 'Virhe kellon hakemisessa';
            }}
          }}
          setInterval(updateTime, 1000);
          window.onload = updateTime;
        </script>
      </head>
      <body>
        <h1>RaccoonSQL -server</h1>
        <h2>SQL-palvelimen kellonaika:</h2>
        <div id="clock">Ladataan...</div>

        <p style="font-style:italic; color:#666; margin-bottom:30px;">
          Dude! Raccoons just rock!
        </p>

        <hr style="width:60%; margin:30px auto;">

        <h2>Git-commithistoria</h2>
        <table>
          <tr>
            <th>Hash</th>
            <th>Viesti</th>
            <th>Päiväys</th>
          </tr>
          {commits_rows}
        </table>

        <footer>
          Palvelin: LEMPPARI-RaccoonServer 🦝
          <br>
          <span>Git käytössä: commitit luetaan suoraan palvelimen git-reposta.</span>
        </footer>
      </body>
    </html>
    """


@app.route("/time")
def time():
    return jsonify({"time": get_mysql_time()})


@app.route("/health")
def health():
    try:
        _ = get_mysql_time()
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

