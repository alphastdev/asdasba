import cv2
import numpy as np
import mss
import time
import pyautogui
import win32gui
import win32con
import win32api
import pydirectinput
import json

chsecimresim = cv2.imread('resimler/autologin/chsecimekrani.png', cv2.IMREAD_COLOR)
loginekranresim = cv2.imread('resimler/autologin/loginekran.png', cv2.IMREAD_COLOR)
baglantiekranresim = cv2.imread('resimler/autologin/baglantiekran.png', cv2.IMREAD_COLOR)
karakterekranresim = cv2.imread('resimler/autologin/karakterekran.png', cv2.IMREAD_COLOR)
karakterolusturresim = cv2.imread('resimler/autologin/karakterolustur.png', cv2.IMREAD_COLOR)

threshold = 0.8

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

def mouse_leftclick(hwnd, x, y):
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

def vpnresimsorgulama(resim):
    with mss.mss() as sct:
        monitor = {
            "top": 0,
            "left": 0,
            "width": 1920,
            "height": 1080
        }
        frame = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        result = cv2.matchTemplate(frame, resim, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)
        found = False
        if loc[0].size > 0:
            found = True
        return found

def chsec(wins):
    with open("chsecim.json", "r", encoding="utf-8") as f:
        jsonch = json.load(f)  # JSON dosyasındaki veriyi al
    charaligi = 17
    chsecim = jsonch
    chtikx = 520
    chtiky = ((chsecim * charaligi) + 146)
    pyautogui.moveTo(chtikx, chtiky)
    time.sleep(0.2)
    mouse_leftclick(wins[0], chtikx, chtiky)
    time.sleep(0.2)
    pyautogui.moveTo(520, 520)
    time.sleep(0.2)
    mouse_leftclick(wins[0], 520, 520)




# sorguornek = resimsorgulama(chsecimresim)
# if sorguornek:
#     print("bulundu")



def autologin(wins_param):
    global wins
    wins = wins_param

    while True:
        print("login başladı")

        chsecimsorgu = resimsorgulama(chsecimresim)
        loginsorgu = resimsorgulama(loginekranresim)
        karaktersorgu =  resimsorgulama(karakterekranresim)
        karakterolustursorgu = resimsorgulama(karakterolusturresim)
        if not chsecimsorgu and not loginsorgu and not karaktersorgu and not karakterolustursorgu:
            print("breakle")
            break

        if chsecimsorgu:
            print("chseç")
            chsec(wins)
            time.sleep(1)

        if loginsorgu:
            pyautogui.moveTo(350,400)
            time.sleep(0.1)
            mouse_leftclick(wins[0],350,400)
            time.sleep(0.2)
            pyautogui.moveTo(360,360)
            time.sleep(0.2)
            mouse_leftclick(wins[0], 360,360)
            time.sleep(7)
            baglantisorgu = resimsorgulama(baglantiekranresim)
            if baglantisorgu:
                while baglantisorgu:
                    for x in range(0, 11):  # 0'dan 100'e kadar
                        pydirectinput.keyDown("enter")
                        time.sleep(0.1)
                        pydirectinput.keyUp("enter")
                    time.sleep(7)
                    baglantisorgu = resimsorgulama(baglantiekranresim)

        if karaktersorgu:
            pydirectinput.keyDown("enter")
            time.sleep(0.1)
            pydirectinput.keyUp("enter")
            time.sleep(10)
            karaktersorgu = resimsorgulama(karakterekranresim)
            if karaktersorgu:
                while karaktersorgu:
                    pydirectinput.keyDown("right")
                    time.sleep(0.1)
                    pydirectinput.keyUp("right")
                    time.sleep(1)
                    pydirectinput.keyDown("enter")
                    time.sleep(0.1)
                    pydirectinput.keyUp("enter")
                    time.sleep(1)
                    pydirectinput.keyDown("esc")
                    time.sleep(0.1)
                    pydirectinput.keyUp("esc")
                    time.sleep(1)
                    pydirectinput.keyDown("enter")
                    time.sleep(0.1)
                    pydirectinput.keyUp("enter")
                    time.sleep(6)
                    karaktersorgu = resimsorgulama(karakterekranresim)

        if karakterolustursorgu:
            pydirectinput.keyDown("enter")
            time.sleep(0.1)
            pydirectinput.keyUp("enter")
            time.sleep(1)
            pydirectinput.keyDown("esc")
            time.sleep(0.1)
            pydirectinput.keyUp("esc")
            time.sleep(4)









        time.sleep(0.1)