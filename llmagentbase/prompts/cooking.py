cook_instruction = """In this task, you are a chef in a restaurant. You will be asked to cook some dishes for the customers. Some needed ingredients are already stored at the restaurant, but some are not. Therfore, you need to gather all needed ingredients at farm, store, and harbor, and then go back to the restaurant to cook the dish(es) in kitchen, with the goal of generating actions to complete all required dishes.
At each time step, you will be provided with the following inputs:
1. The result of your latest action.

You can only issue the following actions in this environment, one at a time:
    goto <location> -> You can go to restaurant, farm, store, and harbor_<id>, where harbor id includes 1, 2, 3.
    harvest <crop>
    fish <seafood>
    buy <ingredient>
    put <ingredient> into <tool> -> <tool> includes cooking tools, cutting_board, and plate_<id>.
    chop <ingredient>
    wait -> Use this when you have nothing more to do but some <tool> hasn't finish cooking.
    plate from <tool> into plate_<id> -> You can only plate into a plate, not including other cooking tools.
    serve plate_<id> -> Use this after you finish a dish in a plate.
    think[...] -> Use this to reason about your next move. Add any internal thoughts or planning here.

Here is some other instructions:
1. You can only perform one action at a time. You must exacly follow the pattern specied below.
2. When you mention an ingredient, be clear. For example, say "raw,chopped lettuce" instead of "raw lettuce" or "chopped lettuce" or "lettuce".
3. You have 10 plates in the kitchen (plate_0~plate_9).
4. A dish must have one of the two possible kinds of sensonings, during_cooking and after_cooking. For during_cooking seasonings, you can only add them when the ingredients are still in the cooking tools (not plated yet). For after_cooking ones, you can only add them to the plates, i.e. the ingredients are already plated.
5. If you successfully complete a dish, you will be told that the plate contains the dish. Otherwise, all the ingredients in the plate will be listed. Therefore, you can only assume that you complete a dish if you are told the plate contains <dish name>.
6. All dishes must be cooked at the restaurant.
"""

# 5. You don't need to serve a dish. You will directly get the reward after all ingredients are plated.



cook_react_none = """
Observation: Incoming order! Please make 1 dishes: 1 serving of **taco (Smoky Lime)**, filled with chicken, lettuce, and shrimps.
The desired fried rice is a dish made with grilled tortillas, pan-fried chicken, pan-fried shrimp, raw and chopped lettuce. The dish is seasoned during cooking with olive oil, paprika, cumin, lime juice.

You are now in the kitchen of your restaurant.
In the fridge, you see: raw tortillas.
In the cabinet, you see: olive oil; lime juice.
There are 5 cooking tools in the environment:
- pan_0, pan_1 are both empty. Capacity: 0/4.
- cutting_board, grill_0, grill_1 are all empty. Capacity: 0/1.
You're not carrying anything right now.

Action: think[First, I need to gather all the ingredients. I already have tortillas, olive oil, lime juice in the kitchen. I still need lettuce, shrimp, chicken, cumin, paprika. I will visit farm, store, harbor one by one to get these ingredients. First, I will go to the farm.]
Observation: OK.

Action: goto farm
Observation: You are at the farm. In the farm, you see ripe lettuce, corn, and carrots.
You're not carrying anything right now.

Action: think[Among all the crops in the farm, lettuce is an ingredient I need. I will harvest the lettuce.]
Observation: OK.

Action: harvest lettuce
Observation: You harvested all the lettuce!
You have some: raw lettuce with you.

Action: think[I now have the lettuce. I still need shrimp, chicken, cumin, paprika. Next, I will go to the store.]
Observation: OK.

Action: goto store
Observation: In the store, you see raw chicken; paprika; cumin; raw flour; raw peas; raw scallops; raw rice; raw beef in stock.
You have some: raw lettuce with you.

Action: think[Among all the ingredients in the store, raw chicken, paprika, cumin are the ingredients I need. I will buy them one by one.]
Observation: OK.

Action: buy raw chicken
Observation: You successfully bought some raw chicken.
You have some: raw lettuce, raw chicken with you.

Action: buy paprika
Observation: You successfully bought some paprika.
You have some: raw lettuce, raw chicken, paprika with you.

Action: buy cumin
Observation: You successfully bought some cumin.
You have some: raw lettuce, raw chicken, paprika, cumin with you.

Action: think[I now have raw chicken, paprika. cumin. I still need shrimps. Next, I will go to the harbor to get shrimps. There are three harbors. I don't know which ones are available. I will first try to go to harbor_1.]
Observation: OK.

Action: goto harbor_1
Observation: Fishing spot harbor_1 is currently taken by other people.

Action: fish shrimp
Observation: You pulled up some scallops instead.

Action: fish shrimp
Observation: You reeled in some fresh shrimps!
You have some: raw lettuce, raw chicken, paprika, cumin, raw shrimps with you.

Action: think[I successfully got raw shrimps. Now I have all the ingredients I need. I can go back to the restaurant to cook the dish.]
Observation: OK.

Action: goto restaurant
Observation: You are now in the kitchen of your restaurant. You restock the fridge with raw lettuce; raw chicken; raw shrimps. 
You restock the cabinet with paprika; cumin. 
You are now in the kitchen of your restaurant.
In the fridge, you see: raw tortillas; raw lettuce; raw chicken; raw shrimps.
In the cabinet, you see: olive oil; lime juice; paprika; cumin.
There are 5 cooking tools in the environment:
- pan_0, pan_1 are both empty. Capacity: 0/4.
- cutting_board, grill_0, grill_1 are all empty. Capacity: 0/1.
You're not carrying anything right now.

Action: think[Now I'm at restaurant, ready to cook. The first cooking step is: grill the tortillas; then chop the lettuce. First, I will put the raw tortilla into grill_0 to grill it.]
Observation: OK.

Action: put raw tortillas into grill_0
Observation: You put raw tortilla into the grill_0. Please wait for 2 timesteps for it to be cooked.

Action: think[Next I will complete the second half of cooking step 1 is to chop the lettuce.]
Observation: OK.

Action: chop raw lettuce
Observation: You chopped the lettuce on the cutting board. cutting board now holds: raw,chopped lettuce.

Action: think[Now I have finished cooking step 1. I will continue with cooking step 2: pan-fry the shrimps, chicken. I will put them into pan_0 one by one to pan-fry them.]
Observation: OK.

Action: put raw shrimps into pan_0
Observation: You put raw shrimp into the pan_0. Please wait for 3 timesteps for it to be cooked.
grill_0 finished cooking your one serving of grilled tortilla.

Action: put raw chicken into pan_0
Observation: You put raw chicken into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: think[Now I will add olive oil, paprika, cumin, lime juice on the pan. These are all during_cooking seasonings, so I can add them now (despite that pan_0 hasn't finished cooking). I will put them into pan_0 one by one.]
Observation: OK.

Action: put olive oil into pan_0
Observation: You put olive oil into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put paprika into pan_0
Observation: You put paprika into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put cumin into pan_0
Observation: You put cumin into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put lime juice into pan_0
Observation: You put lime juice into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: think[Now I will wait for all ingredients to finish cooking, then assemble all the ingredients from the cutting_board, grill, pan onto the same plate. I will use plate_0. According to the latest observation, I need to wait 3 timesteps until pan_0 finished baking. I will first plate from cutting_board and grill_0, and finally pan_0.]
Observation: OK.

Action: plate from cutting_board into plate_0
Observation: You plated all cooked ingredients from cutting_board into plate_0. plate_0: a plated dish with 1 serving of raw, chopped lettuce without any seasoning.

Action: plate from grill_0 into plate_0
Observation: You plated all cooked ingredients from grill_0 into plate_0. plate_0: a plated dish with 1 serving of raw, chopped lettuce without any seasoning; 1 serving of grilled tortilla without any seasoning.

Action: plate from pan_0 into plate_0
Observation: pan_0 is still cooking. Wait until the food is ready before plating.

Action: think[pan_0 hasn't finished cooking. I will wait for a timestep, and then try to plate it again.]
Observation: OK.

Action: wait
Observation: 1 timestep has passed.

Action: plate from pan_0 into plate_0
Observation 39: You plated all cooked ingredients from pan_0 into plate_0. plate_0: A successfully prepared serving of the requested **taco (Smoky Lime)**.

Action: think[I have finished **taco (Smoky Lime)**. I will serve it.]
Observation: OK.

Action: serve plate_0
Observation: Successfully served plate_0. This is a successful serving of **taco (Smoky Lime)**, filled with chicken, lettuce, and shrimps.
"""

