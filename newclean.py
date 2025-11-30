import win32gui
import win32con
import win32api
import time
import captcharesolver
import cv2
import numpy as np
import mss
import pyautogui
import pydirectinput
from ultralytics import YOLO
import random
import torch
import autologin
pydirectinput.PAUSE = 0

wins = []

device = "cuda" if torch.cuda.is_available() else "cpu"
model = YOLO("best.pt").to(device)

threshold = 0.8

template = cv2.imread('template_bot_kontrol.png', cv2.IMREAD_COLOR)
onmetin = cv2.imread('metinbari.png', cv2.IMREAD_COLOR)
escscreen = cv2.imread('esc.png', cv2.IMREAD_COLOR)
canazalma = cv2.imread('canazalma.png',cv2.IMREAD_COLOR)
chsecimresim = cv2.imread('chsecimekrani.png', cv2.IMREAD_COLOR)
loginekranresim = cv2.imread('loginekran.png', cv2.IMREAD_COLOR)
karakterekranresim = cv2.imread('karakterekran.png', cv2.IMREAD_COLOR)
potsuzresim = cv2.imread('undead/potsuzresim.png')

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
        lparam = win32api.MAKELONG(x-8, y-29)
        win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
        time.sleep(0.02)
        win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, None, lparam)
        #print(f"Tıklama gönderildi -> {win32gui.GetWindowText(hwnd)} | x={x}, y={y}")
    except Exception as e:
        pass
        #print(f"Tıklama hatası: {e}")

def resimsorgulama(resim,frame):
    result = cv2.matchTemplate(frame, resim, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= threshold)
    found = False
    if loc[0].size > 0:
        found = True
    return found
def ekranss(x,y):
    with mss.mss() as sct:
        monitor = {"top": 0, "left": 0, "width": x, "height": y}
        frame = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    return frame


def metindetect(ekranboyutx,ekranboyuty):
    with mss.mss() as sct:
        monitor = {"top": 0, "left": 0, "width": ekranboyutx, "height": ekranboyuty}

        img = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        # küçültme boyutları
        new_w, new_h = int(ekranboyutx / 2), int(ekranboyuty / 2)
        scale_x = monitor["width"] / new_w
        scale_y = monitor["height"] / new_h

        # küçült
        small = cv2.resize(frame, (new_w, new_h))

        # YOLO tahmini
        results = model(small, imgsz=new_w, conf=0.5, max_det=1, device=device, verbose=False)

        boxes = results[0].boxes.xyxy
        if len(boxes) > 0:
            x1, y1, x2, y2 = boxes[0].tolist()

            # geri ölçeklendir (kritik kısım)
            x1 *= scale_x
            x2 *= scale_x
            y1 *= scale_y
            y2 *= scale_y

            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)

            return center_x, center_y

        return None, None


def esyatoplama():
    sequence = [
        ('w', 0.4),
        ('a', 0.4),
        ('s', 0.8),
        ('d', 0.7),
        ('w', 0.9)
    ]

    for key, hold in sequence:
        pydirectinput.keyDown("z")
        time.sleep(0.1)
        pydirectinput.keyUp("z")
        pydirectinput.keyDown(key)
        time.sleep(hold)
        pydirectinput.keyUp(key)
        pydirectinput.keyDown("z")
        time.sleep(0.1)
        pydirectinput.keyUp("z")
        # buraya minik bir bekleme koy, tamamen gecikmesiz olursa takılma olabilir
        time.sleep(0.05)  # 50 ms geçiş
def kameraduzeltme():
    pydirectinput.keyDown("f")
    time.sleep(1)
    pydirectinput.keyUp("f")
    time.sleep(0.1)
    pydirectinput.keyDown("g")
    time.sleep(1)
    pydirectinput.keyUp("g")
    time.sleep(0.1)
    pydirectinput.keyDown("t")
    time.sleep(0.7)
    pydirectinput.keyUp("t")
    time.sleep(0.1)
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
        if loc[0].size > 0:
            found = True
        if found:
            print("can azaldı")
            escekran = resimsorgulama(escscreen,800,600)
            if not escekran:
                pyautogui.moveTo(781, 615)
                time.sleep(0.1)
                mouse_leftclick(wins[0], 781, 615)
                escekran = resimsorgulama(escscreen,800,600)
            if escekran:
                pyautogui.moveTo(410,385)
                time.sleep(0.1)
                mouse_leftclick(wins[0],410,385)
                time.sleep(1.2)


ekrantoparlama()
searchleme = 0
counter = 0
kameracounter = 0
x = None
tiklandimi = None
kameraduzeltme()
metincanazaliyomu = None

