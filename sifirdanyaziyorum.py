import cv2
import pydirectinput
import numpy as np
import mss
import torch
from ultralytics import YOLO
import time
import pyautogui
import ctypes
import win32gui
import win32con
import win32api
import random

import autologin
import captcharesolver
import autoselltas

import traceback



# Windows API fonksiyonu
GetAsyncKeyState = ctypes.windll.user32.GetAsyncKeyState

VK_F1 = 0x70  # F1 tuşu
VK_F2 = 0x71  # F2 tuşu


pydirectinput.PAUSE = 0

wins = []

threshold = 0.8



device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[YOLO] Model yükleniyor... ({device})")
model = YOLO("kendiyapim1ve2.pt").to(device)
print(f"[YOLO] Model başarıyla yüklendi → {device}")

BOT_CONTROL = "bot_control"
LOOKING = "looking"
TARGET_FOUND = "target_found"
METINATTACKING = "metinkesiliyor"
STUCK = "stuck"
NOTATTACKING = "notattacking"
COLLECT = "collect"
LOGIN = "login"
DEAD = "dead"
HPLOST = "hplost"

STUCK_LIMIT = 15  # saniye
stuck_start_time = None
metin_start_time = None

x = None


template = cv2.imread('resimler/genel/template_bot_kontrol.png', cv2.IMREAD_COLOR)
onmetin = cv2.imread('resimler/genel/metinbari.png', cv2.IMREAD_COLOR)
escscreen = cv2.imread('resimler/genel/esc.png', cv2.IMREAD_COLOR)
canazalma = cv2.imread('resimler/genel/canazalma.png', cv2.IMREAD_COLOR)
potsuzresim = cv2.imread('resimler/undead/potsuzresim.png')
oyuniciresim = cv2.imread('resimler/genel/oyunicindemi.png')
olumekranresim = cv2.imread('resimler/genel/olumekrani.png')


def resimsorgulama(resim, frame):
    result = cv2.matchTemplate(frame, resim, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= threshold)
    return loc[0].size > 0

def ekranss(x1, y1, x2, y2):
    with mss.mss() as sct:
        monitor = {"top": x1, "left": y1, "width": x2, "height": y2}
        frame = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    return frame

def metindetect(ekranboyutx, ekranboyuty, imgsize):
    with mss.mss() as sct:
        monitor = {"top": 0, "left": 0, "width": ekranboyutx, "height": ekranboyuty}

        # --- EN HIZLI ekran yakalama ---
        raw = sct.grab(monitor)
        frame = np.frombuffer(raw.rgb, dtype=np.uint8).reshape(raw.height, raw.width, 3)

        # --- YOLO INFERENCE (direct input, zero scaling) ---
        results = model.predict(
            frame,
            imgsz=imgsize,        # YOLO kendi letterbox yapar
            conf=0.5,
            max_det=1,
            device=device
        )

        boxes = results[0].boxes.xyxy

        # Box yoksa direkt None dön
        if len(boxes) == 0:
            return None, None

        x1, y1, x2, y2 = boxes[0].tolist()

        # Hepsi doluysa merkez hesapla
        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)

        return center_x, center_y


def kameraduzeltme():
    pydirectinput.keyDown("f"); time.sleep(1); pydirectinput.keyUp("f"); time.sleep(0.1)
    pydirectinput.keyDown("g"); time.sleep(1); pydirectinput.keyUp("g"); time.sleep(0.1)
    pydirectinput.keyDown("t"); time.sleep(0.7); pydirectinput.keyUp("t"); time.sleep(0.1)


def esyatoplama():
    sequence = [('w', 0.4), ('a', 0.4), ('s', 0.8), ('d', 0.7), ('w', 0.9)]
    for key, hold in sequence:
        press_key("z",0.1,0.1)
        pydirectinput.keyDown("z")
        time.sleep(0.1)
        pydirectinput.keyUp("z")
        pydirectinput.keyDown(key)
        time.sleep(hold)
        pydirectinput.keyUp(key)
        press_key("z", 0.1, 0.1)
        pydirectinput.keyDown("z")
        time.sleep(0.1)
        pydirectinput.keyUp("z")
        time.sleep(0.05)
        press_key("z", 0.1, 0.1)

