nav_instruction_template = """In this task, you will navigate through a map with the goal of generating actions to locate and reach the destination.
At each time step, you will be provided with the following inputs:
1. A first-person observation of the 3x3 surrounding tiles, with all unspecified tiles being {unspecified_tile}.
2. The direction you are currently facing.
Here are more detailed explanations of the observation you get:
1. You are positioned at the center tile of the 3x3 tiles:
    [front-left]   [front]   [front-right]
    [left]         [ YOU ]   [right]
    [back-left]    [back]    [back-right]

You can issue the following actions in this environment:
    forward -> Move 1 tile forward in your current direction.
    turn right
    turn left
    turn around -> Rotate 180° to face the opposite direction.
    think[...] -> Use this to reason about your next move. Add any internal thoughts or planning here. After thinking (Observation: OK.), you must immediately issue an execution action (forward, turn left, turn right, or turn around) rather than repeating think[...].

Movement Constraints:
    You can only move along the 'road'.
    Grass, trees, houses, and other obstacles are non-traversable.
    To turn left, the direct 'left' tile must be a road. Note that 'front-left' is diagonal ahead and is NOT the direct 'left' tile.
    To turn right, the direct 'right' tile must be a road. Note that 'front-right' is diagonal ahead and is NOT the direct 'right' tile.
"""

nav_instruction_summer = nav_instruction_template.format(unspecified_tile='grasslands with flowers and scattered stones')
nav_instruction_winter = nav_instruction_template.format(unspecified_tile='lands with ice and scattered stones')


# python main.py --env VillageNav-easy-v0 --manual_type 1 --seed 12087226

nav_react = """
Here is one example:
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the back-left tile.
There is a group of green pines on the front-left tile.
The front-right, left, right tiles are roads that you can step on.
Direction: You are facing east.

Action: think[I can't move forward because the tile ahead isn't a road. But since there's a road to my left, I can turn right and follow it.]
Observation: OK.

Action: turn left
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the front-left tile.
There is a group of green pines on the front-right tile.
The front, back, back-right tiles are roads that you can step on.
Direction: You are facing north.

Action: think[Now that the tile in front of me is a road, I can move forward along it.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the left tile.
There is a group of green pines that spans the front-right, right tiles.
The front, back tiles are roads that you can step on.
Direction: You are facing north.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the back-left tile.
There is a group of green pines that spans the right, back-right tiles.
The front-left, front, front-right, back tiles are roads that you can step on.
Direction: You are facing north.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a group of green pines on the back-right tile.
There is a house on the front-right tile.
The front-left, left, right, back tiles are roads that you can step on.
Direction: You are facing north.

Action: think[The tile in front of me is no longer a road, but there's a road to my left. I can try turning left to see what's over there.]
Observation: OK.

Action: turn left
Observation: You can see the 3x3 tiles surrounding you:
There is a group of green pines on the back-left tile.
There is a house on the back-right tile.
The front, front-right, left, back tiles are roads that you can step on.
Direction: You are facing west.

Action: think[There's a road in front of me now, so I can walk forward and see what's ahead.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
The destination is on the front-right tile.
The front, right, back-left, back tiles are roads that you can step on.
Direction: You are facing west.

Action: forward
Observation: Task completed successfully.
"""


