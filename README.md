# AutoHyakuretsu
An extensible python autoclicker with screen capture and pattern recognition
Still in development, but the basic functionality is there.
Done as a test to make something in python with AI assistance, and to automate some clicking.

## Usage

Create your macros following the examples, they will be loaded automatically.

In the macros script, use the following stuff:

### pattern search

The first argument is the name of the pattern, the second is the screenshot in opencv format.
Patterns are PNG files in the templates folder, and are loaded automatically.

basic pattern search, returns x and y on success
```python
m = self.search_template("vlc_running", screenshot_cv):
if(m):
    x = m[0]
    y = m[1]
    print("vlc icon found at x: " + str(x) + " y: " + str(y))
```

search and click, utility method which saves some instructions for common tasks
```python
m = self.search_and_click("search", screenshot_cv, x_offset=100, y_offset=10, nr_clicks=2):
if(m):
    x = m[0]
    y = m[1]
    print("Made a double click at x: " + str(x) + " y: " + str(y))
```

### mouse control
For mouse clicking, use the main app click method when convenient, or pyautogui directly:
```python
self.app.click(x, y, nr_clicks=1)
pyautogui.click(x, y)
```


### keyboard control

For normal text, use 
```python
self.write_text(text, interval=0.1, wait_ms=0)
```

For special keys, use pyautogui directly:
```python
# send CTRL + A to select all text
pyautogui.hotkey('ctrl', 'a')

# send DEL to delete all text
pyautogui.press('del')

# send ESC to close the search box
pyautogui.press('esc')

# send ENTER to confirm the search
pyautogui.press('enter')

# send TAB to move to the next field
pyautogui.press('tab')

# send SHIFT + TAB to move to the previous field
pyautogui.hotkey('shift', 'tab')

# send CTRL + C to copy the selected text
pyautogui.hotkey('ctrl', 'c')

# send CTRL + V to paste the copied text
pyautogui.hotkey('ctrl', 'v')

# windows button
pyautogui.press('win')
```    