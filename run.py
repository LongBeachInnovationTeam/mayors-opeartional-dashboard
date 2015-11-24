from app import app

# Run the test server
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=1337, debug=True)