nav_react_tiles = """
Important: To assist you in this task, we provide a guide to find the destination.
Note that you can only move one tile per action. If a step in the guide requires you to move multiple tiles, you must execute that number of individual “forward” actions.
For example, if a step requires you to walk five tiles forward, you need to take the “forward” action five times.

Here is one example:
Step-by-Step Guide to Complete the Task:
Start! You are currently facing east.
Step 1. Turn left to face north.
Step 2. Move forward 3 tiles (north).
Step 3. Turn left to face west.
Step 4. Move forward 2 tiles (west) to approach the destination.

Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the back-left tile.
There is a group of green pines on the front-left tile.
The front-right, left, right tiles are roads that you can step on.
Direction: You are facing east.

Action: think[The first step in the guide is to turn left to face north. Since I'm currently facing east, turning left once will orient me toward the north.]
Observation: OK.

Action: turn left
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the front-left tile.
There is a group of green pines on the front-right tile.
The front, back, back-right tiles are roads that you can step on.
Direction: You are facing north.

Action: think[Now I'm facing north. According to the second step in the guide, I need to move forward three tiles in the direction to my left.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the left tile.
There is a group of green pines that spans the front-right, right tiles.
The front, back tiles are roads that you can step on.
Direction: You are facing north.

Action: think[I've moved forward once. According to the guide, I still need to move forward 3-1=2 more times.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the back-left tile.
There is a group of green pines that spans the right, back-right tiles.
The front-left, front, front-right, back tiles are roads that you can step on.
Direction: You are facing north.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a group of green pines on the back-right tile.
There is a house on the front-right tile.
The front-left, left, right, back tiles are roads that you can step on.
Direction: You are facing north.

Action: think[I've successfully moved forward three times. According to the next step in the guide, I need to turn left to face west. Since I'm currently facing north, turning left once will do it.]
Observation: OK.

Action: turn left
Observation: You can see the 3x3 tiles surrounding you:
There is a group of green pines on the back-left tile.
There is a house on the back-right tile.
The front, front-right, left, back tiles are roads that you can step on.
Direction: You are facing west.

Action: think[According to the fourth step in the guide, I need to move forward two tiles westward to approach the destination. So my next two actions will be to move forward twice.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
The destination is on the front-right tile.
The front, right, back-left, back tiles are roads that you can step on.
Direction: You are facing west.

Action: forward
Observation: Task completed successfully.
"""


nav_react_obs = """
Important: To assist you in this task, we provide a guide to find the destination.

Step-by-Step Guide to Complete the Task:
Start! You are currently facing east.
Step 1. Turn left until you are facing north.
Step 2. Walk forward (toward north) until you see There is a group of green pines on the back-right tile. There is a house on the front-right tile. The front-left, left, right, back tiles are roads that you can step on.
Step 3. Turn left until you are facing west.
Step 4. Walk forward (toward west) until you are close to the destination.

Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the back-left tile.
There is a group of green pines on the front-left tile.
The front-right, left, right tiles are roads that you can step on.
Direction: You are facing east.

Action: think[The first step in the guide is to turn left to face north. Since I'm currently facing east, turning left once will orient me toward the north.]
Observation: OK.

Action: turn left
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the front-left tile.
There is a group of green pines on the front-right tile.
The front, back, back-right tiles are roads that you can step on.
Direction: You are facing north.

Action: think[According to Step 2, I need to walk forward (toward north) until I see a group of green pines on the back-right tile and a house on the front-right tile. I'm facing north now, but I haven't seen those landmarks yet, so I should start moving forward.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the left tile.
There is a group of green pines that spans the front-right, right tiles.
The front, back tiles are roads that you can step on.
Direction: You are facing north.

Action: think[I can see a group of green pines now, but they're on the front-right and right tiles — not exactly where the guide described. So I'll keep moving forward to see if I can find the exact spot the guide refers to.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the back-left tile.
There is a group of green pines that spans the right, back-right tiles.
The front-left, front, front-right, back tiles are roads that you can step on.
Direction: You are facing north.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a group of green pines on the back-right tile.
There is a house on the front-right tile.
The front-left, left, right, back tiles are roads that you can step on.
Direction: You are facing north.

Action: think[Now I see a group of green pines on the back-right tile and a house on the front-right tile. The front-left, left, right, back tiles are also roads — exactly as described in the guide. That means I've reached the correct location, so it's time to move on to the next step. The guide says to turn left until I'm facing west. Since I'm currently facing north, one left turn will do.]
Observation: OK.

Action: turn left
Observation: You can see the 3x3 tiles surrounding you:
There is a group of green pines on the back-left tile.
There is a house on the back-right tile.
The front, front-right, left, back tiles are roads that you can step on.
Direction: You are facing west.

Action: think[I'm now facing west. The final instruction says to walk forward toward the west until I'm close to the destination. So I'll keep moving straight ahead.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
The destination is on the front-right tile.
The front, right, back-left, back tiles are roads that you can step on.
Direction: You are facing west.

Action: forward
Observation: Task completed successfully.
"""


