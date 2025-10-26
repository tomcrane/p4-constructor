import settings


def make_uri(prefix: str, slug: str) -> str:
    return f"{settings.BASE_URL}/{settings.IIIF_DIR}/{prefix}/{slug}"


def en_lang_map(value: str):
    return {
        "en": [ value ]
    }


def add_label(resource: dict, label: str):
    if label is not None:
        resource["label"] = en_lang_map(label)
    else:
        del resource["label"]


def make_manifest(slug: str, label: str = None, with_metadata: bool = False) -> dict:
    resource = {
        "id": make_uri("manifest", slug),
        "type": "Manifest",
        "label": {},
        "metadata": [],
        "items": []
    }
    if not with_metadata:
        del resource["metadata"]
    add_label(resource, label)
    return resource


def make_scene(slug: str, label: str = None, with_annotations: bool = False) -> dict:
    resource = {
        "id": make_uri("scene", slug),
        "type": "Scene",
        "label": {},
        "items": [
            {
                "id": make_uri(f"scene/{slug}", "painting-annotation-pages/1"),
                "type": "AnnotationPage",
                "items": []
            }
        ]
    }
    add_label(resource, label)
    if with_annotations:
        resource["annotations"] = [
            {
                "id": make_uri(f"scene/{slug}", "other-annotation-pages/1"),
                "type": "AnnotationPage",
                "items": []
            }
        ]
    return resource


def get_target(target):
    if isinstance(target, dict):
        t_type = target.get("type", None)
        is_container = t_type in ["Scene", "Canvas", "Timeline"]
        if len(target.keys()) > 2 and target.get("id", None) and is_container:
            # Just use the id
            return target["id"]
    # if caller explicitly wants { id, type } then this will return it unchanged
    return target


def make_painting_annotation(slug: str, body_slug: str, body_type: str, target, label: str = None) -> dict:

    resource = {
        "id": make_uri("painting-annotation", slug),
        "type": "Annotation",
        "motivation": [ "painting" ],
        "label": {},
        "body": {
            "id": make_uri(body_type.lower(), body_slug),
            "type": body_type
        },
        "target": get_target(target)
    }
    add_label(resource, label)
    return resource


def add_container(manifest: dict, container: dict):
    manifest["items"].append(container)


def add_painting_annotation(container: dict, annotation: dict):
    container["items"][0]["items"].append(annotation)


def make_specific_resource_point_selector(source, x, y, z):
    return {
        "type": "SpecificResource",
        "source": get_target(source),
        "selector": [
            {
                "type": "PointSelector",
                "x": x,
                "y": y,
                "z": z
            }
        ]
    }


def add_metadata(resource: dict, label: str, value: str):
    metadata = resource.get("metadata", None)
    if metadata is None:
        metadata = []
        resource["metadata"] = metadata
    metadata.append({
        "label": en_lang_map(label),
        "value": en_lang_map(value)
    })


def make_annotation(motivation: str, id_: str):
    return {
        "id": id_,
        "type": "Annotation",
        "motivation": [ motivation ]
    }