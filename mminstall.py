import os
import requests
import zipfile
import shutil
import winreg
import tkinter as tk
from tkinter import messagebox

# Function to get the latest release version from GitHub
def get_latest_release_version():
    latest_release_url = 'https://github.com/scp222thj/MalumMenu/releases/latest'
    response = requests.get(latest_release_url, allow_redirects=False)
    
    # Extract the version from the redirect URL
    if 'Location' in response.headers:
        location = response.headers['Location']
        version = location.split('/')[-1]
        return version
    else:
        raise Exception("No release version found")

# Function to download the latest release
def download_release(version, output_path):
    download_url = f'https://github.com/scp222thj/MalumMenu/releases/download/{version}/MalumMenu-{version[1:]}.zip'
    response = requests.get(download_url, stream=True)
    with open(output_path, 'wb') as file:
        shutil.copyfileobj(response.raw, file)
    return output_path

# Function to unzip the downloaded release
def unzip_file(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

# Function to find Among Us installation directory from the Windows registry
def find_among_us_installation():
    try:
        registry_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path)
        for i in range(winreg.QueryInfoKey(key)[0]):
            subkey_name = winreg.EnumKey(key, i)
            subkey = winreg.OpenKey(key, subkey_name)
            try:
                display_name = winreg.QueryValueEx(subkey, 'DisplayName')[0]
                if display_name == 'Among Us':
                    install_location = winreg.QueryValueEx(subkey, 'InstallLocation')[0]
                    among_us_exe = os.path.join(install_location, 'Among Us.exe')
                    if os.path.isfile(among_us_exe):
                        return install_location
            except FileNotFoundError:
                continue
    except Exception as e:
        print(f"An error occurred while searching the registry: {e}")
    return None

# Function to copy files with a single overwrite confirmation
def copy_files_with_single_confirmation(src_dir, dst_dir):
    # Check if any files need to be overwritten
    files_to_overwrite = []
    for item in os.listdir(src_dir):
        s = os.path.join(src_dir, item)
        d = os.path.join(dst_dir, item)
        if os.path.exists(d):
            files_to_overwrite.append(d)

    if files_to_overwrite:
        overwrite_all = messagebox.askyesno("Overwrite Confirmation",
                                            f"{len(files_to_overwrite)} files/folders already exist. Overwrite all?")
        if not overwrite_all:
            return  # User chose not to overwrite any files

    # Proceed with copying files
    for item in os.listdir(src_dir):
        s = os.path.join(src_dir, item)
        d = os.path.join(dst_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

def main():
    try:
        version = get_latest_release_version()
        print(f"Latest release version: {version}")

        zip_path = download_release(version, 'latest_release.zip')
        print(f"Downloaded latest release to {zip_path}")

        extract_to = 'malum_menu'
        unzip_file(zip_path, extract_to)
        print(f"Extracted to {extract_to}")

        among_us_dir = find_among_us_installation()
        if among_us_dir:
            print(f"Found Among Us installation at: {among_us_dir}")
            copy_files_with_single_confirmation(extract_to, among_us_dir)
            print(f"Copied files to {among_us_dir}")
        else:
            print("Could not find Among Us installation directory automatically.")

        # Clean up
        os.remove(zip_path)
        shutil.rmtree(extract_to)
        print("Cleaned up temporary files.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
