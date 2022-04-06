from flask import Flask, redirect, url_for, render_template, request

app = Flask(__name__)
app.debug = True


# @app.route('/<name>')
@app.route('/')
def home():
    return render_template('index.html')


@app.route("/submit_wiki_title", methods=["GET", "POST"])
def submit_wiki_title():
    if request.method == 'POST':
        wiki_title = request.form.get("wiki_title")
    elif request.method == "GET":
        wiki_title = request.args.get("wiki_title")

    if len(wiki_title) == 0:
        return {'message': "error!"}
    else:
        return {
            'message': "success!",
            'wiki_title': wiki_title,
        }


@app.route("/submit_language_code", methods=["GET", "POST"])
def submit_language_code():
    if request.method == "POST":
        language1 = request.form.get("language1")
        language2 = request.form.get("language2")
    if request.method == "GET":
        language1 = request.args.get("language1")
        language2 = request.args.get("language2")

    if len(language1) == 0 or len(language2) == 0:
        return {'message': "error!"}
    else:
        return {
            'message': 'success!',
            'language1': language1,
            'language2': language2
        }


if __name__ == '__main__':
    app.run()
    # host='127.0.0.1:5000/'
    # host='112.232.149.0/'
    # host='15189996915.zicp.vip'