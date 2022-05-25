from flask import Flask
app = Flask(__name__)


@app.route("/")
def hello_world():
	print("swagswagswag")
	print(__name__)
	return "yo"


if __name__=="__main__":
	app.debug = True
	app.run()
