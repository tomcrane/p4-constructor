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
    point_light = make_annotation("painting", scene["id"] + "/lights/point-light-4")
    point_light.update({
        "body": {
            "id": scene["id"] + "/lights/4/body",
            "type": "PointLight",
        },
        "target": make_specific_resource_point_selector(scene, 5, 5, 5),
        "behavior": [ "hidden" ]
    })
    scene['items'][0]['items'].append(point_light)

    annotation_page = scene['annotations'][0]

    commenting_annotation = make_annotation("commenting", annotation_page['id'] + "/switch-comment-0")
    commenting_annotation.update({
        "body": {
            "type": "TextualBody",
            "value": "Click the switch to turn the light on or off"
        },
        "target": switch_model_painting_anno['id']
    })

    activating_annotation_on_id = annotation_page['id'] + "/activating-on-2"
    activating_annotation_off_id = annotation_page['id'] + "/activating-off-3"

    activating_annotation_on = make_annotation("activating", activating_annotation_on_id)
    activating_annotation_on.update({
        "target": switch_model_painting_anno['id'], # body/target swapped from issue example
        "disables": [ activating_annotation_on_id ], # i.e., disables itself
        "enables": [ activating_annotation_off_id, point_light['id'] ]
    })

    activating_annotation_off = make_annotation("activating", activating_annotation_off_id)
    activating_annotation_off.update({
        "target": switch_model_painting_anno['id'], # body/target swapped from issue example
        "disables": [ activating_annotation_off_id, point_light['id'] ], # i.e., disables itself
        "enables": [ activating_annotation_on_id ],
        "behavior": [ "hidden" ] # what does it mean for this to be hidden? What difference does it make?
    })

    annotation_page['items'].append(commenting_annotation)
    annotation_page['items'].append(activating_annotation_on)
    annotation_page['items'].append(activating_annotation_off)

    save(manifest)


