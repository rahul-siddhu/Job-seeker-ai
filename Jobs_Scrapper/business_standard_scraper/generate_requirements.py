import os
import pkg_resources

def main():
    # Set the project directory to the current directory (root of Scrapy project)
    project_dir = "."
    imported_modules = set()

    # Scan all Python files in the project for imports
    for root, _, files in os.walk(project_dir):
        for file in files:
            if file.endswith(".py"):
                with open(os.path.join(root, file)) as f:
                    for line in f:
                        if line.startswith("import") or line.startswith("from"):
                            # For simple imports like `import module`
                            if line.startswith("import"):
                                module = line.split()[1].split('.')[0]
                            # For from-imports like `from module.submodule import ...`
                            elif line.startswith("from"):
                                module = line.split()[1].split('.')[0]
                            imported_modules.add(module)

    # Match imported modules with installed packages
    installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
    requirements = {pkg: version for pkg, version in installed_packages.items() if pkg in imported_modules}

    # Write the filtered dependencies to requirements.txt
    with open("requirements.txt", "w") as f:
        for pkg, version in requirements.items():
            f.write(f"{pkg}=={version}\n")

    print("requirements.txt created with project-specific packages.")

if __name__ == "__main__":
    main()
