import chess.pgn

from builders import *
from write import save


# Set up a chessboard (pointselectors, name painting annos using standard notation)
# Read a chess notation format
# with timestamps
# use JSON Patch -> path to move the pieces
# use => hidden to take a piece (off the board)

# Notation supported is https://en.wikipedia.org/wiki/Portable_Game_Notation
# https://python-chess.readthedocs.io/en/latest/pgn.html
# Going to make it easy for myself (and in the absence of actual models) to pretend that:
# - The board model is 8 Scene units by 8 Scene units and its model origin is its bottom left corner, so...
# - placing the board model at 0,0,0 puts it in the horizontal plane extending 8 units into the y and x direction
# - ...with white at the bottom.
# - ...also, piece origin is in their bases, so we can place at x,y and have them sitting on the board.

def make_piece_painting_anno(scene, xy_map, key, model, label):
    square_xy = xy_map[key]
    target = make_specific_resource_point_selector(scene, square_xy['x'], square_xy['y'], 0)
    painting = make_painting_annotation(key, model, "Model", target, label)
    add_painting_annotation(scene, painting)
    return painting


def make_board(game_slug: str, label: str):
    manifest = make_manifest(game_slug, label, with_metadata=True)
    scene = make_scene("1", f"Scene for {label}", False) # we'll make our own annopage for clarity
    add_container(manifest, scene)
    ps_target = make_specific_resource_point_selector(scene, 0, 0, 0)
    painting = make_painting_annotation("board", "chessboard.gltf", "Model", ps_target, "The board")
    add_painting_annotation(scene, painting)

    xy_map = {}
    board_map = {}
    for x in range(8):
        col = chr(ord('a') + x)
        for y in range(8):
            y1 = y + 1
            key = f"{col}{y1}"
            xy_map[key] = { "x": x + 0.5, "y": y + 0.5 }
            if y1 == 2:
                board_map[key] = make_piece_painting_anno(scene, xy_map, key, "white_pawn.gltf", f"{key} White Pawn")
            elif y1 == 7:
                board_map[key] = make_piece_painting_anno(scene, xy_map, key, "black_pawn.gltf", f"{key} Black Pawn")
            else:
                board_map[key] = None

    board_map["a1"] = make_piece_painting_anno(scene, xy_map, "a1", "white_rook.gltf", "a1 White Rook")
    board_map["b1"] = make_piece_painting_anno(scene, xy_map, "b1", "white_knight.gltf", "b1 White Knight")
    board_map["c1"] = make_piece_painting_anno(scene, xy_map, "c1", "white_bishop.gltf", "c1 White Bishop")
    board_map["d1"] = make_piece_painting_anno(scene, xy_map, "d1", "white_queen.gltf", "d1 White Queen")
    board_map["e1"] = make_piece_painting_anno(scene, xy_map, "e1", "white_king.gltf", "e1 White King")
    board_map["f1"] = make_piece_painting_anno(scene, xy_map, "f1", "white_bishop.gltf", "f1 White Bishop")
    board_map["g1"] = make_piece_painting_anno(scene, xy_map, "g1", "white_knight.gltf", "g1 White Knight")
    board_map["h1"] = make_piece_painting_anno(scene, xy_map, "h1", "white_rook.gltf", "h1 White Rook")
    board_map["a8"] = make_piece_painting_anno(scene, xy_map, "a8", "black_rook.gltf", "a8 Black Rook")
    board_map["b8"] = make_piece_painting_anno(scene, xy_map, "b8", "black_knight.gltf", "b8 Black Knight")
    board_map["c8"] = make_piece_painting_anno(scene, xy_map, "c8", "black_bishop.gltf", "c8 Black Bishop")
    board_map["d8"] = make_piece_painting_anno(scene, xy_map, "d8", "black_queen.gltf", "d8 Black Queen")
    board_map["e8"] = make_piece_painting_anno(scene, xy_map, "e8", "black_king.gltf", "e8 Black King")
    board_map["f8"] = make_piece_painting_anno(scene, xy_map, "f8", "black_bishop.gltf", "f8 Black Bishop")
    board_map["g8"] = make_piece_painting_anno(scene, xy_map, "g8", "black_knight.gltf", "g8 Black Knight")
    board_map["h8"] = make_piece_painting_anno(scene, xy_map, "h8", "black_rook.gltf", "h8 Black Rook")

    return manifest, board_map, xy_map


