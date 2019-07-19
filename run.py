from chatbot import app
from settings import HOST_NAME, HOST_PORT, DEBUG


# run Flask app
if __name__ == "__main__":
	app.run(host=HOST_NAME, port=HOST_PORT, debug=DEBUG)
