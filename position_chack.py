import pyautogui
import keyboard

while(True):
    print(f"現在の座標+{pyautogui.position()}")
    if keyboard.is_pressed('q'):
        print("end")
        break
