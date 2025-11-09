from flask import Flask, jsonify
import mysql.connector

app = Flask(__name__)

def get_mysql_time():
    conn = mysql.connector.connect(
        host="localhost",
        user="raccoon",
        password="raccoonmaster",
        database="lemppadb"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT NOW();")
    mysql_time = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return str(mysql_time)

@app.route('/')
def home():
    return """
    <html>
        <head>
            <title>RaccoonSQL</title>
            <script>
                async function updateTime() {
                    let r = await fetch('/time');
                    let data = await r.json();
                    document.getElementById('clock').innerText = data.time;
                }
                setInterval(updateTime, 1000);  // Päivitä 1 sek välein
                window.onload = updateTime;
            </script>
        </head>
        <body style="font-family:Arial; background-color:#f3f3f3; color:#333; text-align:center;">
            <h1>RaccoonSQL -server</h1>
            <h2>SQL-palvelimen kellonaika:</h2>
            <p id="clock" style="font-size:1.5em; color:darkblue;">Ladataan...</p>
            <footer style="margin-top:50px;">
                <em>Dude! Raccoons just rock!</em>
            </footer>
        </body>
    </html>
    """

@app.route('/time')
def time():
    return jsonify({'time': get_mysql_time()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

