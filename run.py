import subprocess
import os
import sys

def main():
    print("Starting Integration API on port 8000...")
    # Run uvicorn
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    api_proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "integration.main:app", "--port", "8000", "--host", "0.0.0.0", "--reload"], env=env)
    
    print("Starting Vite Frontend...")
    # Run npm run dev in frontend
    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    front_proc = subprocess.Popen([npm_cmd, "run", "dev"], cwd=frontend_dir)
    
    try:
        api_proc.wait()
        front_proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down Neural Nexus...")
        api_proc.terminate()
        front_proc.terminate()

if __name__ == "__main__":
    main()
