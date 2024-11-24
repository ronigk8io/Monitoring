#!/bin/bash

result=$(timeout 5 google-chrome --headless --dump-dom 'https://celoscan.io/' --virtual-time-budget=10000 --timeout=10000 --run-all-compositor-stages-before-draw --disable-gpu --user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36" -o | grep -o "block/[0-9]*" | grep -o "[0-9]*"  | head -n 1)
echo "$result"
