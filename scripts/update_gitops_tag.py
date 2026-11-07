import sys
from pathlib import Path

import yaml

if len(sys.argv) != 3:
    print("Usage: python update_gitops_tag.py <values-file> <image-tag>")
    sys.exit(1)

values_file = Path(sys.argv[1])
new_tag = sys.argv[2]

with values_file.open() as file:
    values = yaml.safe_load(file)

old_tag = values["image"]["tag"]
values["image"]["tag"] = str(new_tag)

with values_file.open("w") as file:
    yaml.safe_dump(values, file, sort_keys=False)

print(f"Updated image tag: {old_tag} -> {new_tag}")
