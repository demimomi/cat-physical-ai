#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
export IGN_GAZEBO_RESOURCE_PATH="$PWD${IGN_GAZEBO_RESOURCE_PATH:+:$IGN_GAZEBO_RESOURCE_PATH}"

exec env -u WAYLAND_DISPLAY \
QT_QPA_PLATFORM=xcb \
QSG_RENDER_LOOP=basic \
LIBGL_ALWAYS_SOFTWARE=1 \
ign gazebo -v 3 world_cat.sdf --render-engine ogre2