def multi_stop_gist():
    # https://gist.github.com/JulieWinchester/a70243fbd040278a8306b8ed0e194569
    manifest = single_model_at_origin(
        "multi_stop_gist.json", "Multi stop gist",
        "models/1", "models/astronaut.gltf", "An astronaut")
    add_metadata(manifest, "source", "https://gist.github.com/JulieWinchester/a70243fbd040278a8306b8ed0e194569")

    scene = manifest['items'][0]
    astronaut_painting_anno_1 = scene['items'][0]['items'][0]
    camera_2 = make_annotation("painting", scene["id"] + "/cameras/2")
    camera_2.update({
        "body": {
            "id": scene["id"] + "/cameras/2/body",
            "type": "Camera",
            "interactionMode": "locked", # 'static' in example
            "lookAt": {
                "id": astronaut_painting_anno_1['id'],
                "type": "Annotation"
            }
        },
        "target": make_specific_resource_point_selector(scene, 4, 3, 2)
    })
    scene['items'][0]['items'].append(camera_2)

    annotation_page = scene['annotations'][0]
    # Stop 1
    commenting_annotation_3 = make_annotation("commenting", annotation_page['id'] + "/commenting/3")
    commenting_annotation_3.update({
        "body": {
            "type": "TextualBody",
            "value": "Look at the glove"
        },
        "target": make_specific_resource_point_selector(scene, 12, 4, 9)
    })
    annotation_page['items'].append(commenting_annotation_3)

    activating_annotation_4 = make_annotation("activating", annotation_page['id'] + "/activating/4")
    activating_annotation_4.update({
        "target": commenting_annotation_3['id'], # body/target swapped from issue example
        "body": scene["id"] + "/cameras/5",      # body/target swapped from issue example
        "enables": [
            scene["id"] + "/cameras/5",
            scene["id"] + "/lights/6",
            annotation_page['id'] + "/commenting/7",
            annotation_page['id'] + "/commenting/8"
        ],
        "disables": [
            scene["id"] + "/cameras/2",
            annotation_page['id'] + "/commenting/3",
            annotation_page['id'] + "/activating/4"    # itself
        ]
    })
    annotation_page['items'].append(activating_annotation_4)

    camera_5 = make_annotation("painting", scene["id"] + "/cameras/5")
    camera_5.update({
        "body": {
            "id": scene["id"] + "/cameras/5/body",
            "type": "Camera",
            "interactionMode": "orbit"  # around the glove
        },
        "target": make_specific_resource_point_selector(scene, 4, 3, 2),
        "behavior": [ "hidden" ]
    })
    scene['items'][0]['items'].append(camera_5)


    spotlight_6 = make_annotation("painting", scene["id"] + "/lights/6")
    spotlight_6.update({
        "body": {
            "id": scene["id"] + "/lights/6/body",
            "type": "SpotLight",
            "lookAt": make_specific_resource_point_selector(scene, 4, 3, 2) # the glove
        },
        "target": make_specific_resource_point_selector(scene, 10, 10, 10),
        "behavior": [ "hidden" ]
    })
    scene['items'][0]['items'].append(spotlight_6)


    commenting_annotation_7 = make_annotation("commenting", annotation_page['id'] + "/commenting/7")
    commenting_annotation_7.update({
        "body": {
            "type": "TextualBody",
            "value": "Long discursive text about the glove that should only be visible when looking at glove"
        },
        "target": make_specific_resource_point_selector(scene, 4, 3, 2),  # the glove (?)
        "behavior": [ "hidden" ]
    })
    annotation_page['items'].append(commenting_annotation_7)


    commenting_annotation_8 = make_annotation("commenting", annotation_page['id'] + "/commenting/8")
    commenting_annotation_8.update({
        "body": {
            "type": "TextualBody",
            "value": "Look at the helmet"
        },
        "target": make_specific_resource_point_selector(scene, 0, 0, 9),  # the helmet
        "behavior": [ "hidden" ]
    })
    annotation_page['items'].append(commenting_annotation_8)


    activating_annotation_9 = make_annotation("activating", annotation_page['id'] + "/activating/9")
    activating_annotation_9.update({
        "target": commenting_annotation_8['id'], # body/target swapped from issue example
        "body": scene["id"] + "/cameras/10",      # body/target swapped from issue example
        "enables": [
            # step back:
            scene["id"] + "/cameras/2",               # reactivate locked camera
            annotation_page['id'] + "/commenting/3",  # "Look at the glove" comment
            annotation_page['id'] + "/activating/4",  # Activation for "look at the glove"
            # move on:
            scene["id"] + "/cameras/10",              # not present in manifest yet
            scene["id"] + "/lights/11",               # not present in manifest yet
            annotation_page['id'] + "/commenting/12", # not present in manifest yet
            annotation_page['id'] + "/commenting/13"  # not present in manifest yet
        ],
        "disables": [
            scene["id"] + "/cameras/5",
            scene["id"] + "/lights/6",
            annotation_page['id'] + "/commenting/7",
            annotation_page['id'] + "/commenting/8",
            annotation_page['id'] + "/activating/9"   # itself
        ]
    })
    annotation_page['items'].append(activating_annotation_9)

    save(manifest)


def music_box():
    manifest = single_model_at_origin(
        "music_box.json", "Music Box with lid that opens as an internal animation",
        "models/musicbox", "models/musicbox.gltf", "A music box")

    scene = manifest['items'][0]
    add_label(scene, "A Scene Containing a Music Box")
    mb_painting_anno = scene['items'][0]['items'][0]

    annotation_page = scene['annotations'][0]
    commenting_annotation = make_annotation("commenting", annotation_page['id'] + "/comment")
    commenting_annotation.update({
        "body": {
            "type": "TextualBody",
            "value": "Click the box to open the lid"
        },
        "target": {
            "id": mb_painting_anno["id"],
            "type": "Annotation"
        }
    })
    annotation_page['items'].append(commenting_annotation)

    activating_anno = make_annotation("activating", annotation_page['id'] + "/activator")
    activating_anno.update({
        "target": {
            "id": commenting_annotation["id"],
            "type": "Annotation"
        },
        "body": {
            "type": "SpecificResource",
            "source": mb_painting_anno["id"],
            "selector": [
                {
                    "type": "AnimationSelector",
                    "value": "open-the-lid"
                }
            ]
        }
    })
    annotation_page['items'].append(activating_anno)

    save(manifest)

# -----------------------------------------------------------------------------

basic_astronaut()
issue_2366()
multi_stop_gist()
music_box()