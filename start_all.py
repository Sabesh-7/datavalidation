import os
import sys
import subprocess
import time
import webbrowser

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(base_dir, "backend")
    frontend_dir = os.path.join(base_dir, "frontend")

    print("=====================================================================")
    print("  MoSPI Household Survey Division (HSD) Data Validation Platform")
    print("=====================================================================")

    # Check venv python executable
    venv_python = os.path.join(backend_dir, ".venv", "Scripts", "python.exe")
    if not os.path.exists(venv_python):
        venv_python = sys.executable

    print("\n[1/2] Starting Python Backend on http://localhost:8005 ...")
    backend_cmd = [venv_python, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005"]
    backend_proc = subprocess.Popen(backend_cmd, cwd=backend_dir)

    time.sleep(2)

    print("[2/2] Starting React Frontend on http://localhost:5173 ...")
    npm_bin = "npm.cmd" if os.name == 'nt' else "npm"
    frontend_cmd = [npm_bin, "run", "dev"]
    frontend_proc = subprocess.Popen(frontend_cmd, cwd=frontend_dir)

    print("\n=====================================================================")
    print("  SUCCESS: Both Backend and Frontend are running!")
    print("  - Backend API: http://localhost:8005 (Docs: http://localhost:8005/docs)")
    print("  - Frontend UI:  http://localhost:5173")
    print("  Press Ctrl+C to stop both servers.")
    print("=====================================================================\n")

    try:
        webbrowser.open("http://localhost:5173")
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\nStopping servers...")
        backend_proc.terminate()
        frontend_proc.terminate()

if __name__ == "__main__":
    main()