nav_react_turns = """
Important: To assist you in this task, we provide a guide to find the destination.
Key Rules:
1. When given an instruction like "Head [Direction], then take the N-th [Turn]" or "Continue going [Direction]; turn [Turn] at the 1st opportunity", you must proceed forward along the path in that direction first. Do NOT turn immediately at the intersection you just turned into.
2. A turn (turn left / turn right) can ONLY be executed when the tile directly to your left or right is listed as a road that you can step on. If only the diagonal tile ("front-left" or "front-right") is a road, the turn is 1 tile ahead—you MUST take the "forward" action first to enter the intersection before turning!

Here is one example:
Step-by-Step Guide to Complete the Task:
From your current location and direction, if you want to go to the destination, you can:
Step 1. Going east; turn right at the 1st opportunity.
Step 2. Continue going south and take the 1st left.
Step 3. Head straight — the destination is just past the 1st intersection.

Observation: You can see the 3x3 tiles surrounding you:
The front-left, front, front-right, back tiles are roads that you can step on.
There is a green tree with a hollow trunk that spans the right, back-right tiles.
There is a orange tree with a hollow trunk that spans the left, back-left tiles.
Direction: You are facing east.

Action: think[I am facing east. Step 1 says to go east and turn right at the 1st opportunity. The tile directly to my right is not a road, but front-right is a road, so the intersection is 1 tile ahead. According to Rule 2, I must move forward first to enter the intersection.]
Observation: OK. 

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a cluster of red lantern trees that spans the front, front-right tiles.
There is a group of four orange conical trees with smaller red trees among them on the front-right tile.
The front-left, left, right, back tiles are roads that you can step on.
There is a green tree with a hollow trunk on the back-right tile.
There is a orange tree with a hollow trunk on the back-left tile.
Direction: You are facing east.

Action: think[Now the tile directly to my right is a road, which is the 1st opportunity to turn right. Following Step 1, I will turn right to face south.]
Observation: OK. 

Action: turn right
Observation: You can see the 3x3 tiles surrounding you:
There is a cluster of red lantern trees that spans the front-left, left tiles.
There is a group of four orange conical trees with smaller red trees among them on the front-left tile.
The front, right, back-left, back tiles are roads that you can step on.
There is a green tree with a hollow trunk on the front-right tile.
There is a orange tree with a hollow trunk on the back-right tile.
Direction: You are facing south.

Action: think[I am now facing south. Step 2 says to continue going south and take the 1st left. Following Rule 1, I must proceed forward along this path first rather than turning immediately. So I will move forward.]
Observation: OK. 

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a cluster of green firs on the front-right tile.
There is a cluster of red lantern trees that spans the left, back-left tiles.
There is a group of four orange conical trees with smaller red trees among them that spans the front-left, left tiles.
The front, back, back-right tiles are roads that you can step on.
There is a green tree with a hollow trunk that spans the front-right, right tiles.
Direction: You are facing south.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a cluster of green firs that spans the front-right, right tiles.
There is a cluster of red lantern trees on the back-left tile.
There is a group of four orange conical trees with smaller red trees among them that spans the left, back-left tiles.
The front, back tiles are roads that you can step on.
There is a green tree with a hollow trunk that spans the right, back-right tiles.
Direction: You are facing south.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a cluster of green firs that spans the front-right, right, back-right tiles.
There is a group of four orange conical trees with smaller red trees among them on the back-left tile.
There is a house on the front-right tile.
The front-left, front, back tiles are roads that you can step on.
There is a green tree with a hollow trunk on the back-right tile.
Direction: You are facing south.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a cluster of green firs that spans the right, back-right tiles.
There is a house that spans the front-right, right tiles.
The left, back tiles are roads that you can step on.
Direction: You are facing south.

Action: think[The path ahead is blocked and the tile directly to my left is a road. This is the 1st opportunity to turn left according to Step 2. I will turn left to face east.]
Observation: OK.

Action: turn left
Observation: You can see the 3x3 tiles surrounding you:
There is a cluster of green firs that spans the back-left, back tiles.
There is a house that spans the back, back-right tiles.
The front, left tiles are roads that you can step on.
Direction: You are facing east.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a cluster of two rounded red bushy trees alongside a cone-shaped tree on the front-left tile.
The front, front-right, back-left, back tiles are roads that you can step on.
Direction: You are facing east.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
The destination is on the front-right tile.
There is a cluster of two rounded red bushy trees alongside a cone-shaped tree that spans the front-left, left tiles.
There is a house on the front-left tile.
The front, right, back tiles are roads that you can step on.
Direction: You are facing east.

Action: think[I have reached the 1st intersection and can see the destination on the front-right tile. According to Step 3, the destination is just past the 1st intersection, so I will move forward.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
The destination spans the front-right, right tiles.
There is a cluster of two rounded red bushy trees alongside a cone-shaped tree that spans the left, back-left tiles.
There is a house that spans the front-left, left tiles.
The front, back, back-right tiles are roads that you can step on.
Direction: You are facing east.

Observation: Task completed successfully.
"""