def karakterat():
    pyautogui.moveTo(785, 615)
    time.sleep(0.1)
    mouse_leftclick(wins[0], 785, 615)
    time.sleep(0.1)
    pyautogui.moveTo(403, 384)
    time.sleep(0.1)
    mouse_leftclick(wins[0], 403, 384)
    time.sleep(5)

active_key = None
key_stage = 0
key_next_time = 0

def press_key(key, down_time=0.05, up_time=0.05):
    global active_key, key_stage, key_next_time

    now = time.time()

    # Henüz bir işlem yok → yeni tuş basma başlat
    if active_key is None:
        active_key = key
        key_stage = 0
        key_next_time = now
        return False  # işlem devam ediyor

    # İşlem devam ederken zaman gelmemiş → hiçbir şey yapma
    if now < key_next_time:
        return False

    # Stage 0 → bas
    if key_stage == 0:
        pydirectinput.keyDown(active_key)
        key_stage = 1
        key_next_time = now + down_time
        return False

    # Stage 1 → bırak
    elif key_stage == 1:
        pydirectinput.keyUp(active_key)
        key_stage = 2
        key_next_time = now + up_time
        return False

    # Stage 2 → işlem bitti
    else:
        active_key = None
        key_stage = 0
        return True  # işlem tamamlandı

def mouse_leftclick(hwnd, x, y):
    try:
        bring_to_front(hwnd)
        time.sleep(0.05)
        lparam = win32api.MAKELONG(x-8, y-29)
        win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
        time.sleep(0.02)
        win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, None, lparam)
    except:
        pass

def ekrantoparlama():
    TARGET = "Misali2 (E"
    global wins

    def enum_handler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if TARGET.lower() in title.lower():
                wins.append(hwnd)

    win32gui.EnumWindows(enum_handler, None)

    if not wins:
        print("Hiç 'Misali2' penceresi bulunamadı.")
        return

    for i, h in enumerate(wins[:2]):
        x = 0 if i == 0 else 960
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

ekrantoparlama()

kesilenmetin = 0
counterstuck = 0
aramayap = False
lookingcounter = None

kameraduzeltme()

STATE = "fck"

LAST_STATE = None

