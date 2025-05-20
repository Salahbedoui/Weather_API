# generate_requirements.py

import pkg_resources

# Get all installed distributions
installed_packages = pkg_resources.working_set

# Sort them alphabetically by package name
packages = sorted(["{}=={}".format(i.key, i.version) for i in installed_packages])

# Define the output file path
output_file = "requirements.txt"

# Write to file
with open(output_file, "w") as f:
    for package in packages:
        f.write(f"{package}\n")

print(f"requirements.txt file has been generated with {len(packages)} packages.")
