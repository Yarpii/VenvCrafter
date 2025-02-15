#!/usr/bin/env python3
import os
import sys
import venv
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

BASE_DIR = Path.home() / "python_envs"
BORDER = "─" * 40

def clear_screen():
    os.system('clear')

def pause():
    input("\nPress Enter to continue...")

def print_header():
    clear_screen()
    print("╔════════════════════════════════════════════╗")
    print("║     Virtual Environment Manager v2.0       ║")
    print("║         For Debian-based Systems           ║")
    print("╚════════════════════════════════════════════╝\n")

def check_system():
    if not Path("/etc/debian_version").exists():
        print("Error: This script is only for Debian-based Linux systems.")
        sys.exit(1)

def ensure_base_dir():
    try:
        BASE_DIR.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        print(f"Error: No permission to create directory at {BASE_DIR}")
        sys.exit(1)

def get_available_envs():
    if not BASE_DIR.exists():
        return []
    return [d.name for d in BASE_DIR.iterdir() if d.is_dir()]

def select_environment(prompt):
    envs = get_available_envs()
    if not envs:
        print("\nNo virtual environments found.")
        pause()
        return None
    print("\nSelect environment:")
    print(BORDER)
    for idx, env in enumerate(envs, 1):
        print(f"  {idx}. {env}")
    print(BORDER)
    while True:
        choice = input(f"\n{prompt} (1-{len(envs)} or 'q' to cancel): ").strip()
        if choice.lower() == 'q':
            return None
        if choice.isdigit():
            num = int(choice)
            if 1 <= num <= len(envs):
                return envs[num - 1]
        print(f"Please enter a number between 1 and {len(envs)} or 'q' to cancel.")

def list_envs():
    envs = get_available_envs()
    if envs:
        print("\nAvailable environments:")
        print(BORDER)
        for idx, env in enumerate(envs, 1):
            print(f"  {idx}. {env}")
        print(BORDER)
    else:
        print("\nNo virtual environments found.")
    pause()

