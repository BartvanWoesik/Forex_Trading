#!/usr/bin/env python

import subprocess
import sys

def activate_conda_environment(conda_env):
    activate_script = f"conda activate {conda_env}"
    activate_cmd = activate_script.split()
    subprocess.call(activate_cmd)

def run_hook():
    # Your hook script code goes here
    print("Hook script is running...")

if __name__ == "__main__":
    # Name of your conda environment
    conda_env = "trading2"
    
    # Activate conda environment
    activate_conda_environment(conda_env)
    
    # Run your hook
    run_hook()
