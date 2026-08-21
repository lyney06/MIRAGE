#!/bin/bash

# Base directory
BASE_DIR="visualization"

# Folder structure
mkdir -p $BASE_DIR/{core,screens,entities,levels,ui,assets/{fonts,images/{characters,enemies,items,backgrounds,ui},sounds}}

# Python module files
touch $BASE_DIR/__init__.py
touch $BASE_DIR/core/__init__.py
touch $BASE_DIR/core/game_display.py
touch $BASE_DIR/core/assets_manager.py
touch $BASE_DIR/core/ui_manager.py
touch $BASE_DIR/core/input_handler.py

touch $BASE_DIR/screens/__init__.py
touch $BASE_DIR/screens/screen.py
touch $BASE_DIR/screens/main_menu.py
touch $BASE_DIR/screens/level_screen.py
touch $BASE_DIR/screens/game_over.py
touch $BASE_DIR/screens/victory_screen.py

touch $BASE_DIR/entities/__init__.py
touch $BASE_DIR/entities/entity_renderer.py
touch $BASE_DIR/entities/player_renderer.py
touch $BASE_DIR/entities/enemy_renderer.py

touch $BASE_DIR/levels/__init__.py
touch $BASE_DIR/levels/level_renderer.py
touch $BASE_DIR/levels/growth_renderer.py
touch $BASE_DIR/levels/combat_renderer.py
touch $BASE_DIR/levels/boss_renderer.py
touch $BASE_DIR/levels/shop_renderer.py
touch $BASE_DIR/levels/crafting_renderer.py

touch $BASE_DIR/ui/__init__.py
touch $BASE_DIR/ui/text_box.py
touch $BASE_DIR/ui/button.py
touch $BASE_DIR/ui/inventory_panel.py
touch $BASE_DIR/ui/status_panel.py
touch $BASE_DIR/ui/message_log.py
touch $BASE_DIR/ui/command_input.py

touch $BASE_DIR/assets/placeholder.py

echo "Project structure initialized in $BASE_DIR/"