while True:
    frame = ekranss(800,600)
    canarama()
    kameracounter = kameracounter + 1
    if kameracounter >= 50:
        pydirectinput.keyDown("1")
        time.sleep(0.1)
        pydirectinput.keyUp("1")
        time.sleep(0.1)

        pydirectinput.keyDown("2")
        time.sleep(0.1)
        pydirectinput.keyUp("2")

        time.sleep(0.1)
        kameraduzeltme()
        kameracounter = 0
        chsecimsorgu = resimsorgulama(chsecimresim,frame) #Burası değişecek
        loginsorgu = resimsorgulama(loginekranresim,frame) #Burası değişecek
        karaktersorgu = resimsorgulama(karakterekranresim,frame) #Burası değişecek

        if chsecimsorgu or loginsorgu or karaktersorgu: #Burası değişecek Oyun içinden bir ekran yoksa login deneyecek!
            autologin.autologin(wins)

    botkontrol = resimsorgulama(template,frame)
    if botkontrol: #eğer bot kontrol resmi varsa bot kontrol başlayacak.
        #print("Bot koruma tespit edildi! Modül Başlıyor.")
        captcharesolver.solve_captcha(wins)

    if x == None:
        x, y = metindetect(832,600)
        counter = counter + 1
        if counter >= 14:
            pydirectinput.keyDown("w")
    if not x == None:
        pydirectinput.keyUp("q")
        counter = 0
        pydirectinput.keyUp("w")
        if len(wins) == 0:
            break
        elif len(wins) == 1:
            target = wins[0]
        else:
            target = wins[0] if x < 960 else wins[1]

        pyautogui.moveTo(x, y + 5)
        time.sleep(0.05)
        mouse_leftclick(target, x, y + 5)
        pydirectinput.keyDown("q")  # bazen metine tıklayamıyor ve döngüde kalıyor
        time.sleep(0.05)
        pydirectinput.keyUp("q")
        time.sleep(0.5)
        frame = ekranss(565,110)
        tiklandimi = resimsorgulama(onmetin,frame)
        if not tiklandimi == False:  # metine tıklandı anlamına geliyor
            pyautogui.moveTo(70, 70)
            for i in range(600):  # 60 saniye döneceks
                canarama()
                frame = ekranss(800,600)
                botkontrol = resimsorgulama(template,frame)
                if botkontrol:  # eğer bot kontrol resmi varsa bot kontrol başlayacak.
                    # print("Bot koruma tespit edildi! Modül Başlıyor.")
                    captcharesolver.solve_captcha(wins)
                stuck = resimsorgulama(onmetin,frame)
                if i == 0:
                    i = 1
                    counter2 = 0
                if i % 50 == 0:
                    metinvarmi = resimsorgulama(onmetin,frame)
                    if metinvarmi:
                        metincanazaliyomu = resimsorgulama(canazalma,frame)
                        if not metincanazaliyomu:

                            counter2 = counter2 + 1

                            directions = ['w', 'a', 's', 'd']
                            random.shuffle(directions)  # yön sırasını karıştır

                            move_count = random.randint(2, 4)  # 2 ila 4 farklı yön seç
                            for move in directions[:move_count]:
                                hold_time = random.uniform(0.3, 1.0)  # her hareketin süresi farklı
                                pydirectinput.keyDown(move)
                                time.sleep(hold_time)
                                pydirectinput.keyUp(move)
                if metincanazaliyomu:
                    metinkeserkenaramayap = 1
                    if metinkeserkenaramayap == 1:
                        x, y = metindetect(832,256)
                        if x == None:
                            pydirectinput.keyDown("q")
                            time.sleep(0.7)
                            pydirectinput.keyUp("q")
                        if not x == None:
                            metinkeserkenaramayap = 0
                    if counter2 >= 4:
                        pydirectinput.keyDown("esc")
                        time.sleep(0.1)
                        pydirectinput.keyUp("esc")
                        time.sleep(0.5)
                        esckontrol = resimsorgulama(escscreen,frame)
                        if esckontrol:
                            pydirectinput.keyDown("esc")
                            time.sleep(0.1)
                            pydirectinput.keyUp("esc")
                            time.sleep(0.5)
                        counter2 = 0
                if stuck == False:
                    esyatoplama()
                    x = None
                    break
        if tiklandimi == False:
            time.sleep(1.5)
            pydirectinput.keyDown("s")  # bazen metine tıklayamıyor ve döngüde kalıyor
            time.sleep(0.1)
            pydirectinput.keyUp("s")
            time.sleep(1)
    x, y = metindetect(832,608)
    if x == None:
        pyautogui.moveTo(70, 70)
        pydirectinput.keyDown("q")
        # pydirectinput.press("q", presses=5)
        # print(f"{sayi} geldi → 'q' basıldı.")