def create_env():
    print("\nCreate New Environment")
    print(BORDER)
    env_name = input("Enter environment name: ").strip()
    if not env_name:
        print("\nError: Invalid name provided.")
        pause()
        return
    env_path = BASE_DIR / env_name
    if env_path.exists():
        print(f"\nError: Environment '{env_name}' already exists.")
        pause()
        return
    print(f"\nCreating '{env_name}'...")
    try:
        venv.create(env_path, with_pip=True)
        subprocess.run([str(env_path / "bin" / "pip"), "install", "--upgrade", "pip", "--quiet"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"\nSuccess: Environment created at {env_path}")
    except Exception as e:
        print(f"\nError: {e}")
    pause()

def delete_env():
    env_name = select_environment("Choose environment to delete")
    if not env_name:
        return
    env_path = BASE_DIR / env_name
    confirmation = input(f"Are you sure you want to delete '{env_name}'? (y/N): ").strip().lower()
    if confirmation != 'y':
        print("Deletion cancelled.")
        pause()
        return
    try:
        shutil.rmtree(env_path)
        print(f"Environment '{env_name}' deleted successfully.")
    except Exception as e:
        print(f"Error: {e}")
    pause()

def rename_env():
    old_env = select_environment("Choose environment to rename")
    if not old_env:
        return
    new_name = input("Enter new name for the environment: ").strip()
    if not new_name:
        print("Error: Invalid name provided.")
        pause()
        return
    new_env_path = BASE_DIR / new_name
    if new_env_path.exists():
        print(f"Error: An environment named '{new_name}' already exists.")
        pause()
        return
    try:
        (BASE_DIR / old_env).rename(new_env_path)
        print(f"Environment '{old_env}' renamed to '{new_name}' successfully.")
    except Exception as e:
        print(f"Error: {e}")
    pause()

def clone_env():
    source_env = select_environment("Choose source environment to clone")
    if not source_env:
        return
    new_env_name = input("Enter new environment name: ").strip()
    if not new_env_name:
        print("Error: Invalid name provided.")
        pause()
        return
    new_env_path = BASE_DIR / new_env_name
    if new_env_path.exists():
        print(f"Error: Environment '{new_env_name}' already exists.")
        pause()
        return
    source_env_path = BASE_DIR / source_env
    source_pip = source_env_path / "bin" / "pip"
    if not source_pip.exists():
        print("Error: pip not found in the source environment.")
        pause()
        return
    try:
        result = subprocess.run([str(source_pip), "freeze"], capture_output=True, text=True)
        freeze_output = result.stdout.strip()
    except Exception as e:
        print(f"Error retrieving package list: {e}")
        pause()
        return
    print(f"\nCloning '{source_env}' to '{new_env_name}'...")
    try:
        venv.create(new_env_path, with_pip=True)
        new_pip = new_env_path / "bin" / "pip"
        subprocess.run([str(new_pip), "install", "--upgrade", "pip", "--quiet"],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if freeze_output:
            req_file = new_env_path / "requirements.txt"
            with req_file.open("w") as f:
                f.write(freeze_output)
            subprocess.run([str(new_pip), "install", "-r", str(req_file)])
            req_file.unlink()
        print(f"Environment '{new_env_name}' cloned successfully.")
    except Exception as e:
        print(f"Error during cloning: {e}")
    pause()

def activate_env():
    env_name = select_environment("Choose environment to activate")
    if not env_name:
        return
    env_path = BASE_DIR / env_name
    activate_script = env_path / "bin" / "activate"
    if not activate_script.exists():
        print("\nError: Activation script not found.")
        pause()
        return
    print("\nActivation Instructions")
    print(BORDER)
    print(f"Run this command to activate:\n\n  source {activate_script}\n")
    print("To deactivate later, run:\n  deactivate")
    print(BORDER)
    pause()

def run_command_in_env():
    env_name = select_environment("Choose environment to run command in")
    if not env_name:
        return
    command = input("Enter the command to run: ").strip()
    if not command:
        print("No command entered.")
        pause()
        return
    env_path = BASE_DIR / env_name
    new_env = os.environ.copy()
    new_env['PATH'] = f"{env_path / 'bin'}:" + new_env.get('PATH', '')
    try:
        subprocess.run(command, shell=True, env=new_env)
    except Exception as e:
        print(f"Error running command: {e}")
    pause()

def interactive_shell():
    env_name = select_environment("Choose environment for interactive shell")
    if not env_name:
        return
    env_path = BASE_DIR / env_name
    new_env = os.environ.copy()
    new_env['PATH'] = f"{env_path / 'bin'}:" + new_env.get('PATH', '')
    print(f"\nStarting interactive shell for '{env_name}'. Type 'exit' to return.")
    subprocess.run("/bin/bash", env=new_env, shell=True)
    pause()

def environment_details():
    env_name = select_environment("Choose environment to show details")
    if not env_name:
        return
    env_path = BASE_DIR / env_name
    try:
        ctime = os.path.getctime(env_path)
        creation_date = datetime.fromtimestamp(ctime).strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        creation_date = "Unknown"
    def get_dir_size(path):
        total = 0
        for p in path.rglob('*'):
            if p.is_file():
                try:
                    total += p.stat().st_size
                except Exception:
                    pass
        return total
    size_bytes = get_dir_size(env_path)
    pip_path = env_path / "bin" / "pip"
    num_packages = 0
    if pip_path.exists():
        try:
            result = subprocess.run([str(pip_path), "freeze"], capture_output=True, text=True)
            packages = result.stdout.strip().splitlines()
            num_packages = len(packages)
        except Exception:
            pass
    print(f"\nDetails for environment '{env_name}':")
    print(BORDER)
    print(f"Creation date   : {creation_date}")
    print(f"Size on disk   : {size_bytes} bytes")
    print(f"Installed pkgs : {num_packages}")
    print(BORDER)
    pause()

def install_packages():
    env_name = select_environment("Choose environment to install packages in")
    if not env_name:
        return
    env_path = BASE_DIR / env_name
    pip_path = env_path / "bin" / "pip"
    if not pip_path.exists():
        print("\nError: pip not found in the selected environment.")
        pause()
        return
    packages = input("Enter packages to install (separated by spaces): ").strip()
    if not packages:
        print("No packages entered.")
        pause()
        return
    package_list = packages.split()
    try:
        subprocess.run([str(pip_path), "install"] + package_list)
    except Exception as e:
        print(f"\nError: {e}")
    pause()

def list_installed_packages():
    env_name = select_environment("Choose environment to list packages")
    if not env_name:
        return
    env_path = BASE_DIR / env_name
    pip_path = env_path / "bin" / "pip"
    if not pip_path.exists():
        print("\nError: pip not found in the selected environment.")
        pause()
        return
    try:
        result = subprocess.run([str(pip_path), "freeze"], capture_output=True, text=True)
        packages = result.stdout.strip()
        if packages:
            print(f"\nInstalled packages in '{env_name}':")
            print(BORDER)
            print(packages)
            print(BORDER)
        else:
            print(f"\nNo packages found in '{env_name}'.")
    except Exception as e:
        print(f"\nError: {e}")
    pause()

def update_outdated():
    env_name = select_environment("Choose environment to update outdated packages")
    if not env_name:
        return
    env_path = BASE_DIR / env_name
    pip_path = env_path / "bin" / "pip"
    if not pip_path.exists():
        print("\nError: pip not found in the selected environment.")
        pause()
        return
    try:
        result = subprocess.run([str(pip_path), "list", "--outdated", "--format=columns"], capture_output=True, text=True)
        output = result.stdout.strip()
        if not output:
            print(f"\nNo outdated packages found in '{env_name}'.")
            pause()
            return
        print(f"\nOutdated packages in '{env_name}':")
        print(BORDER)
        print(output)
        print(BORDER)
        choice = input("Upgrade all outdated packages? (y/N): ").strip().lower()
        if choice == 'y':
            lines = output.splitlines()[2:]
            packages = []
            for line in lines:
                parts = line.split()
                if parts:
                    packages.append(parts[0])
            if packages:
                for pkg in packages:
                    print(f"Upgrading {pkg}...")
                    subprocess.run([str(pip_path), "install", "--upgrade", pkg])
                print("All outdated packages upgraded.")
        else:
            print("No packages were upgraded.")
    except Exception as e:
        print(f"\nError: {e}")
    pause()

def dependency_graph():
    env_name = select_environment("Choose environment to display dependency graph")
    if not env_name:
        return
    env_path = BASE_DIR / env_name
    pip_path = env_path / "bin" / "pip"
    if not pip_path.exists():
        print("\nError: pip not found in the selected environment.")
        pause()
        return
    try:
        result = subprocess.run([str(pip_path), "freeze"], capture_output=True, text=True)
        packages = result.stdout.strip().splitlines()
        if not packages:
            print(f"\nNo packages installed in '{env_name}'.")
            pause()
            return
        print(f"\nDependency graph for '{env_name}':")
        print(BORDER)
        for pkg_line in packages:
            pkg = pkg_line.split("==")[0]
            show_result = subprocess.run([str(pip_path), "show", pkg], capture_output=True, text=True)
            requires = "None"
            for line in show_result.stdout.splitlines():
                if line.startswith("Requires:"):
                    req = line.split(":", 1)[1].strip()
                    requires = req if req else "None"
                    break
            print(f"{pkg} -> {requires}")
        print(BORDER)
    except Exception as e:
        print(f"\nError: {e}")
    pause()

def backup_env():
    env_name = select_environment("Choose environment to backup")
    if not env_name:
        return
    env_path = BASE_DIR / env_name
    pip_path = env_path / "bin" / "pip"
    if not pip_path.exists():
        print("\nError: pip not found in the selected environment.")
        pause()
        return
    backup_file = input(f"Enter backup file path (default: {env_name}_backup.txt): ").strip()
    if not backup_file:
        backup_file = f"{env_name}_backup.txt"
    try:
        result = subprocess.run([str(pip_path), "freeze"], capture_output=True, text=True)
        with open(backup_file, "w") as f:
            f.write(result.stdout)
        print(f"\nBackup of '{env_name}' saved to {backup_file}.")
    except Exception as e:
        print(f"\nError: {e}")
    pause()

def restore_env():
    backup_file = input("Enter path to backup file: ").strip()
    if not backup_file or not Path(backup_file).exists():
        print("Backup file not found.")
        pause()
        return
    new_env_name = input("Enter new environment name to restore to: ").strip()
    if not new_env_name:
        print("Invalid environment name.")
        pause()
        return
    new_env_path = BASE_DIR / new_env_name
    if new_env_path.exists():
        print(f"Environment '{new_env_name}' already exists.")
        pause()
        return
    try:
        venv.create(new_env_path, with_pip=True)
        new_pip = new_env_path / "bin" / "pip"
        subprocess.run([str(new_pip), "install", "--upgrade", "pip", "--quiet"],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([str(new_pip), "install", "-r", backup_file])
        print(f"Environment '{new_env_name}' restored successfully from {backup_file}.")
    except Exception as e:
        print(f"Error: {e}")
    pause()

def package_env():
    env_name = select_environment("Choose environment to package")
    if not env_name:
        return
    default_tar = f"{env_name}.tar.gz"
    tarball = input(f"Enter output tarball name (default: {default_tar}): ").strip()
    if not tarball:
        tarball = default_tar
    try:
        subprocess.run(["tar", "-czf", tarball, "-C", str(BASE_DIR), env_name])
        print(f"Environment '{env_name}' packaged into {tarball}.")
    except Exception as e:
        print(f"Error: {e}")
    pause()

def search_envs():
    search_str = input("Enter search string: ").strip().lower()
    if not search_str:
        print("No search string provided.")
        pause()
        return
    envs = get_available_envs()
    matching = [env for env in envs if search_str in env.lower()]
    if matching:
        print("\nMatching environments:")
        print(BORDER)
        for env in matching:
            print(env)
        print(BORDER)
    else:
        print("No environments match the search string.")
    pause()

def custom_notes():
    env_name = select_environment("Choose environment to manage notes")
    if not env_name:
        return
    env_path = BASE_DIR / env_name
    notes_file = env_path / "notes.txt"
    print("\nCustom Notes")
    print(BORDER)
    if notes_file.exists():
        with notes_file.open("r") as f:
            content = f.read().strip()
        print("Current notes:")
        print(content if content else "No notes.")
    else:
        print("No notes found.")
    print(BORDER)
    print("Options:")
    print("1. Edit notes")
    print("2. Clear notes")
    print("3. Back")
    choice = input("Enter choice: ").strip()
    if choice == "1":
        new_notes = input("Enter new notes (will overwrite existing):\n")
        with notes_file.open("w") as f:
            f.write(new_notes)
        print("Notes updated.")
    elif choice == "2":
        if notes_file.exists():
            notes_file.unlink()
        print("Notes cleared.")
    pause()

def env_management_menu():
    while True:
        clear_screen()
        print("Environment Management")
        print(BORDER)
        print("1. List environments")
        print("2. Create environment")
        print("3. Delete environment")
        print("4. Rename environment")
        print("5. Clone environment")
        print("6. Back")
        print(BORDER)
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            list_envs()
        elif choice == "2":
            create_env()
        elif choice == "3":
            delete_env()
        elif choice == "4":
            rename_env()
        elif choice == "5":
            clone_env()
        elif choice == "6":
            break
        else:
            print("Invalid choice.")
            pause()

def env_interaction_menu():
    while True:
        clear_screen()
        print("Environment Interaction")
        print(BORDER)
        print("1. Activate environment (instructions)")
        print("2. Run command in environment")
        print("3. Interactive shell in environment")
        print("4. Environment details")
        print("5. Back")
        print(BORDER)
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            activate_env()
        elif choice == "2":
            run_command_in_env()
        elif choice == "3":
            interactive_shell()
        elif choice == "4":
            environment_details()
        elif choice == "5":
            break
        else:
            print("Invalid choice.")
            pause()

def package_management_menu():
    while True:
        clear_screen()
        print("Package Management")
        print(BORDER)
        print("1. Install packages")
        print("2. List installed packages")
        print("3. Update outdated packages")
        print("4. Package dependency graph")
        print("5. Back")
        print(BORDER)
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            install_packages()
        elif choice == "2":
            list_installed_packages()
        elif choice == "3":
            update_outdated()
        elif choice == "4":
            dependency_graph()
        elif choice == "5":
            break
        else:
            print("Invalid choice.")
            pause()

def backup_restore_menu():
    while True:
        clear_screen()
        print("Backup & Restore / Packaging")
        print(BORDER)
        print("1. Backup environment")
        print("2. Restore environment")
        print("3. Package environment")
        print("4. Back")
        print(BORDER)
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            backup_env()
        elif choice == "2":
            restore_env()
        elif choice == "3":
            package_env()
        elif choice == "4":
            break
        else:
            print("Invalid choice.")
            pause()

def extras_menu():
    while True:
        clear_screen()
        print("Extras")
        print(BORDER)
        print("1. Search/Filter environments")
        print("2. Custom environment notes")
        print("3. Back")
        print(BORDER)
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            search_envs()
        elif choice == "2":
            custom_notes()
        elif choice == "3":
            break
        else:
            print("Invalid choice.")
            pause()

def main_menu():
    while True:
        print_header()
        print("MAIN MENU - Categories")
        print(BORDER)
        print("1. Environment Management")
        print("2. Environment Interaction")
        print("3. Package Management")
        print("4. Backup & Restore / Packaging")
        print("5. Extras")
        print("6. Exit")
        print(BORDER)
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            env_management_menu()
        elif choice == "2":
            env_interaction_menu()
        elif choice == "3":
            package_management_menu()
        elif choice == "4":
            backup_restore_menu()
        elif choice == "5":
            extras_menu()
        elif choice == "6":
            clear_screen()
            sys.exit(0)
        else:
            print("Invalid choice.")
            pause()

def main():
    check_system()
    ensure_base_dir()
    main_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear_screen()
        sys.exit(0)
