from app import app, handler

from flask import Flask, abort, request

from linebot.exceptions import InvalidSignatureError

@app.route("/callback", methods=["POST"])
def callback():

	signature = request.headers["X-Line-Signature"]

	body = request.get_data(as_text=True)
	app.logger.info("Request body: " + body)

	try:
		handler.handle(body, signature)
	except InvalidSignatureError:
		abort(400)

	return "OK"