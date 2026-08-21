# LLM-Agent with Imperfect Manuals

## Install
```bash
# Python 3.10+
conda create -n manuals python=3.10; conda activate manuals
pip install --upgrade pip
pip install -r requirements.txt
```

## Run experiments
Example run:
```bash
python main.py --agent_model $MODEL --env VillageNav-v0 --manual_type 1
```

# 🧾 Manual Types and Code Status

## 🗺️ Navigation Environments
### 🧭 Navigation Manual Modes

| ID | Manual Mode Name     | Description                                                                                     |
|----|----------------------|-------------------------------------------------------------------------------------------------|
| 0  | `action-only, # turns`        | Move forward and take the n-th possible turn     |
| 1  | `action-only, # tiles`        | Observation-agnostic: contains **only action sequences**, no reliance on environment feedback, move forward n tiles    |
| 2  | `observation-based`  | Decisions depend on what is visible (e.g., "walk until you see a house, then turn left")        |
| 3  | `wrong # turns`        | Includes intentional wrong directions or detours that can be recovered                          |
| 4  | `wrong # tiles`          | Steps contain reasonable omissions (e.g., missing one turn) but goal is still reachable         |
---

### ✅ Base Environments
| Env ID                           | Description                                                                                         | 
|----------------------------------|-----------------------------------------------------------------------------------------------------|
| `VillageNav-v0`     | Village map with basic to complex layouts, difficulty based on the initial goal distance                                              |

---

### 🧪 Variant Environments
| Env ID                                     | Description                                                                                         |
|--------------------------------------------|-----------------------------------------------------------------------------------------------------|
| `VillageNav-Seasonal-v0`       | Village with seasonal changes (summer vs winter)                                                    | 
| `UrbanNav-Construction-v0`     | Roads randomly blocked due to construction                                                          | 
| `VillageNav-Dynamic-v0`          | Dynamic environment with pedestrians, bystanders, and traffic lights    |   
| `VillageNav-Large-v0`          | version with customized size    |  

## 🍳 Cooking Environments

### 📚 Cooking Manual Modes
| Mode | Description                                                                                    |
|------|---------------------------------------------------------------------------------------------------|
| 0    | Detailed **recipe** only                                                                           | 
| 1    | A simplified yet accurate recipe **plus ingredient location information** (e.g., store, farm)      | 
| 2    | Detailed **recipe** (type=0) and ingredient location information                                   |
| 4    | A **slightly mismatched recipe** (same dish and flavor but with different ingredients – UPDATE: we may now include further hints, such as "chicken should be pan-fried," otherwise it's domain knowledge.) | 

---

### ✅ Base Environments

| Environment Name     | Description                                           |
|----------------------|------------------------------------------------------|
| `Cooking-easy-v0`    | Default version with 1 dish and 1 serving            | 

---

### 🧪 Variant Environments

| Proposed Env Name             | Description                                                                                  | 
|-------------------------------|----------------------------------------------------------------------------------------------|
| `Cooking-easy-crop-gone-v0`      | Small animals may **steal or damage crops** from the farm before harvesting – this does not work with `manual_type==1`; you must provide location information. | 
| `Cooking-easy-storage-loss-v0`    | Ingredients **stored at the restaurant** might go missing or become spoiled before use   | 
| `Cooking-easy-rookie-chef-v0`     | You're a **rookie chef** — seasoning may **go wrong**, requiring the dish to be redone   | 

## 🎮 Gaming Environments
### 💻 Gaming Manual Modes
| Mode | Description                                                                                       |    
|------|---------------------------------------------------------------------------------------------------|
| 0    | Very detailed — specifies which item to collect and drop at each level                            | 
| 1    | Boss element, selected weapon, weapon crafting recipe, and items to collect                        | 
| 2    | Only tells the agent which items to collect — does not reveal the full inventory state or any other contextual details        | 
| 3    | more comprehensive and low level instruction, even telling you where to find which item specifically | 
| 4    | 3, but only for partial levels |
| 5    | 3, but wrong recipe, however craft won't be successful and we can call recipes function to craft | 
---

### ✅ Base Environments
| Env ID                           | Description                                                                                         | 
|----------------------------------|-----------------------------------------------------------------------------------------------------|
| `Roguelike-easy-v0`              | growth → growth → combat → growth → shop → boss                                                     |
| `Roguelike-reversible-easy-v0`   | Allows agents to backtrack to previously visited levels, enabling recovery from suboptimal actions and supporting strategic replanning   | 
---

### 🧪 Variant Environments
| Env ID                                     | Description                                                                                         | 
|--------------------------------------------|-----------------------------------------------------------------------------------------------------|
| `Roguelike-shuffle-easy-v0`                | Shuffle item locations in the same level containers and shuffle enemy drops | 
| `Roguelike-rename-easy-v0`                 | Different names for the items, but we let NPCs give some hints accordingly.      |

## Add the new environment to envs
1. create `cuterpg.yaml` in `env_configs`
2. add the env files to `envs`
3. Modify `env/utils` correspondingly.

## Create an agent
1. Create the agent class in `llmagentbase/agent/cuterpg.py`
2. Write prompts (one-shot, or instruction) in `llmagentbase/prompts/cuterpg.py`
