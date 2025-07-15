import subprocess

def run_whisper_server():
    subprocess.run([
        "uvicorn", "faster_whisper_server.main:create_app",
        "--host", "0.0.0.0",
        "--port", "9000",
        "--factory"
    ])

if __name__ == "__main__":
    run_whisper_server()
