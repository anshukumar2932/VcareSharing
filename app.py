from flask import Flask, render_template, redirect

app = Flask(__name__)

@app.route('/')
def entry():
    return render_template("index.html")  # Use render_template to serve HTML files

if __name__ == '__main__':
    app.run(debug=True)