def make_move_anno(board, move, board_map, xy_map, scene):
    print("-----------------------------------------------------------")
    print(str(board))
    from_key = chess.square_name(move.from_square)
    to_key = chess.square_name(move.to_square)
    turn = 'Black' if board.turn else 'White'
    print(f"{turn} {move} {from_key} -> {to_key}")

    # In this private world we know we've put comments first then activators
    commenting_anno_id = f"{scene['annotations'][0]['id']}/{board.fullmove_number}{turn.lower()}"
    activating_anno_id = f"{scene['annotations'][1]['id']}/{board.fullmove_number}{turn.lower()}"
    scene['annotations'][0]['items'].append({
        "id": commenting_anno_id,
        "type": "Annotation",
        "motivation": [ "commenting" ],
        "body": {
            "type": "TextualBody",
            "value": f"{turn} {move}\n\n{str(board)}"
            # TODO: pull move comments from the parsed PGN
        },
        "target": scene["id"] # ? just target the scene all the time?
    })
    activating_annotation = make_move(activating_anno_id, board_map, commenting_anno_id, from_key, to_key, xy_map)
    if activating_annotation is None:
        return False

    scene['annotations'][1]['items'].append(activating_annotation)

    # Extra castling rook moves
    rook_from = None
    rook_to = None
    if str(move) == "e1g1":
        rook_from = "h1"
        rook_to = "f1"
    elif str(move) == "e1c1":
        rook_from = "a1"
        rook_to = "d1"
    elif str(move) == "e8g8":
        rook_from = "h8"
        rook_to = "f8"
    elif str(move) == "e8c8":
        rook_from = "a8"
        rook_to = "d8"

    if rook_from is not None:
        print(f"Castling: need to move rook as well - {rook_from}{rook_to}")
        castle_move = make_move(f"{activating_anno_id}-castle", board_map, commenting_anno_id,
                                rook_from, rook_to, xy_map)
        scene['annotations'][1]['items'].append(castle_move)

    print("-----------------------------------------------------------")
    print()
    return True


def make_move(activating_anno_id, board_map, commenting_anno_id, from_key, to_key, xy_map):
    # TODO: castling, en passant, promotion
    painting_anno_at_from = board_map[from_key]  # assume there is always a painting anno here
    painting_anno_at_to = board_map[to_key]  # key will exist from initial population, value may be null
    if painting_anno_at_from is None:
        print("I can't make this move (for now), nothing on " + from_key)
        return None

    from_xy = xy_map[from_key]
    to_xy = xy_map[to_key]
    print(f"From {from_key} ({from_xy['x']}, {from_xy['y']}) to {to_key} ({to_xy['x']}, {to_xy['y']})")
    print(f"Patching anno {painting_anno_at_from["id"]} to target ({to_xy['x']}, {to_xy['y']})")

    activating_annotation = {
        "id": activating_anno_id,
        "type": "Annotation",
        "motivation": ["activating"],
        "target": commenting_anno_id,  # the thing that triggers the action (revised switcheroo)
        "body": [  # the thing being acted upon... except that this isn't quite that...
            {
                "type": "JSONPatch",
                "patchTarget": painting_anno_at_from["id"],  # How else to get this in here????
                "value": [
                    {"op": "replace", "path": "/target/selector/1/x", "value": to_xy["x"]},
                    {"op": "replace", "path": "/target/selector/1/y", "value": to_xy["y"]}
                ]
            }
        ]
    }
    if painting_anno_at_to is not None:
        activating_annotation["disables"] = [painting_anno_at_to["id"]]

    board_map[from_key] = None
    board_map[to_key] = painting_anno_at_from
    return activating_annotation


def pgn_to_manifest(pgn_path: str):
    pgn = open(pgn_path)
    game = chess.pgn.read_game(pgn)
    board = game.board()
    manifest_slug = f"{pgn_path.split('/')[-1].split('.')[0]}.json"
    label = game.headers.get("Event", pgn_path)
    manifest, board_map, xy_map = make_board(manifest_slug, label)
    for h in ["Event", "Site", "Date", "Round", "White", "Black", "Result"]:
        h_val = game.headers.get(h, None)
        if h_val is not None:
            add_metadata(manifest, h, h_val)

    scene = manifest["items"][0]

    # Where do the activating annotations actually go... in a separate anno page?
    scene["annotations"] = [
        {
            "id": f"{manifest['id']}/1/commenting",
            "type": "AnnotationPage",
            "behavior": ["sequence"],
            "items": []
        },
        {
            "id": f"{manifest['id']}/1/activating",
            "type": "AnnotationPage",
            "items": []
        }
    ]

    for move in game.mainline_moves():
        board.push(move)
        success = make_move_anno(board, move, board_map, xy_map, scene)
        if not success:
            print("Have to stop the game here as I can't yet process that move! Sorry.")
            break

    save(manifest)


pgn_to_manifest('games/1992-29-fischer-spassky.pgn')
pgn_to_manifest('games/game-of-the-century.pgn')