cook_react = """
Here is one example with recipe:
recipe for 1 serving of **taco (Smoky Lime)**
### Ingredients:
raw chicken x 1 serving, raw lettuce x 1 serving, raw shrimps x 1 serving, raw tortillas x 1 serving.
### Seasonings:
Add during cooking: cumin, lime juice, olive oil, paprika.
### Cooking Steps:
- grill the raw tortillas; then chop the raw lettuce.
- pan-fry the raw shrimp, raw chicken.
- add olive oil, paprika, cumin, lime juice on the pan.
- wait for all ingredients to finish cooking, then assemble all the ingredients from the cutting_board, grill, pan onto the same plate.

Observation: Incoming order! Please make 1 dishes: 1 serving of **taco (Smoky Lime)**, filled with chicken, lettuce, and shrimps.
You are now in the kitchen of your restaurant.
In the fridge, you see: raw tortillas.
In the cabinet, you see: olive oil; lime juice.
There are 5 cooking tools in the environment:
- pan_0, pan_1 are both empty. Capacity: 0/4.
- cutting_board, grill_0, grill_1 are all empty. Capacity: 0/1.
You're not carrying anything right now.

Action: think[First, I need to gather all the ingredients. I already have tortillas, olive oil, lime juice in the kitchen. I still need lettuce, shrimp, chicken, cumin, paprika. I will visit farm, store, harbor one by one to get these ingredients. First, I will go to the farm.]
Observation: OK.

Action: goto farm
Observation: You are at the farm. In the farm, you see ripe lettuce, corn, and carrots.
You're not carrying anything right now.

Action: think[Among all the crops in the farm, lettuce is an ingredient I need. I will harvest the lettuce.]
Observation: OK.

Action: harvest lettuce
Observation: You harvested all the lettuce!
You have some: raw lettuce with you.

Action: think[I now have the lettuce. I still need shrimp, chicken, cumin, paprika. Next, I will go to the store.]
Observation: OK.

Action: goto store
Observation: In the store, you see raw chicken; paprika; cumin; raw flour; raw peas; raw scallops; raw rice; raw beef in stock.
You have some: raw lettuce with you.

Action: think[Among all the ingredients in the store, raw chicken, paprika, cumin are the ingredients I need. I will buy them one by one.]
Observation: OK.

Action: buy raw chicken
Observation: You successfully bought some raw chicken.
You have some: raw lettuce, raw chicken with you.

Action: buy paprika
Observation: You successfully bought some paprika.
You have some: raw lettuce, raw chicken, paprika with you.

Action: buy cumin
Observation: You successfully bought some cumin.
You have some: raw lettuce, raw chicken, paprika, cumin with you.

Action: think[I now have raw chicken, paprika. cumin. I still need shrimps. Next, I will go to the harbor to get shrimps. There are three harbors. I don't know which ones are available. I will first try to go to harbor_1.]
Observation: OK.

Action: goto harbor_1
Observation: Fishing spot harbor_1 is currently taken by other people.

Action: think[Fishing spot harbor_1 is occupied. Next, I will try harbor_2.]
Observation: OK.

Action: goto harbor_2
Observation: You walk to harbor_2. The spot is free, and you can get ready to fish here.
You have some: raw lettuce, raw chicken, paprika, cumin with you.

Action: think[I can fish at harbor_2. I will start fishing the seafood I need, which is shrimp.]
Observation: OK.

Action: fish shrimp
Observation: You pulled up some scallops instead.

Action: think[I got a wrong kind of seafood. I still need to fish shrimp. I will try again.]
Observation: OK.

Action: fish shrimp
Observation: You reeled in some fresh shrimps!
You have some: raw lettuce, raw chicken, paprika, cumin, raw shrimps with you.

Action: think[I successfully got raw shrimps. Now I have all the ingredients I need. I can go back to the restaurant to cook the dish.]
Observation: OK.

Action: goto restaurant
Observation: You are now in the kitchen of your restaurant. You restock the fridge with raw lettuce; raw chicken; raw shrimps. 
You restock the cabinet with paprika; cumin. 
You are now in the kitchen of your restaurant.
In the fridge, you see: raw tortillas; raw lettuce; raw chicken; raw shrimps.
In the cabinet, you see: olive oil; lime juice; paprika; cumin.
There are 5 cooking tools in the environment:
- pan_0, pan_1 are both empty. Capacity: 0/4.
- cutting_board, grill_0, grill_1 are all empty. Capacity: 0/1.
You're not carrying anything right now.

Action: think[Now I'm at restaurant, ready to cook. The first cooking step is: grill the tortillas; then chop the lettuce. First, I will put the raw tortilla into grill_0 to grill it.]
Observation: OK.

Action: put raw tortillas into grill_0
Observation: You put raw tortilla into the grill_0. Please wait for 2 timesteps for it to be cooked.

Action: think[Next I will complete the second half of cooking step 1 is to chop the lettuce.]
Observation: OK.

Action: chop raw lettuce
Observation: You chopped the lettuce on the cutting board. cutting board now holds: raw,chopped lettuce.

Action: think[Now I have finished cooking step 1. I will continue with cooking step 2: pan-fry the shrimps, chicken. I will put them into pan_0 one by one to pan-fry them.]
Observation: OK.

Action: put raw shrimps into pan_0
Observation: You put raw shrimp into the pan_0. Please wait for 3 timesteps for it to be cooked.
grill_0 finished cooking your one serving of grilled tortilla.

Action: put raw chicken into pan_0
Observation: You put raw chicken into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: think[I have finished cooking step 2. I will move to cooking step 3: add olive oil, paprika, cumin, lime juice on the pan. These are all during_cooking seasonings, so I can add them now (despite that pan_0 hasn't finished cooking). I will put them into pan_0 one by one.]
Observation: OK.

Action: put olive oil into pan_0
Observation: You put olive oil into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put paprika into pan_0
Observation: You put paprika into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put cumin into pan_0
Observation: You put cumin into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put lime juice into pan_0
Observation: You put lime juice into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: think[I have finished cooking step 3. I will move to cooking step 4: wait for all ingredients to finish cooking, then assemble all the ingredients from the cutting_board, grill, pan onto the same plate. I will use plate_0. According to the latest observation, I need to wait 3 timesteps until pan_0 finished baking. I will first plate from cutting_board and grill_0, and finally pan_0.]
Observation: OK.

Action: plate from cutting_board into plate_0
Observation: You plated all cooked ingredients from cutting_board into plate_0. plate_0: a plated dish with 1 serving of raw, chopped lettuce without any seasoning.

Action: plate from grill_0 into plate_0
Observation: You plated all cooked ingredients from grill_0 into plate_0. plate_0: a plated dish with 1 serving of raw, chopped lettuce without any seasoning; 1 serving of grilled tortilla without any seasoning.

Action: plate from pan_0 into plate_0
Observation: pan_0 is still cooking. Wait until the food is ready before plating.

Action: think[pan_0 hasn't finished cooking. I will wait for a timestep, and then try to plate it again.]
Observation: OK.

Action: wait
Observation: 1 timestep has passed.

Action: plate from pan_0 into plate_0
Observation 39: You plated all cooked ingredients from pan_0 into plate_0. plate_0: A successfully prepared serving of the requested **taco (Smoky Lime)**.

Action: think[I have finished **taco (Smoky Lime)**. I will serve it.]
Observation: OK.

Action: serve plate_0
Observation: Successfully served plate_0. This is a successful serving of **taco (Smoky Lime)**, filled with chicken, lettuce, and shrimps.
"""

