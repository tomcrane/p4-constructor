from builders import *
from write import save


def single_model_at_origin(manifest_slug, manifest_label, painting_slug, body_slug, model_label):
    manifest = make_manifest(manifest_slug, manifest_label)
    scene = make_scene(f"{manifest_slug}/scene-1", "A scene", True)
    add_container(manifest, scene)
    painting = make_painting_annotation(painting_slug, body_slug, "Model", scene, model_label)
    add_painting_annotation(scene, painting)
    return manifest


def basic_astronaut():
    manifest = single_model_at_origin(
        "basic_astronaut.json", "Manifest with scene",
        "astronaut", "models/astronaut.gltf", "An astronaut")
    save(manifest)


def issue_2366():
    # anno slugs align with https://github.com/IIIF/api/issues/2366#issuecomment-3329802820
    manifest = single_model_at_origin(
        "issue_2366.json", "GitHub API issue 2366 - Light switch",
        "lightswitch-1", "models/lightswitch.gltf", "A light switch")

    scene = manifest['items'][0]
    switch_model_painting_anno = scene['items'][0]['items'][0]
    point_light = {
        "id": scene["id"] + "/lights/point-light-4",
        "type": "Annotation",
        "motivation": [ "painting" ],
        "body": {
            "id": scene["id"] + "/lights/4/body",
            "type": "PointLight",
        },
        "target": make_specific_resource_point_selector(scene, 5, 5, 5),
        "behavior": [ "hidden" ]
    }
    scene['items'][0]['items'].append(point_light)

    annotation_page = scene['annotations'][0]

    commenting_annotation = {
        "id": annotation_page['id'] + "/switch-comment-0",
        "type": "Annotation",
        "motivation": [ "commenting" ],
        "body": {
            "type": "TextualBody",
            "value": "Click the switch to turn the light on or off"
        },
        "target": switch_model_painting_anno['id']
    }
    annotation_page['items'].append(commenting_annotation)

    activating_annotation_on_id = annotation_page['id'] + "/activating-on-2"
    activating_annotation_off_id = annotation_page['id'] + "/activating-off-3"
    activating_annotation_on = {
        "id": activating_annotation_on_id,
        "type": "Annotation",
        "motivation": [ "activating" ],
        "target": switch_model_painting_anno['id'], # body/target swapped from issue example
        "disables": [ activating_annotation_on_id ], # i.e., disables itself
        "enables": [ activating_annotation_off_id, point_light['id'] ]
    }
    activating_annotation_off = {
        "id": activating_annotation_off_id,
        "type": "Annotation",
        "motivation": [ "activating" ],
        "target": switch_model_painting_anno['id'], # body/target swapped from issue example
        "disables": [ activating_annotation_off_id, point_light['id'] ], # i.e., disables itself
        "enables": [ activating_annotation_on_id ],
        "behavior": [ "hidden" ] # what does it mean for this to be hidden? What difference does it make?
    }
    annotation_page['items'].append(activating_annotation_on)
    annotation_page['items'].append(activating_annotation_off)

    save(manifest)


basic_astronaut()
issue_2366()