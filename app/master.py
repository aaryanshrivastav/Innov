# app/run_stage3_master.py
import subprocess
import time

# List of Stage 2 scripts in the correct order
scripts = [
    "app\deploy.py",
    "app\mint_tokens.py",
    "app\set_outflow_cap.py",
    "app\burn_tokens.py",
    "app\read_data.py"
]

print("🎬 Starting Stage 3: Full Workflow Demo")

for script in scripts:
    print(f"\n➡️ Running {script} ...")
    try:
        result = subprocess.run(
            ["python", script],
            capture_output=True,
            text=True,
            check=True  # will raise CalledProcessError on failure
        )
        print(result.stdout)
        if result.stderr:
            print("⚠️ Script warning/error output:", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"❌ {script} failed with error:")
        print(e.stderr)
        # Optionally, break here to stop the sequence
        # break
    # Small delay for readability between scripts
    time.sleep(2)

print("\n🎉 Stage 3 Master Runner completed successfully!")
