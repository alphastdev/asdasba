import cv2
import numpy as np
import mss
import time
import pyautogui
import win32gui
import win32con
import win32api
import pydirectinput

template = cv2.imread('template_bot_kontrol.png', cv2.IMREAD_COLOR)
t_height, t_width = template.shape[:2]
threshold = 0.8
same_dirs = [f"output/same{i}" for i in range(1, 29)]

wins = []  # main.py'den gelecek

def bring_to_front(hwnd):
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.05)
        win32gui.SetForegroundWindow(hwnd)
        win32gui.BringWindowToTop(hwnd)
        win32gui.SetActiveWindow(hwnd)
    except Exception as e:
        print(f"Öne getirme hatası: {e}")

def mouse_click(hwnd, x, y):
    try:
        bring_to_front(hwnd)
        time.sleep(0.05)
        lparam = win32api.MAKELONG(x, y)
        win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
        time.sleep(0.02)
        win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, None, lparam)
        print(f"Tıklama gönderildi -> {win32gui.GetWindowText(hwnd)} | x={x}, y={y}")
    except Exception as e:
        print(f"Tıklama hatası: {e}")

def solve_captcha(wins_param):
    global wins
    wins = wins_param

    with mss.mss() as sct:
        monitor = sct.monitors[1]

        while True:
            frame = np.array(sct.grab(monitor))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(result >= threshold)

            found = False
            for pt in zip(*loc[::-1]):
                sol_alt_x = pt[0]
                sol_alt_y = pt[1] + t_height
                found = True
                break

            if not found:
                print("Ekranda bulunamadı.")

            if found:
                print(f"Bulundu! Sol alt köşe: ({sol_alt_x}, {sol_alt_y})")
                scan_area = {
                    "left": sol_alt_x,
                    "top": sol_alt_y,
                    "width": 300,
                    "height": 300
                }
                frame = np.array(sct.grab(scan_area))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                h, w = frame.shape[:2]
                h_step = h // 3
                w_step = w // 3

                parts = []
                centers = []
                for i in range(3):
                    for j in range(3):
                        y1, y2 = i * h_step, (i + 1) * h_step
                        x1, x2 = j * w_step, (j + 1) * w_step
                        sub = frame[y1:y2, x1:x2]
                        parts.append(sub)
                        centers.append((scan_area["left"] + x1 + w_step // 2,
                                        scan_area["top"] + y1 + h_step // 2))

                best_match = None
                for folder in same_dirs:
                    match_count = 0
                    unmatched_index = None

                    for idx, part in enumerate(parts):
                        img_path = f"{folder}/part{idx + 1}.png"
                        candidate = cv2.imread(img_path, cv2.IMREAD_COLOR)
                        if candidate is None:
                            continue

                        res = cv2.matchTemplate(part, candidate, cv2.TM_CCOEFF_NORMED)
                        max_val = cv2.minMaxLoc(res)[1]

                        if max_val >= 0.8:
                            match_count += 1
                        else:
                            unmatched_index = idx

                    if match_count == 8:
                        best_match = (folder, unmatched_index)
                        break

                if best_match:
                    folder, idx = best_match
                    cx, cy = centers[idx]
                    print(f"{folder} klasörü 8 eşleşme içeriyor. "
                          f"Eşleşmeyen parça {idx + 1}, merkez koordinat: ({cx}, {cy})")

                    # 🔒 güvenli kontrol
                    if len(wins) == 0:
                        print("wins listesi boş, captcha çözülemedi.")
                        break
                    elif len(wins) == 1:
                        target = wins[0]
                    else:
                        target = wins[0] if cx < 960 else wins[1]

                    pyautogui.moveTo(cx, cy)
                    time.sleep(0.1)
                    mouse_click(target, cx, cy)
                    time.sleep(2)
                    pyautogui.moveTo(sol_alt_x + 148, sol_alt_y + 346)
                    time.sleep(0.1)
                    mouse_click(target, sol_alt_x + 148, sol_alt_y + 346)
                    break

                if not best_match:
                    if len(wins) == 0:
                        print("wins listesi boş, captcha çözülemedi.")
                        break
                    elif len(wins) == 1:
                        target = wins[0]
                    else:
                        target = wins[0] if sol_alt_x < 960 else wins[1]
                    pyautogui.moveTo(406, 424) #screen baz alınarak yapılacak 2. ekranı eklediğimzde
                    time.sleep(0.1)
                    mouse_click(target, 406, 424) #screen baz alınarak yapılacak 2. ekranı eklediğimzde
                    time.sleep(0.1)
                    pyautogui.moveTo(401, 518) #screen baz alınarak yapılacak 2. ekranı eklediğimzde
                    time.sleep(0.1)
                    mouse_click(target, 401, 518) #screen baz alınarak yapılacak 2. ekranı eklediğimzde
                    time.sleep(1)
                    break

            cv2.imshow("Taranan Alan", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

            time.sleep(0.2)

    cv2.destroyAllWindows()