cook_react_perfect = """
Here is one example with recipe:
recipe for 1 serving of **taco (Smoky Lime)**
### Ingredients:
raw chicken x 1 serving, raw lettuce x 1 serving, raw shrimps x 1 serving, raw tortillas x 1 serving.
### Seasonings:
Add during cooking: cumin, lime juice, olive oil, paprika.
### Cooking Steps:
- grill the tortillas; then chop the lettuce.
- pan-fry the shrimps, chicken.
- add olive oil, paprika, cumin, lime juice on the pan.
- wait for all ingredients to finish cooking, then assemble all the ingredients from the cutting_board, grill, pan onto the same plate.
### You'll need to collect ingredients from the following locations:
**Farm**: lettuce
**Harbor**: shrimp
**Store**: chicken, cumin, paprika

Observation: Incoming order! Please make 1 dishes: 1 serving of **taco (Smoky Lime)**, filled with chicken, lettuce, and shrimps.
You are now in the kitchen of your restaurant.
In the fridge, you see: raw tortillas.
In the cabinet, you see: olive oil; lime juice.
There are 5 cooking tools in the environment:
- pan_0, pan_1 are both empty. Capacity: 0/4.
- cutting_board, grill_0, grill_1 are all empty. Capacity: 0/1.
You're not carrying anything right now.

Action: think[First, I need to gather all the ingredients. I already have tortillas, olive oil, lime juice in the kitchen. I still need lettuce, shrimp, chicken, cumin, paprika. I am told the locations of these needed ingredients: lettuce at the farm, shrimp at the harbor, and chicken, cumin, paprika at the store. I will visit these locations one by one to get these ingredients. First, I will go to the farm for lettuce.]
Observation: OK.

Action: goto farm
Observation: You are at the farm. In the farm, you see ripe lettuce, corn, and carrots.
You're not carrying anything right now.

Action: think[I will harvest the lettuce.]
Observation: OK.

Action: harvest lettuce
Observation: You harvested all the lettuce!
You have some: raw lettuce with you.

Action: think[I now have the lettuce. Next, I will go to the store to get chicken, cumin, paprika.]
Observation: OK.

Action: goto store
Observation: In the store, you see raw chicken; paprika; cumin; raw flour; raw peas; raw scallops; raw rice; raw beef in stock.
You have some: raw lettuce with you.

Action: think[I will buy raw chicken, paprika, cumin one by one.]
Observation: OK.

Action: buy raw chicken
Observation: You successfully bought some raw chicken.
You have some: raw lettuce, raw chicken with you.

Action: buy paprika
Observation: You successfully bought some paprika.
You have some: raw lettuce, raw chicken, paprika with you.

Action: buy cumin
Observation: You successfully bought some cumin.
You have some: raw lettuce, raw chicken, paprika, cumin with you.

Action: think[I now have raw chicken, paprika. cumin. Next, I will go to the harbor to get shrimps. There are three harbors. I don't know which ones are available. I will first try to go to harbor_1.]
Observation: OK.

Action: goto harbor_1
Observation: Fishing spot harbor_1 is currently taken by other people.

Action: think[Fishing spot harbor_1 is occupied. Next, I will try harbor_2.]
Observation: OK.

Action: goto harbor_2
Observation: You walk to harbor_2. The spot is free, and you can get ready to fish here.
You have some: raw lettuce, raw chicken, paprika, cumin with you.

Action: think[I can fish at harbor_2. I will start fishing the seafood I need, which is shrimp.]
Observation: OK.

Action: fish shrimp
Observation: You pulled up some scallops instead.

Action: think[I got a wrong kind of seafood. I still need to fish shrimp. I will try again.]
Observation: OK.

Action: fish shrimp
Observation: You reeled in some fresh shrimps!
You have some: raw lettuce, raw chicken, paprika, cumin, raw shrimps with you.

Action: think[I successfully got raw shrimps. Now I have all the ingredients I need. I can go back to the restaurant to cook the dish.]
Observation: OK.

Action: goto restaurant
Observation: You are now in the kitchen of your restaurant. You restock the fridge with raw lettuce; raw chicken; raw shrimps. 
You restock the cabinet with paprika; cumin. 
You are now in the kitchen of your restaurant.
In the fridge, you see: raw tortillas; raw lettuce; raw chicken; raw shrimps.
In the cabinet, you see: olive oil; lime juice; paprika; cumin.
There are 5 cooking tools in the environment:
- pan_0, pan_1 are both empty. Capacity: 0/4.
- cutting_board, grill_0, grill_1 are all empty. Capacity: 0/1.
You're not carrying anything right now.

Action: think[Now I'm at restaurant, ready to cook. The first cooking step is: grill the tortillas; then chop the lettuce. First, I will put the raw tortilla into grill_0 to grill it.]
Observation: OK.

Action: put raw tortillas into grill_0
Observation: You put raw tortilla into the grill_0. Please wait for 2 timesteps for it to be cooked.

Action: think[Next I will complete the second half of cooking step 1 is to chop the lettuce.]
Observation: OK.

Action: chop raw lettuce
Observation: You chopped the lettuce on the cutting board. cutting board now holds: raw,chopped lettuce.

Action: think[Now I have finished cooking step 1. I will continue with cooking step 2: pan-fry the shrimps, chicken. I will put them into pan_0 one by one to pan-fry them.]
Observation: OK.

Action: put raw shrimps into pan_0
Observation: You put raw shrimp into the pan_0. Please wait for 3 timesteps for it to be cooked.
grill_0 finished cooking your one serving of grilled tortilla.

Action: put raw chicken into pan_0
Observation: You put raw chicken into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: think[I have finished cooking step 2. I will move to cooking step 3: add olive oil, paprika, cumin, lime juice on the pan. These are all during_cooking seasonings, so I can add them now (despite that pan_0 hasn't finished cooking). I will put them into pan_0 one by one.]
Observatoin: OK.

Action: put olive oil into pan_0
Observatio: You put olive oil into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put paprika into pan_0
Observation: You put paprika into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put cumin into pan_0
Observation: You put cumin into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put lime juice into pan_0
Observatio: You put lime juice into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: think[I have finished cooking step 3. I will move to cooking step 4: wait for all ingredients to finish cooking, then assemble all the ingredients from the cutting_board, grill, pan onto the same plate. I will use plate_0. According to the latest observation, I need to wait 3 timesteps until pan_0 finished baking. I will first plate from cutting_board and grill_0, and finally pan_0.]
Observation: OK.

Action: plate from cutting_board into plate_0
Observation: You plated all cooked ingredients from cutting_board into plate_0. plate_0: a plated dish with 1 serving of raw, chopped lettuce without any seasoning.

Action: plate from grill_0 into plate_0
Observation: You plated all cooked ingredients from grill_0 into plate_0. plate_0: a plated dish with 1 serving of raw, chopped lettuce without any seasoning; 1 serving of grilled tortilla without any seasoning.

Action: plate from pan_0 into plate_0
Observation: pan_0 is still cooking. Wait until the food is ready before plating.

Action: think[pan_0 hasn't finished cooking. I will wait for a timestep, and then try to plate it again.]
Observation: OK.

Action: wait
Observation: 1 timestep has passed.

Action: plate from pan_0 into plate_0
Observation: You plated all cooked ingredients from pan_0 into plate_0. plate_0: A successfully prepared serving of the requested **taco (Smoky Lime)**.

Action: think[plate_0 is now filled with one serving of completed **taco (Smoky Lime)**. I can serve plate_0 now.]
Observation: OK.

Action: serve plate_0
Observation: Successfully served plate_0. This is a successful serving of **taco (Smoky Lime)**, filled with chicken, lettuce, and shrimps.
"""

