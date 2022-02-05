Title: Tilemaps with data
Category: Cavetown
Date: 02-04-2022 13:30

#### How and why you might want tilemaps that have data associated with the tiles in [Godot](https://godotengine.org/).

### Problem: You have tiles that need to track some state

In my case I wanted to have tiles that were could be destoryed after multiple hits.

There's three ways I considered doing this:

1. Don't use a `TileMap`, just use `Node`s with `Sprite2D`s attached and have some logic that makes sure they are placed on a grid, as if they were rendered with a `TileMap`
2. Extend the `TileMap` class and maintain a `Dictionary` of `Vector2 -> <Custom class>`
3. (The option I went with) Extend the `TileMap` class and maintain a `Dictionary` of `Vector2 -> <Node with a script attached>`

Options 2 and 3 are very similar one might be better than the other depending on the use case.

[ore_map.gd](https://github.com/ToxicGLaDOS/cavetown/blob/f0c83d58bd6cc65210ac7b2a2aeb0bcb698e54ee/ore_map/ore_map.gd)
```gdscript
extends TileMap

export(PackedScene) var iron_ore

# This holds references to the nodes so we
# can access them with TileMap coordinates
var cell_data : Dictionary = {}

# Called when the node enters the scene tree for the first time.
func _ready():
    # Create 10 ores in random locations on the tilemap
    for x in range(10):
        var node = spawn_ore()
        var cell = world_to_map(node.position)
        set_cellv(cell, node.id)
        cell_data[cell] = node

func spawn_ore():
    # This iron_ore Node has no sprites attached to it
    # it's just a Node that holds a script which contains
    # helper functions
    var node = iron_ore.instance()
    var width = 16
    var height = 16
    var x = randi() % 30
    var y = randi() % 30

    add_child(node)
    node.position = Vector2(x * 16 + width / 2, y * 16 + height / 2)
    return node

# This function deals with the player hitting a tile
# when a player presses the button to swing their pickaxe
# they call this function with the tilemap coords that their aiming at
func hit_cell(x, y):
    var key = Vector2(x, y)
    # Check if that cell is tracked by us
    if cell_data.has(key):
        # Note: cell_data[key] is a Node
        cell_data[key].health -= 1

        # If the ore is out of health we destory it
        # and clean it up from our cell_data map
        if cell_data[key].health == 0:
            # Set the tiles sprite to empty
            set_cell(x, y, -1)
            # Destory the Node
            var drops = cell_data[key].destroy()

            # Get drops from the ore
            for drop in drops:
                add_child(drop)

            # Clean up the cell_data map
            cell_data.erase(key)
            return true
    return false
```

This is the script attached to the `Node`s we reference in the `TileMap`

[iron_ore.gd](https://github.com/ToxicGLaDOS/cavetown/blob/f0c83d58bd6cc65210ac7b2a2aeb0bcb698e54ee/ore_nodes/iron_ore.gd)

```gdscript
extends Node2D

# The chunk that's dropped after mining this ore
export(PackedScene) var iron_chunk

const id: int  = 0
var health: int = 2

func destroy():
    var node = iron_chunk.instance()
    node.position = position
    queue_free()
    return [node]
```


## What does this actually do?

When the player mines the ore you can see that the nodes in the remote scene view (on the very left) are replaced with an iron chunk.
This is the iron chunk generated from `destory()` in `iron_ore.gd`.
After the player picks up the iron chunk it's gone for good.

<img src="mining_ore.gif">


## Why is this better than cutting out the `TileMap` and using `Node2D` directly?

1. It allows us to have the rendering logic handled by a `TileMap` which means that our ore can't be placed some where it shouldn't be.
2. `TileMap`s tend to be slightly more optimized for rendering. I don't know about Godot specifically, but this probably has some minor performance benifits. Although, this is probably irrelvent for my case.
3. We still get all the benefits of having `Node`s, because the tiles are backed by actual `Node` instances.

## Why is this better than using a custom class rather than a Node

Here's what a class that might look like:

```gdscript
class IronOre:
    const id: int  = 0
    var health: int = 2
    var iron_chunk: PackedScene
    
    func destroy():
        var node = iron_chunk.instance()
        node.position = position
        queue_free()
        return [node]

    func _init(chunk):
        iron_chunk = chunk
        # We could remove the need to pass in chunk
        # if we loaded the chunk scene with a hardcoded string
        # load("res://iron_ore.tscn")
```

Notice that it's basically the same as `iron_ore.gd`.
We'd use `IronOre.new(iron_chunk)` instead of `iron_ore.instantiate()` to create it, but that's not necessarily a problem.
Where this _does_ run into issues is with getting the `iron_chunk` reference.
When using the class we need to load the `PackedScene` somehow, and this could be done by hardcoding it in.
i.e. `load("res://iron_ore.tscn")`, this would remove the need for the `_init(chunk)` constructor.
Or we could export a varible in our `TileMap` which is then passed through when we instantiate the `IronOre` class like this.

```gdscript
extends TileMap

# Notice this is iron_chunk (the thing that iron_ore drops), _not_ iron_ore (the thing that a player mines)
export(PackedScene) var iron_chunk

...

func spawn_ore():
    # Pass the iron_chunk PackedScene through
    var node = IronOre.new(iron_chunk)
    var width = 16
    var height = 16
    var x = randi() % 30
    var y = randi() % 30
    
    ...

```

This works, but if we need to pass in more `PackedScene`s to `IronOre` we'll have to export those through the `TileMap`.
And if we introduce more types of ore, we'll have to export even more variables through the `TileMap`.
The worst part of this is that these scenes don't have anything to do with the `TileMap`.

On the other hand, by having `Node`s be the backend we can use the editor to drag-and-drop the correct chunk for each ore scene.
We still have to export a variable in the `TileMap` for each ore type, but that's it!


## Why is this worse than the other options?

There are some trade-offs we make by using this method.

1. We have to maintain the node tree and keep that in sync. With the class method we'd have to ensure we free our memory, and this has the same issue. Everytime we create a node we need to `queue_free` it if we remove it.
2. We have two ways to refer to the "position" of the ore. The `Node` has a position and we have a position which acts as a key for the dictionary. The `Node` position should never be used, so it doesn't have to be kept in sync, but you need to make sure you never use it.


## Another strategy?

While writing this I thought it might be possible to get the best of both worlds by using `Resource`s instead of `Node`s to hold the state.
I think this might give us all the ability to

1. Call functions, hold data, and be seperate from the TileMap file (both methods have this already)
2. Edit variables from the editor (like the `Node` method can do)
3. Cut out the need to manage `Node`s in the node tree, which could reduce clutter (like the class solution can do).

I'm not totally sure if 3 is possible, but this seems worth investigating!

