import os
import sys
import subprocess
import shutil

def get_python_executable():
    # Check current interpreter first
    try:
        res = subprocess.run([sys.executable, "-c", "import uvicorn, fastapi"], capture_output=True)
        if res.returncode == 0:
            return sys.executable
    except Exception:
        pass

    # Check known Python versions with dependencies
    candidates = [
        "/Library/Frameworks/Python.framework/Versions/3.13/bin/python3",
        "python3",
        "python",
    ]
    for cand in candidates:
        path = shutil.which(cand) or cand
        if os.path.exists(path):
            try:
                res = subprocess.run([path, "-c", "import uvicorn, fastapi"], capture_output=True)
                if res.returncode == 0:
                    return path
            except Exception:
                continue
    return sys.executable

def main():
    py_exec = get_python_executable()
    print(f"Using Python interpreter: {py_exec}")
    print("Starting Integration API on port 8000...")
    # Run uvicorn
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    api_proc = subprocess.Popen([py_exec, "-m", "uvicorn", "integration.main:app", "--port", "8000", "--host", "0.0.0.0", "--reload"], env=env)
    
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