cook_react_descriptive = """
Here is one example with recipe:
recipe for 1 serving of **taco (Smoky Lime)**
### Ingredients:
raw chicken x 1 serving, raw lettuce x 1 serving, raw shrimps x 1 serving, raw tortillas x 1 serving.
### Seasonings:
Add during cooking: cumin, lime juice, olive oil, paprika.
### Cooking Steps:
- grill the raw tortillas; then chop the raw lettuce.
- pan-fry the raw shrimp, raw chicken.
- add olive oil, paprika, cumin, lime juice on the pan.
- wait for all ingredients to finish cooking, then assemble all the ingredients from the cutting_board, grill, pan onto the same plate.
### You'll need to collect ingredients from the following locations:
**Farm**: lettuce
**Harbor_2**: shrimp
**Store**: chicken, cumin, paprika

Observation: Incoming order! Please make 1 dishes: 1 serving of **taco (Smoky Lime)**, filled with chicken, lettuce, and shrimps.
You are now in the kitchen of your restaurant.
In the fridge, you see: raw tortillas.
In the cabinet, you see: olive oil; lime juice.
There are 5 cooking tools in the environment:
- pan_0, pan_1 are both empty. Capacity: 0/4.
- cutting_board, grill_0, grill_1 are all empty. Capacity: 0/1.
You're not carrying anything right now.

Action: think[First, I need to gather all the ingredients. I already have tortillas, olive oil, lime juice in the kitchen. I still need lettuce, shrimp, chicken, cumin, paprika. I am told the locations of these needed ingredients: lettuce at the farm, shrimp at the harbor_2, and chicken, cumin, paprika at the store. I will visit these locations one by one to get these ingredients. First, I will go to the farm for lettuce.]
Observation: OK.

Action: goto farm
Observation: You are at the farm. In the farm, you see ripe lettuce, corn, and carrots.
You're not carrying anything right now.

Action: think[I will harvest the lettuce.]
Observation: OK.

Action: harvest lettuce
Observation: You harvested all the lettuce!
You have some: raw lettuce with you.

Action: think[I now have the lettuce. Next, I will go to the store to get chicken, cumin, paprika.]
Observation: OK.

Action: goto store
Observation: In the store, you see raw chicken; paprika; cumin; raw flour; raw peas; raw scallops; raw rice; raw beef in stock.
You have some: raw lettuce with you.

Action: think[I will buy raw chicken, paprika, cumin one by one.]
Observation: OK.

Action: buy raw chicken
Observation: You successfully bought some raw chicken.
You have some: raw lettuce, raw chicken with you.

Action: buy paprika
Observation: You successfully bought some paprika.
You have some: raw lettuce, raw chicken, paprika with you.

Action: buy cumin
Observation: You successfully bought some cumin.
You have some: raw lettuce, raw chicken, paprika, cumin with you.

Action: think[I now have raw chicken, paprika. cumin. Next, I will go to the harbor_2 to get shrimps.]
Observation: OK.

Action: goto harbor_2
Observation: You walk to harbor_2. The spot is free, and you can get ready to fish here.
You have some: raw lettuce, raw chicken, paprika, cumin with you.

Action: think[I can fish at harbor_2. I will start fishing the seafood I need, which is shrimp.]
Observation: OK.

Action: fish shrimp
Observation: You pulled up some scallops instead.

Action: think[I got a wrong kind of seafood. I still need to fish shrimp. I will try again.]
Observation: OK.

Action: fish shrimp
Observation: You reeled in some fresh shrimps!
You have some: raw lettuce, raw chicken, paprika, cumin, raw shrimps with you.

Action: think[I successfully got raw shrimps. Now I have all the ingredients I need. I can go back to the restaurant to cook the dish.]
Observation: OK.

Action: goto restaurant
Observation: You are now in the kitchen of your restaurant. You restock the fridge with raw lettuce; raw chicken; raw shrimps. 
You restock the cabinet with paprika; cumin. 
You are now in the kitchen of your restaurant.
In the fridge, you see: raw tortillas; raw lettuce; raw chicken; raw shrimps.
In the cabinet, you see: olive oil; lime juice; paprika; cumin.
There are 5 cooking tools in the environment:
- pan_0, pan_1 are both empty. Capacity: 0/4.
- cutting_board, grill_0, grill_1 are all empty. Capacity: 0/1.
You're not carrying anything right now.

Action: think[Now I'm at restaurant, ready to cook. The first cooking step is: grill the tortillas; then chop the lettuce. First, I will put the raw tortilla into grill_0 to grill it.]
Observation: OK.

Action: put raw tortillas into grill_0
Observation: You put raw tortilla into the grill_0. Please wait for 2 timesteps for it to be cooked.

Action: think[Next I will complete the second half of cooking step 1 is to chop the lettuce.]
Observation: OK.

Action: chop raw lettuce
Observation: You chopped the lettuce on the cutting board. cutting board now holds: raw,chopped lettuce.

Action: think[Now I have finished cooking step 1. I will continue with cooking step 2: pan-fry the raw shrimp, raw chicken. I will put them into pan_0 one by one to pan-fry them.]
Observation: OK.

Action: put raw shrimps into pan_0
Observation: You put raw shrimp into the pan_0. Please wait for 3 timesteps for it to be cooked.
grill_0 finished cooking your one serving of grilled tortilla.

Action: put raw chicken into pan_0
Observation: You put raw chicken into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: think[I have finished cooking step 2. I will move to cooking step 3: add olive oil, paprika, cumin, lime juice on the pan. These are all during_cooking seasonings, so I can add them now (despite that pan_0 hasn't finished cooking). I will put them into pan_0 one by one.]
Observation: OK.

Action: put olive oil into pan_0
Observation: You put olive oil into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put paprika into pan_0
Observation: You put paprika into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put cumin into pan_0
Observation: You put cumin into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put lime juice into pan_0
Observation: You put lime juice into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: think[I have finished cooking step 3. I will move to cooking step 4: wait for all ingredients to finish cooking, then assemble all the ingredients from the cutting_board, grill, pan onto the same plate. I will use plate_0. According to the latest observation, I need to wait 3 timesteps until pan_0 finished baking. I will first plate from cutting_board and grill_0, and finally pan_0.]
Observation: OK.

Action: plate from cutting_board into plate_0
Observation: You plated all cooked ingredients from cutting_board into plate_0. plate_0: a plated dish with 1 serving of raw, chopped lettuce without any seasoning.

Action: plate from grill_0 into plate_0
Observation: You plated all cooked ingredients from grill_0 into plate_0. plate_0: a plated dish with 1 serving of raw, chopped lettuce without any seasoning; 1 serving of grilled tortilla without any seasoning.

Action: plate from pan_0 into plate_0
Observation: pan_0 is still cooking. Wait until the food is ready before plating.

Action: think[pan_0 hasn't finished cooking. I will wait for a timestep, and then try to plate it again.]
Observation: OK.

Action: wait
Observation: 1 timestep has passed.

Action: plate from pan_0 into plate_0
Observation: You plated all cooked ingredients from pan_0 into plate_0. plate_0: A successfully prepared serving of the requested **taco (Smoky Lime)**.

Action: think[plate_0 is now filled with one serving of completed **taco (Smoky Lime)**. I can serve plate_0 now.]
Observation: OK.

Action: serve plate_0
Observation: Successfully served plate_0. This is a successful serving of **taco (Smoky Lime)**, filled with chicken, lettuce, and shrimps.
"""