nav_tiles_obs = """Important: To assist you in this task, we provide a guide to find the destination.
Note that you can only move one tile per action. If a step in the guide requires you to move multiple tiles, you must execute that number of individual “forward” actions.
For example, if a step requires you to walk five tiles forward, you need to take the “forward” action five times.

Here is one example:
Step-by-Step Guide to Complete the Task:
Start! You are currently facing east.
Step 1. Turn left to face north.
Step 2. Move forward 3 tiles (north), after that you will see a group of green pines on the back-right tile and a house on the front-right tile.
Step 3. Turn left to face west.
Step 4. Move forward 2 tiles (west) to approach the destination.

Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the back-left tile.
There is a group of green pines on the front-left tile.
The front-right, left, right tiles are roads that you can step on.
Direction: You are facing east.

Action: think[The first step in the guide is to turn left to face north. Since I'm currently facing east, turning left once will orient me toward the north.]
Observation: OK.

Action: turn left
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the front-left tile.
There is a group of green pines on the front-right tile.
The front, back, back-right tiles are roads that you can step on.
Direction: You are facing north.

Action: think[Now I'm facing north. According to the second step in the guide, I need to move forward three tiles in the direction to my left.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the left tile.
There is a group of green pines that spans the front-right, right tiles.
The front, back tiles are roads that you can step on.
Direction: You are facing north.

Action: think[I've moved forward once. According to the guide, I still need to move forward 3-1=2 more times.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the back-left tile.
There is a group of green pines that spans the right, back-right tiles.
The front-left, front, front-right, back tiles are roads that you can step on.
Direction: You are facing north.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a group of green pines on the back-right tile.
There is a house on the front-right tile.
The front-left, left, right, back tiles are roads that you can step on.
Direction: You are facing north.

Action: think[I've successfully moved forward three times. I can see that there are a group of green pines on the back-right tile and a house on the front-right tile, which matches the description in the guide exactly. According to the next step in the guide, I need to turn left to face west. Since I'm currently facing north, turning left once will do it.]
Observation: OK.

Action: turn left
Observation: You can see the 3x3 tiles surrounding you:
There is a group of green pines on the back-left tile.
There is a house on the back-right tile.
The front, front-right, left, back tiles are roads that you can step on.
Direction: You are facing west.

Action: think[According to the fourth step in the guide, I need to move forward two tiles westward to approach the destination. So my next two actions will be to move forward twice.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
The destination is on the front-right tile.
The front, right, back-left, back tiles are roads that you can step on.
Direction: You are facing west.

Action: forward
Observation: Task completed successfully."""

