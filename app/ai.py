import sys
import subprocess


venv_python = sys.executable  # this ensures the venv Python is used

if __name__ == "__main__":
    try:
        input_value = int(float(sys.argv[1]))
        computed_value = input_value * 2  # Replace with real AI logic

        # Send computed value to set.py
        subprocess.run([venv_python, "app/set_outflow_cap.py", str(computed_value)], check=True)
        
    except Exception as e:
        print("❌ Error in ai.py:", e)
        sys.exit(1)
