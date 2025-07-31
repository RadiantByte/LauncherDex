#!/usr/bin/env python3
"""
DEX Modifier Script
Removes specified classes from launcher.dex and rebuilds it with remaining classes.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

# Classes to remove from the DEX file
CLASSES_TO_REMOVE = [
    'com/mojang/minecraftpe/MainActivity',
    'com/mojang/minecraftpe/FilePickerManagerHandler', 
    'com/mojang/minecraftpe/store/ExtraLicenseResponseData',
    'com/mojang/minecraftpe/store/Product',
    'com/mojang/minecraftpe/store/Purchase',
    'com/mojang/minecraftpe/store/Store',
    'com/mojang/minecraftpe/store/StoreListener'
]

def find_android_sdk():
    """Find Android SDK path from environment or common locations."""
    android_home = os.environ.get('ANDROID_HOME')
    if android_home and os.path.exists(android_home):
        return android_home
    
    # Common locations
    common_paths = [
        os.path.expanduser('~/AppData/Local/Android/Sdk'),  # Windows
        os.path.expanduser('~/Android/Sdk'),  # Linux
        os.path.expanduser('~/Library/Android/sdk'),  # macOS
        '/c/Users/*/AppData/Local/Android/Sdk'  # Git Bash Windows
    ]
    
    for path in common_paths:
        if '*' in path:
            # Handle wildcard paths
            import glob
            matches = glob.glob(path)
            if matches and os.path.exists(matches[0]):
                return matches[0]
        elif os.path.exists(path):
            return path
    
    return None

def find_build_tools(android_sdk):
    """Find the latest build-tools version."""
    build_tools_dir = os.path.join(android_sdk, 'build-tools')
    if not os.path.exists(build_tools_dir):
        return None
    
    versions = [d for d in os.listdir(build_tools_dir) 
                if os.path.isdir(os.path.join(build_tools_dir, d))]
    if not versions:
        return None
    
    # Sort versions and get the latest
    versions.sort(reverse=True)
    return os.path.join(build_tools_dir, versions[0])

def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, 
                              capture_output=True, text=True, check=True)
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {cmd}")
        print(f"Error: {e.stderr}")
        return None, e.stderr

def extract_classes_from_jar(jar_path, temp_dir, classes_to_keep):
    """Extract only the classes we want to keep from the JAR file."""
    print("Extracting classes from JAR...")

    # Extract all classes first
    extract_dir = os.path.join(temp_dir, 'extracted')
    os.makedirs(extract_dir, exist_ok=True)

    # Use absolute path for JAR file
    abs_jar_path = os.path.abspath(jar_path)
    stdout, stderr = run_command(f'jar xf "{abs_jar_path}"', cwd=extract_dir)
    if stdout is None:
        return False
    
    # Remove unwanted class files
    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            if file.endswith('.class'):
                file_path = os.path.join(root, file)
                # Get relative path from extracted directory
                rel_path = os.path.relpath(file_path, extract_dir)
                # Convert to forward slashes and remove .class extension
                class_name = rel_path.replace('\\', '/').replace('.class', '')
                
                if class_name in CLASSES_TO_REMOVE:
                    print(f"Removing class: {class_name}")
                    os.remove(file_path)
                else:
                    print(f"Keeping class: {class_name}")
    
    return extract_dir

def create_modified_jar(extract_dir, output_jar):
    """Create a new JAR file with the remaining classes."""
    print("Creating modified JAR...")
    
    # Create new JAR with remaining classes
    stdout, stderr = run_command(f'jar cf "{output_jar}" .', cwd=extract_dir)
    return stdout is not None

def convert_jar_to_dex(jar_path, dex_path, build_tools_path):
    """Convert JAR to DEX using Android build tools."""
    print("Converting JAR to DEX...")

    # Try d8 first (newer), then dx (older)
    d8_path = os.path.join(build_tools_path, 'd8.bat' if os.name == 'nt' else 'd8')
    dx_path = os.path.join(build_tools_path, 'dx.bat' if os.name == 'nt' else 'dx')

    # Use absolute paths
    abs_jar_path = os.path.abspath(jar_path)
    abs_dex_path = os.path.abspath(dex_path)

    if os.path.exists(d8_path):
        print("Using d8 tool...")
        temp_output_dir = os.path.dirname(abs_dex_path)
        stdout, stderr = run_command(f'"{d8_path}" --output "{temp_output_dir}" "{abs_jar_path}"')
        
        if stdout is not None:
            # d8 creates classes.dex, rename it
            classes_dex = os.path.join(temp_output_dir, 'classes.dex')
            if os.path.exists(classes_dex):
                shutil.move(classes_dex, abs_dex_path)
                return True

    elif os.path.exists(dx_path):
        print("Using dx tool...")
        stdout, stderr = run_command(f'"{dx_path}" --dex --output="{abs_dex_path}" "{abs_jar_path}"')
        return stdout is not None
    
    print("Error: Neither d8 nor dx tool found in build-tools")
    return False

def main():
    """Main function to modify the DEX file."""
    print("DEX Modifier - Removing specified classes from launcher.dex")
    print("=" * 60)
    
    # Check if launcher.dex exists
    dex_file = 'build/libs/launcher.dex'
    jar_file = 'build/libs/LeviLauncherDex-1.0.jar'
    
    if not os.path.exists(dex_file):
        print(f"Error: {dex_file} not found. Please build the project first.")
        return 1
    
    if not os.path.exists(jar_file):
        print(f"Error: {jar_file} not found. Please build the project first.")
        return 1
    
    # Find Android SDK
    android_sdk = find_android_sdk()
    if not android_sdk:
        print("Error: Android SDK not found. Please set ANDROID_HOME environment variable.")
        return 1
    
    print(f"Using Android SDK: {android_sdk}")
    
    # Find build tools
    build_tools_path = find_build_tools(android_sdk)
    if not build_tools_path:
        print("Error: Android build-tools not found.")
        return 1
    
    print(f"Using build-tools: {build_tools_path}")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Working in temporary directory: {temp_dir}")
        
        # Extract classes from JAR (removing unwanted ones)
        extract_dir = extract_classes_from_jar(jar_file, temp_dir, CLASSES_TO_REMOVE)
        if not extract_dir:
            print("Error: Failed to extract classes from JAR")
            return 1
        
        # Create modified JAR
        modified_jar = os.path.join(temp_dir, 'modified.jar')
        if not create_modified_jar(extract_dir, modified_jar):
            print("Error: Failed to create modified JAR")
            return 1
        
        # Convert to DEX
        modified_dex = 'build/libs/launcher_modified.dex'
        if not convert_jar_to_dex(modified_jar, modified_dex, build_tools_path):
            print("Error: Failed to convert JAR to DEX")
            return 1
        
        # Replace original DEX with modified one
        if os.path.exists(modified_dex):
            shutil.move(modified_dex, dex_file)
            print(f"\n✅ Successfully modified {dex_file}")
            print("Removed classes:")
            for class_name in CLASSES_TO_REMOVE:
                print(f"  - {class_name}")
            
            # Show file size
            size = os.path.getsize(dex_file)
            print(f"\nModified DEX file size: {size} bytes")
            
        else:
            print("Error: Modified DEX file was not created")
            return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
