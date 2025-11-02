
# "New document" を含むウィンドウを探して送信
WINDOW_ID=$(xdotool search --name "Inkscape" getwindowname %@ | grep -n "New document" | cut -d: -f1)
ACTUAL_ID=$(xdotool search --name "Inkscape" | sed -n "${WINDOW_ID}p")

echo -n "日本語テキスト" | xclip -selection clipboard
xdotool windowactivate --sync "$ACTUAL_ID"
sleep 0.3
xdotool key ctrl+v
