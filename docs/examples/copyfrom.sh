#!/bin/bash
# inkscape-get-text-simple.sh

echo "Inkscapeのテキストボックスをクリックしてください"
echo "3秒後に実行します..."
sleep 3

echo "ctrl + a"
xdotool key ctrl+a
sleep 0.3
echo "ctrl + c"
xdotool key ctrl+c
sleep 0.3

TEXT=$(xclip -selection clipboard -o)
echo "取得したテキスト:"
echo "$TEXT"
