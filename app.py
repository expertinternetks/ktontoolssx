from flask import Flask
import FacebookAutomation

app = Flask(__name__)

@app.route("/")
def run_script():
    FacebookAutomation.main()  # funksioni kryesor i script-it
    return "Script u ekzekutua!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
