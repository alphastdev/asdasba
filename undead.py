import pyautogui
import win32gui
import win32con
import win32api
import time
import mss
import cv2
import numpy as np
import pydirectinput
pydirectinput.PAUSE = 0
pyautogui.PAUSE = 0

threshold = 0.8

wins = []

potluresim = cv2.imread('undead/potluresim.png')
potsuzresim = cv2.imread('undead/potsuzresim.png')

escscreen = cv2.imread('esc.png', cv2.IMREAD_COLOR)

def resimsorgulama(resim):
    with mss.mss() as sct:
        monitor = {
            "top": 0,
            "left": 0,
            "width": 800,
            "height": 600
        }
        frame = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        result = cv2.matchTemplate(frame, resim, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)
        found = False
        if loc[0].size > 0:
            found = True
        return found

def canarama():
    with mss.mss() as sct:
        monitor = {
            "top": 595,
            "left": 63,
            "width": 60,
            "height": 17
        }
        frame = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        result = cv2.matchTemplate(frame, potsuzresim, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)
        found = False
        print(found)
        if loc[0].size > 0:
            found = True
        if found:
            escekran = resimsorgulama(escscreen)
            if not escekran:
                pyautogui.moveTo(781, 615)
                time.sleep(0.1)
                mouse_leftclick(wins[0], 781, 615)
            if escekran:
                print("esc açık karakter at")
                pyautogui.moveTo(410,385)
                time.sleep(0.1)
                mouse_leftclick(wins[0],410,385)
                time.sleep(1.2)
        cv2.imshow("Ekran", frame)
        cv2.waitKey(1)

def ekrantoparlama():
    TARGET = "Misali2 (Ebedi)"
    global wins

    # Tüm pencereleri tara ve Misali2 içerenleri listele
    def enum_handler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if TARGET.lower() in title.lower():
                wins.append(hwnd)

    win32gui.EnumWindows(enum_handler, None)

    if not wins:
        print("Hiç 'Misali2' penceresi FGamadı.")
        return

    # İlk iki pencereyi konumlandır (dilersen 2 yerine len(wins) yazabilirsin)
    for i, h in enumerate(wins[:2]):
        x = 0 if i == 0 else 960  # 1. pencere sol, 2. pencere sağ
        r = win32gui.GetWindowRect(h)
        width = r[2] - r[0]
        height = r[3] - r[1]
        win32gui.MoveWindow(h, x, 0, width, height, True)
        print(f"Pencere taşındı: {win32gui.GetWindowText(h)} -> X={x}, Y=0")

    bring_to_front(wins[0])

def bring_to_front(hwnd):
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.05)
        win32gui.SetForegroundWindow(hwnd)
        win32gui.BringWindowToTop(hwnd)
        win32gui.SetActiveWindow(hwnd)
    except Exception as e:
        print(f"Öne getirme hatası: {e}")

def mouse_leftclick(hwnd, x, y):
    try:
        bring_to_front(hwnd)
        time.sleep(0.05)
        lparam = win32api.MAKELONG(x, y-29)
        win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
        time.sleep(0.02)
        win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, None, lparam)
    except Exception as e:
        pass

ekrantoparlama()


while True:
    canarama()

    time.sleep(0.2)
