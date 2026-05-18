# Create all the required files and folders
mkdir logs
mkdir config
mv logs/latest.log logs/old.log
touch logs/latest.log

# Create a virtual environment (venv)
python -m venv --system-site-packages ./.venv
echo "Installing Packages..."

# Install python packages into the venv
# ./.venv/bin/pip install numpy --upgrade
./.venv/bin/pip3 install lgpio pigpio gpio   # gpio pins
./.venv/bin/pip3 install gpiozero            # Button input
./.venv/bin/pip3 install hx711               # Load cell

# Start the program
echo "Done! Starting Program"
./.venv/bin/python3 ./src/main.py
