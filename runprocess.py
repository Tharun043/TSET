import subprocess,time

# Define the paths to the two Python scripts
script_1 = "no_mail_alert_check.py"
script_2 = "navigate_mentor.py"
script_3 = "navigate_mentee.py"



# Run the scripts using subprocess
try:
    # Run the first script
    process1 = subprocess.Popen(["python", script_1])
    process1.wait()  # Wait for the first script to finish
    print(f"{script_1} execution completed.")

    # Run the second script
    process2 = subprocess.Popen(["python", script_2])
    process2.wait()  # Wait for the second script to finish
    print(f"{script_2} execution completed.")

    # Delay before running the third script
    time.sleep(10)

    # Run the third script
    process3 = subprocess.Popen(["python", script_3])
    process3.wait()  # Wait for the third script to finish
    print(f"{script_3} execution completed.")

    print("All scripts finished execution.")
except Exception as e:
    print(f"An error occurred: {e}")
