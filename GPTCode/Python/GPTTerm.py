import os
import subprocess

def main():
    while True:
        try:
            # Get the current working directory
            cwd = os.getcwd()
            # Display the prompt with the current directory
            cmd = input(f'{cwd}> ')
            # Skip if the input is empty
            if not cmd.strip():
                continue
            # Exit the console if 'exit' or 'quit' is entered
            if cmd.lower() in ('exit', 'quit'):
                break
            # Handle 'cd' command internally
            if cmd.lower().startswith('cd '):
                path = cmd[3:].strip().strip('"')
                try:
                    os.chdir(path)
                except FileNotFoundError:
                    print(f"The system cannot find the path specified: '{path}'")
                except Exception as e:
                    print(e)
                continue
            # Execute other commands using subprocess
            process = subprocess.Popen(cmd, shell=True)
            process.communicate()
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print()
        except EOFError:
            # Exit on Ctrl+Z (EOF)
            break

if __name__ == '__main__':
    main()
