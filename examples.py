from builders import *
from write import save


def basic_astronaut():
    manifest = make_manifest("basic_astronaut.json", "Manifest with scene")
    scene = make_scene("s1", "A scene", True)
    add_container(manifest, scene)
    painting = make_painting_annotation("astronaut", "models/astronaut.gltf", "Model", scene, "An astronaut")
    add_painting_annotation(scene, painting)
    save(manifest)


basic_astronaut()