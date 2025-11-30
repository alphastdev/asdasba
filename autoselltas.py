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

def resimsorgulamaxy(resim):
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
        if loc[0].size > 0:
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            x, y = max_loc
            return (x, y)
        else:
            return None

def ekrantoparlama():
    TARGET = "Misali2 (E"
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

def mouse_leftclickdown(hwnd, x, y):
    try:
        bring_to_front(hwnd)
        time.sleep(0.1)
        lparam = win32api.MAKELONG(x, y-29)
        win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
        #print(f"Tıklama gönderildi -> {win32gui.GetWindowText(hwnd)} | x={x}, y={y}")
    except Exception as e:
        #print(f"Tıklama hatası: {e}")
        pass

def mouse_leftclickup(hwnd, x, y):
    try:
        bring_to_front(hwnd)
        time.sleep(0.1)
        lparam = win32api.MAKELONG(x, y-29)
        win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, None, lparam)

    except Exception as e:
        pass

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

kekranresim = cv2.imread('autosell/kekrani.png', cv2.IMREAD_COLOR)
tasekranresim = cv2.imread('autosell/tasekrani.png', cv2.IMREAD_COLOR)
tasbutonresim = cv2.imread('autosell/tasbuton.png', cv2.IMREAD_COLOR)

ilksatilacakyerxy = (11,42)
satilacakslotaraligi = 32
envantergenisligix = 5
envantergenisligiy = 9

ksorgu = resimsorgulama(kekranresim)
while not ksorgu:
    print("k kapalı")
    pydirectinput.keyDown("k")  # bazen metine tıklayamıyor ve döngüde kalıyor
    time.sleep(0.05)
    pydirectinput.keyUp("k")
    ksorgu = resimsorgulama(kekranresim)

while ksorgu:
    kekransorguxy = resimsorgulamaxy(kekranresim)
    pyautogui.moveTo(kekransorguxy[0]-10,kekransorguxy[1])
    time.sleep(0.1)
    mouse_leftclick(wins[0],kekransorguxy[0],kekransorguxy[1])

    time.sleep(3)
    tasekransorgu = resimsorgulama(tasekranresim)


    if not tasekransorgu:
        tasbutonsorguxy = resimsorgulamaxy(tasbutonresim)
        pyautogui.moveTo(tasbutonsorguxy)
        time.sleep(0.1)
        mouse_leftclick(wins[0],tasbutonsorguxy[0],tasbutonsorguxy[1])
    if tasekransorgu:
        for satir in range(envantergenisligiy):  # 9 satır
            for sutun in range(envantergenisligix):  # 5 sütun
                x = kekransorguxy[0]+11 + sutun * satilacakslotaraligi
                y = kekransorguxy[1]+42 + satir * satilacakslotaraligi

                # Mouse'u slotun üzerine götür
                pyautogui.moveTo(x, y)
                mouse_leftclickdown(wins[0], x, y)
                pyautogui.moveTo(19, 135)
                mouse_leftclickup(wins[0], 19, 135)
                pyautogui.moveTo(408, 308)
                mouse_leftclick(wins[0],408,308)
                #pyautogui.click()  # tıklamak istiyorsan
                print(f"Tıklandı: ({x}, {y})")
        break





# pyautogui.moveTo(475,220)
#
# mouse_leftclickdown(wins[0],475,191)
#
# pyautogui.moveTo(19,135)
#
# mouse_leftclickup(wins[0],19,135)