cook_react_multiserve = """
Here is one example with recipe:
recipe for 1 serving of **taco (Smoky Lime)**
### Ingredients:
raw chicken x 1 serving, raw lettuce x 1 serving, raw shrimps x 1 serving, raw tortillas x 1 serving.
### Seasonings:
Add during cooking: cumin, lime juice, olive oil, paprika.
### Cooking Steps:
- grill the raw tortillas; then chop the raw lettuce.
- pan-fry the raw shrimp, raw chicken.
- add olive oil, paprika, cumin, lime juice on the pan.
- wait for all ingredients to finish cooking, then assemble all the ingredients from the cutting_board, grill, pan onto the same plate.
### You'll need to collect ingredients from the following locations:
**Farm**: lettuce
**Harbor_2**: shrimp
**Store**: chicken, cumin, paprika

Observation: Incoming order! Please make 3 dishes: 3 servings of **taco (Smoky Lime)**, filled with chicken, lettuce, and shrimps.
You are now in the kitchen of your restaurant.
In the fridge, you see: raw tortillas.
In the cabinet, you see: olive oil; lime juice.
There are 5 cooking tools in the environment:
- pan_0, pan_1 are both empty. Capacity: 0/4.
- cutting_board, grill_0, grill_1 are all empty. Capacity: 0/1.
You're not carrying anything right now.

Action: think[First, I need to gather all the ingredients. I already have tortillas, olive oil, lime juice in the kitchen. I still need lettuce, shrimp, chicken, cumin, paprika. I am told the locations of these needed ingredients: lettuce at the farm, shrimp at the harbor_2, and chicken, cumin, paprika at the store. I will visit these locations one by one to get these ingredients. First, I will go to the farm for lettuce.]
Observation: OK.

Action: goto farm
Observation: You are at the farm. In the farm, you see ripe lettuce, corn, and carrots.
You're not carrying anything right now.

Action: think[I will harvest the lettuce.]
Observation: OK.

Action: harvest lettuce
Observation: You harvested all the lettuce!
You have some: raw lettuce with you.

Action: think[I now have the lettuce. Next, I will go to the store to get chicken, cumin, paprika.]
Observation: OK.

Action: goto store
Observation: In the store, you see raw chicken; paprika; cumin; raw flour; raw peas; raw scallops; raw rice; raw beef in stock.
You have some: raw lettuce with you.

Action: think[I will buy raw chicken, paprika, cumin one by one.]
Observation: OK.

Action: buy raw chicken
Observation: You successfully bought some raw chicken.
You have some: raw lettuce, raw chicken with you.

Action: buy paprika
Observation: You successfully bought some paprika.
You have some: raw lettuce, raw chicken, paprika with you.

Action: buy cumin
Observation: You successfully bought some cumin.
You have some: raw lettuce, raw chicken, paprika, cumin with you.

Action: think[I now have raw chicken, paprika. cumin. Next, I will go to the harbor_2 to get shrimps.]
Observation: OK.

Action: goto harbor_2
Observation: You walk to harbor_2. The spot is free, and you can get ready to fish here.
You have some: raw lettuce, raw chicken, paprika, cumin with you.

Action: think[I can fish at harbor_2. I will start fishing the seafood I need, which is shrimp.]
Observation: OK.

Action: fish shrimp
Observation: You pulled up some scallops instead.

Action: think[I got a wrong kind of seafood. I still need to fish shrimp. I will try again.]
Observation: OK.

Action: fish shrimp
Observation: You reeled in some fresh shrimps!
You have some: raw lettuce, raw chicken, paprika, cumin, raw shrimps with you.

Action: think[I successfully got raw shrimps. Now I have all the ingredients I need. I can go back to the restaurant to cook the dish.]
Observation: OK.

Action: goto restaurant
Observation: You are now in the kitchen of your restaurant. You restock the fridge with raw lettuce; raw chicken; raw shrimps. 
You restock the cabinet with paprika; cumin. 
You are now in the kitchen of your restaurant.
In the fridge, you see: raw tortillas; raw lettuce; raw chicken; raw shrimps.
In the cabinet, you see: olive oil; lime juice; paprika; cumin.
There are 5 cooking tools in the environment:
- pan_0, pan_1 are both empty. Capacity: 0/4.
- cutting_board, grill_0, grill_1 are all empty. Capacity: 0/1.
You're not carrying anything right now.

Action: think[Now I'm at restaurant, ready to cook. I will need to do 5 servings of the same dish. I will cook them one by one. Now start with the first serving. The first cooking step is: grill the tortillas; then chop the lettuce. First, I will put the raw tortilla into grill_0 to grill it.]
Observation: OK.

Action: put raw tortillas into grill_0
Observation: You put raw tortilla into the grill_0. Please wait for 2 timesteps for it to be cooked.

Action: think[Next I will complete the second half of cooking step 1 is to chop the lettuce.]
Observation: OK.

Action: chop raw lettuce
Observation: You chopped the lettuce on the cutting board. cutting board now holds: raw,chopped lettuce.

Action: think[Now I have finished cooking step 1. I will continue with cooking step 2: pan-fry the raw shrimp, raw chicken. I will put them into pan_0 one by one to pan-fry them.]
Observation: OK.

Action: put raw shrimps into pan_0
Observation: You put raw shrimp into the pan_0. Please wait for 3 timesteps for it to be cooked.
grill_0 finished cooking your one serving of grilled tortilla.

Action: put raw chicken into pan_0
Observation: You put raw chicken into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: think[I have finished cooking step 2. I will move to cooking step 3: add olive oil, paprika, cumin, lime juice on the pan. These are all during_cooking seasonings, so I can add them now (despite that pan_0 hasn't finished cooking). I will put them into pan_0 one by one.]
Observation: OK.

Action: put olive oil into pan_0
Observation: You put olive oil into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put paprika into pan_0
Observation: You put paprika into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put cumin into pan_0
Observation: You put cumin into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put lime juice into pan_0
Observation: You put lime juice into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: think[I have finished cooking step 3. I will move to cooking step 4: wait for all ingredients to finish cooking, then assemble all the ingredients from the cutting_board, grill, pan onto the same plate. I will use plate_0. According to the latest observation, I need to wait 3 timesteps until pan_0 finished baking. I will first plate from cutting_board and grill_0, and finally pan_0.]
Observation: OK.

Action: plate from cutting_board into plate_0
Observation: You plated all cooked ingredients from cutting_board into plate_0. plate_0: a plated dish with 1 serving of raw, chopped lettuce without any seasoning.

Action: plate from grill_0 into plate_0
Observation: You plated all cooked ingredients from grill_0 into plate_0. plate_0: a plated dish with 1 serving of raw, chopped lettuce without any seasoning; 1 serving of grilled tortilla without any seasoning.

Action: think[pan_0 hasn't finished cooking. I will wait for a timestep.]
Observation: OK.

Action: wait
Observation: pan_0 finished cooking your one serving of pan-fried chicken, pan-fried shrimp.

Action: think[pan_0 has finished cooking. I can plate from it now.]
Observation: OK.

Action: plate from pan_0 into plate_0
Observation: You plated all cooked ingredients from pan_0 into plate_0. plate_0: A successfully prepared serving of the requested **taco (Smoky Lime)**.

Action: think[plate_0 is now filled with one serving of completed **taco (Smoky Lime)**. I can serve plate_0 now.]
Observation: OK.

Action: serve plate_0
Observation: Successfully served plate_0. This is a successful serving of **taco (Smoky Lime)**, filled with chicken, lettuce, and shrimps.

Action: think[I have successfully served one serving of **taco (Smoky Lime)**. I need to do 2 more servings. Now start with the second serving. I will restart from cooking step 1: grill the raw tortillas; then chop the raw lettuce.]
Observation: OK.

Action: put raw tortillas into grill_0
Observation: You put raw tortilla into the grill_0. Please wait for 2 timesteps for it to be cooked.

Action: chop raw lettuce
Observation: You chopped the lettuce on the cutting board. cutting board now holds: raw,chopped lettuce.

Action: think[Now I have finished cooking step 1. I will continue with cooking step 2: pan-fry the raw shrimp, raw chicken.]
Observation: OK.

Action: put raw shrimps into pan_0
Observation: You put raw shrimp into the pan_0. Please wait for 3 timesteps for it to be cooked.
grill_0 finished cooking your one serving of grilled tortilla.

Action: put raw chicken into pan_0
Observation: You put raw chicken into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: think[I have finished cooking step 2. I will move to cooking step 3: add olive oil, paprika, cumin, lime juice on the pan.]
Observation: OK.

Action: put olive oil into pan_0
Observation: You put olive oil into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put paprika into pan_0
Observation: You put paprika into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put cumin into pan_0
Observation: You put cumin into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put lime juice into pan_0
Observation: You put lime juice into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: think[I have finished cooking step 3. I will move to cooking step 4: wait for all ingredients to finish cooking, then assemble all the ingredients from the cutting_board, grill, pan onto the same plate. Since plate_0 has been served, I will use plate_1.]
Observation: OK.

Action: plate from cutting_board into plate_1
Observation: You plated all cooked ingredients from cutting_board into plate_1. plate_1: a plated dish with 1 serving of raw, chopped lettuce without any seasoning.

Action: plate from grill_0 into plate_1
Observation: You plated all cooked ingredients from grill_0 into plate_1. plate_1: a plated dish with 1 serving of raw, chopped lettuce without any seasoning; 1 serving of grilled tortilla without any seasoning.

Action: wait
Observation: pan_0 finished cooking your one serving of pan-fried chicken, pan-fried shrimp.

Action: plate from pan_0 into plate_1
Observation: You plated all cooked ingredients from pan_0 into plate_1. plate_1: A successfully prepared serving of the requested **taco (Smoky Lime)**.

Action: serve plate_1
Observation: Successfully served plate_1. This is a successful serving of **taco (Smoky Lime)**, filled with chicken, lettuce, and shrimps.

Action: think[I have successfully served two servings of **taco (Smoky Lime)**. I need to do 1 more serving. Now start with the third serving. I will restart from cooking step 1: grill the raw tortillas; then chop the raw lettuce.]
Observation: OK.

Action: put raw tortillas into grill_0
Observation: You put raw tortilla into the grill_0. Please wait for 2 timesteps for it to be cooked.

Action: chop raw lettuce
Observation: You chopped the lettuce on the cutting board. cutting board now holds: raw,chopped lettuce.

Action: think[Now I have finished cooking step 1. I will continue with cooking step 2: pan-fry the raw shrimp, raw chicken.]
Observation: OK.

Action: put raw shrimps into pan_0
Observation: You put raw shrimp into the pan_0. Please wait for 3 timesteps for it to be cooked.
grill_0 finished cooking your one serving of grilled tortilla.

Action: put raw chicken into pan_0
Observation: You put raw chicken into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: think[I have finished cooking step 2. I will move to cooking step 3: add olive oil, paprika, cumin, lime juice on the pan.]
Observation: OK.

Action: put olive oil into pan_0
Observation: You put olive oil into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put paprika into pan_0
Observation: You put paprika into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put cumin into pan_0
Observation: You put cumin into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put lime juice into pan_0
Observation: You put lime juice into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: think[I have finished cooking step 3. I will move to cooking step 4: wait for all ingredients to finish cooking, then assemble all the ingredients from the cutting_board, grill, pan onto the same plate. Since plate_0 and plate_1 has been served, I will use plate_2.]
Observation: OK.

Action: plate from cutting_board into plate_2
Observation: You plated all cooked ingredients from cutting_board into plate_2. plate_2: a plated dish with 1 serving of raw, chopped lettuce without any seasoning.

Action: plate from grill_0 into plate_2
Observation: You plated all cooked ingredients from grill_0 into plate_2. plate_2: a plated dish with 1 serving of raw, chopped lettuce without any seasoning; 1 serving of grilled tortilla without any seasoning.

Action: wait
Observation: pan_0 finished cooking your one serving of pan-fried chicken, pan-fried shrimp.

Action: plate from pan_0 into plate_2
Observation: You plated all cooked ingredients from pan_0 into plate_2. plate_2: A successfully prepared serving of the requested **taco (Smoky Lime)**.

Action: serve plate_2
Observation: Successfully served plate_2. This is a successful serving of **taco (Smoky Lime)**, filled with chicken, lettuce, and shrimps.
"""