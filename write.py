import json
import settings
from pathlib import Path

def save(resource: dict):
    if resource.get("@context", None) is None:
        resource["@context"] = "http://iiif.io/api/presentation/4/context.json"
    relative_path = Path(resource['id'].replace(f"{settings.BASE_URL}/", ""))
    relative_path.parent.mkdir(parents=True, exist_ok=True)
    with open(relative_path, "w", ) as f:
        json.dump(resource, f, indent=4)