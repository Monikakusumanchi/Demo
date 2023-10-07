import main

def get_requirements(output_file='requirements.txt'):
    # Get a list of all installed packages and their versions
    installed_packages = pkg_resources.working_set
    package_names = [package.key for package in installed_packages]
    
    # Write the package names and versions to the output file
    with open(output_file, 'w') as f:
        for package_name in package_names:
            f.write(f"{package_name}\n")

if __name__ == "__main__":
    # Call the function to generate requirements.txt
    get_requirements()
    print("requirements.txt file created.")