nav_turns_obs =  """
Important: To assist you in this task, we provide a guide to find the destination.
Key Rules:
1. When given an instruction like "Head [Direction], then take the N-th [Turn]" or "Continue going [Direction]; turn [Turn] at the 1st opportunity", you must proceed forward along the path in that direction first. Do NOT turn immediately at the intersection you just turned into.
2. A turn (turn left / turn right) can ONLY be executed when the tile directly to your left or right is listed as a road that you can step on. If only the diagonal tile ("front-left" or "front-right") is a road, the turn is 1 tile ahead—you MUST take the "forward" action first to enter the intersection before turning!

Step-by-Step Guide to Complete the Task:
From your current location and direction, if you want to go to the destination, you can:
Step 1. Head east; turn right at the 1st opportunity. At the intersection you will see a cluster of red lantern trees that spans the front, front-right tiles and a green tree with a hollow trunk on the back-right tile.
Step 2. Walk towards south; turn left at the 1st opportunity. At the intersection you will see a cluster of green firs that spans the right, back-right tiles and a house that spans the front-right, right tiles.
Step 3. Continue forward — your goal is right after the 1st intersection.

Observation: You can see the 3x3 tiles surrounding you:
The front-left, front, front-right, back tiles are roads that you can step on.
There is a green tree with a hollow trunk that spans the right, back-right tiles.
There is a orange tree with a hollow trunk that spans the left, back-left tiles.
Direction: You are facing east.

Action: think[I am facing east. According to Step 1, I need to head east and turn right at the 1st opportunity, where I should see red lantern trees ahead and a green tree with a hollow trunk on the back-right. The direct right tile is not a road, so the turn is 1 tile ahead. According to Rule 2, I must move forward first to enter the intersection.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a cluster of red lantern trees that spans the front, front-right tiles.
There is a group of four orange conical trees with smaller red trees among them on the front-right tile.
The front-left, left, right, back tiles are roads that you can step on.
There is a green tree with a hollow trunk on the back-right tile.
There is a orange tree with a hollow trunk on the back-left tile.
Direction: You are facing east.

Action: think[The tile directly to my right is now a road, and the landmarks match Step 1's description of the intersection (red lantern trees on front/front-right, green tree with hollow trunk on back-right). This is the 1st opportunity to turn right, so I will turn right to face south.]
Observation: OK.

Action: turn right
Observation: You can see the 3x3 tiles surrounding you:
There is a cluster of red lantern trees that spans the front-left, left tiles.
There is a group of four orange conical trees with smaller red trees among them on the front-left tile.
The front, right, back-left, back tiles are roads that you can step on.
There is a green tree with a hollow trunk on the front-right tile.
There is a orange tree with a hollow trunk on the back-right tile.
Direction: You are facing south.

Action: think[I am now facing south. Step 2 says to walk towards south and turn left at the 1st opportunity. Following Rule 1, I must proceed forward along this path first rather than turning immediately. So I will move forward.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a cluster of green firs on the front-right tile.
There is a cluster of red lantern trees that spans the left, back-left tiles.
There is a group of four orange conical trees with smaller red trees among them that spans the front-left, left tiles.
The front, back, back-right tiles are roads that you can step on.
There is a green tree with a hollow trunk that spans the front-right, right tiles.
Direction: You are facing south.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a cluster of green firs that spans the front-right, right tiles.
There is a cluster of red lantern trees on the back-left tile.
There is a group of four orange conical trees with smaller red trees among them that spans the left, back-left tiles.
The front, back tiles are roads that you can step on.
There is a green tree with a hollow trunk that spans the right, back-right tiles.
Direction: You are facing south.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a cluster of green firs that spans the front-right, right, back-right tiles.
There is a group of four orange conical trees with smaller red trees among them on the back-left tile.
There is a house on the front-right tile.
The front-left, front, back tiles are roads that you can step on.
There is a green tree with a hollow trunk on the back-right tile.
Direction: You are facing south.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a cluster of green firs that spans the right, back-right tiles.
There is a house that spans the front-right, right tiles.
The left, back tiles are roads that you can step on.
Direction: You are facing south.

Action: think[The tile directly to my left is now a road, and the landmarks match Step 2's description of the intersection (green firs on right/back-right, house on front-right/right). This is the 1st opportunity to turn left, so I will turn left to face east.]
Observation: OK.

Action: turn left
Observation: You can see the 3x3 tiles surrounding you:
There is a cluster of green firs that spans the back-left, back tiles.
There is a house that spans the back, back-right tiles.
The front, left tiles are roads that you can step on.
Direction: You are facing east.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a cluster of two rounded red bushy trees alongside a cone-shaped tree on the front-left tile.
The front, front-right, back-left, back tiles are roads that you can step on.
Direction: You are facing east.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
The destination is on the front-right tile.
There is a cluster of two rounded red bushy trees alongside a cone-shaped tree that spans the front-left, left tiles.
There is a house on the front-left tile.
The front, right, back tiles are roads that you can step on.
Direction: You are facing east.

Action: think[I have reached the 1st intersection and can see the destination on the front-right tile. According to Step 3, the goal is right after the 1st intersection, so I will move forward to reach it.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
The destination spans the front-right, right tiles.
There is a cluster of two rounded red bushy trees alongside a cone-shaped tree that spans the left, back-left tiles.
There is a house that spans the front-left, left tiles.
The front, back, back-right tiles are roads that you can step on.
Direction: You are facing east.

Observation: Task completed successfully.
"""