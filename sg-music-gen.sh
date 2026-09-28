#!/bin/sh

# sg-music-gen - An acestep.cpp-based command-line music generator for *nix.
# Copyright (C) 2026 Soumendra Ganguly

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

REAL=$(realpath "$0")
DIR=$(dirname "$REAL")
NAME=$(basename "$REAL" .sh)
SCRIPT=$(printf '%s' "$NAME" | tr - _).py

command -v nvidia-smi >/dev/null && command -v nvidia-container-cli >/dev/null && GPU=all

exec docker run --rm -i --user "$(id -u):$(id -g)" ${GPU:+--gpus "$GPU"} --network none \
    -e GGML_BACKEND -v "$DIR":/app:ro -v "$DIR/models":/models:ro -v "$PWD":/work -w /work \
    "$NAME" python3 "/app/$SCRIPT" --models /models "$@"