while True:
    try:
        time.sleep(0.1)

        if GetAsyncKeyState(VK_F1) & 0x8000:
            print("F1 basıldı, çıkıyorum...")
            break

        if GetAsyncKeyState(VK_F2) & 0x8000:
            print("F2 basıldı, satış başladı...")
            autoselltas.autosell(wins)
        frame = ekranss(0,0,800,600)

        metintiklandimi = resimsorgulama(onmetin,frame)

        if not metintiklandimi and not LAST_STATE == "metinkesiliyor":
            STATE = "looking"
            stuck_start_time = None

        if metintiklandimi:
            STATE = "target_found"
            metinevuruyormu = resimsorgulama(canazalma, frame)
            if metinevuruyormu: # counter eklenecek ve 60 saniyeden fazla kesiliyorda kalırsa esc basacak.
                stuck_start_time = None
                STATE = "metinkesiliyor"
                LAST_STATE = "metinkesiliyor"
                if metin_start_time is None:
                    metin_start_time = time.time()
                frame = ekranss(595, 63, 60, 17)
                canazaldimi = resimsorgulama(potsuzresim, frame)
                if canazaldimi:
                    STATE = "hplost"
            else:
                # iki frame al, fark kontrolü
                frame1 = ekranss(93, 735, 12, 12)
                time.sleep(0.1)
                frame2 = ekranss(93, 735, 12, 12)
                diff = cv2.absdiff(frame1, frame2)
                non_zero_count = np.count_nonzero(diff)

                if non_zero_count < 10:
                    if stuck_start_time is None:
                        stuck_start_time = time.time()  # stuck başladı
                    STATE = "stuck"

                    # süresi dolmuş mu kontrol et
                    if time.time() - stuck_start_time >= STUCK_LIMIT:
                        STATE = "notattacking"
                else:
                    STATE = "target_found"

        frame = ekranss(595, 63, 60, 17)
        canazaldimi = resimsorgulama(potsuzresim, frame)
        if canazaldimi:
            STATE = "hplost"

        frame = ekranss(18, 750, 75, 75)
        oyundami = resimsorgulama(oyuniciresim, frame)
        if not oyundami:
            STATE = "login"

        frame = ekranss(0, 0, 800, 600)

        botgeldimi = resimsorgulama(template,frame)
        if botgeldimi:
            STATE = "bot_control"

        if STATE == "looking":
            if lookingcounter is None:
                lookingcounter = time.time()
            if lookingcounter is not None:
                lookingcounterkalansure = time.time() - lookingcounter
                if lookingcounterkalansure >= 15:
                    lookingcounter = None
                    kameraduzeltme()
            x, y = metindetect(800,600,640)
            if x == None:
                pyautogui.moveTo(70, 70)
                press_key("q",0.2,0.1)
                press_key("q", 0.2, 0.1)
            if not x == None:
                pydirectinput.keyDown("s")
                time.sleep(0.1)
                pydirectinput.keyUp("s")
                time.sleep(0.1)
                pydirectinput.keyUp("q")
                time.sleep(0.5)
                x, y = metindetect(800, 600,640) # tekrar none geliyor bazen
                if not x == None:
                    pyautogui.moveTo(x, y + 5)
                    time.sleep(0.1)
                    mouse_leftclick(wins[0], x, y + 5)
                x, y = None, None
                aramayap = True
                time.sleep(1)

        if STATE == "metinkesiliyor":
            if metin_start_time is not None:
                elapsed = time.time() - metin_start_time
                if elapsed >= 30:
                    metin_start_time = None
                    STATE = "notattacking"
            if aramayap == True:
                x, y = metindetect(800,600,320)
                if x == None:
                    pyautogui.moveTo(70, 70)
                    pydirectinput.keyDown("q")
                    time.sleep(0.5)
                    pydirectinput.keyUp("q")
                    time.sleep(0.15)
                if not x == None:
                    aramayap = False
                    x, y = None, None

        if LAST_STATE == "metinkesiliyor":
            frame = ekranss(0, 0, 800, 600)
            metintiklandimi = resimsorgulama(onmetin, frame)
            if metintiklandimi == False:
                kesilenmetin = kesilenmetin + 1
                metin_start_time = None
                print("kesilenmetin:")
                print(kesilenmetin)
                STATE = "collect"

        if STATE == "notattacking":
            pydirectinput.keyDown("esc")
            time.sleep(0.1)
            pydirectinput.keyUp("esc")
            time.sleep(0.1)
            pydirectinput.keyDown("e")
            time.sleep(1)
            pydirectinput.keyUp("e")
            LAST_STATE = None
            kameraduzeltme()

        if STATE == "stuck":
            counterstuck = counterstuck + 1
            if counterstuck >= 3:

                directions = ['w', 'a', 's', 'd']
                random.shuffle(directions)  # yön sırasını karıştır

                move_count = random.randint(2, 4)  # 2 ila 4 farklı yön seç
                for move in directions[:move_count]:
                    hold_time = random.uniform(0.3, 1.0)  # her hareketin süresi farklı
                    pydirectinput.keyDown(move)
                    time.sleep(hold_time)
                    pydirectinput.keyUp(move)

                counterstuck = 0

        if STATE == "collect":
            esyatoplama()
            LAST_STATE = None

        if STATE == "bot_control":
            captcharesolver.solve_captcha(wins)

        if STATE == "login":
            autologin.autologin(wins)

        if STATE == "hplost":
            karakterat()










    except Exception as e:

        print("[HATA]", e)

        traceback.print_exc()  # tam trace burada yazacak

        time.sleep(0.2)



