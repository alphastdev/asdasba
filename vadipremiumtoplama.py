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

ch0x,ch0y = 500,153
charaligi = 17
chsecim = 7 # guida chsi yazıldığında seçimi yapılacak keenks

ekran1xy = 0,0
ekran2xy = 960,0

ebedisunucuxy = 306,535

sunucuchonayxy = 530,522

otohesapxy = 354,403 # +20

wins = []

sayi = 1
torch.load("best.pt", weights_only=False)
model = YOLO("best.pt")


def esyatoplama():
    sequence = [
        ('w', 0.4),
        ('a', 0.4),
        ('s', 0.8),
        ('d', 0.7),
        ('w', 0.9)
    ]

    for key, hold in sequence:
        pydirectinput.keyDown(key)
        time.sleep(hold)
        pydirectinput.keyUp(key)
        pydirectinput.keyDown("z")
        time.sleep(0.1)
        pydirectinput.keyUp("z")
        # buraya minik bir bekleme koy, tamamen gecikmesiz olursa takılma olabilir
        time.sleep(0.05)  # 50 ms geçiş

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

template = cv2.imread('template_bot_kontrol.png', cv2.IMREAD_COLOR)
t_height, t_width = template.shape[:2]
threshold = 0.8

onmetin = cv2.imread('metinbari.png', cv2.IMREAD_COLOR)
t_height, t_width = template.shape[:2]

escscreen = cv2.imread('esc.png', cv2.IMREAD_COLOR)

canazalma = cv2.imread('canazalma.png',cv2.IMREAD_COLOR)

chsecimresim = cv2.imread('chsecimekrani.png', cv2.IMREAD_COLOR)
loginekranresim = cv2.imread('loginekran.png', cv2.IMREAD_COLOR)
karakterekranresim = cv2.imread('karakterekran.png', cv2.IMREAD_COLOR)

potsuzresim = cv2.imread('undead/potsuzresim.png')

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

def botkontrolsekme():
    with mss.mss() as sct:
        monitor = {
            "top": 0,
            "left": 0,
            "width": 800,
            "height": 600
        }
        frame = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)
        found = False
        if loc[0].size > 0:
            found = True
        # if not found:
        #     print("Bot Koruma Kontrol Edildi ve Bot Koruma Yoktur.")
        if found:
            #print("Bot koruma tespit edildi! Modül Başlıyor.")
            captcharesolver.solve_captcha(wins)
        return found

def esckontrol():
    with mss.mss() as sct:
        monitor = {
            "top": 0,
            "left": 0,
            "width": 800,
            "height": 600
        }
        frame = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        result = cv2.matchTemplate(frame, escscreen, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)
        found = False
        if loc[0].size > 0:
            found = True
        # if not found:
        #     print("Bot Koruma Kontrol Edildi ve Bot Koruma Yoktur.")
        if found:
            #print("Bot koruma tespit edildi! Modül Başlıyor.")
            pydirectinput.keyDown("esc")
            time.sleep(0.1)
            pydirectinput.keyUp("esc")
            time.sleep(0.5)

def metindetect():
    with mss.mss() as sct:
        monitor = {
            "top": 0,
            "left": 0,
            "width": 800,
            "height": 600
        }
        sct_img = sct.grab(monitor)
        frame = np.array(sct_img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        results = model.predict(source=frame)

        boxes = results[0].boxes.xyxy  # x1, y1, x2, y2 formatında
        if len(boxes) > 0:
            x1, y1, x2, y2 = boxes[0].tolist()
            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)
            return center_x, center_y
        return None, None

def metindetectwhilekill():
    with mss.mss() as sct:
        monitor = {
            "top": 0,
            "left": 0,
            "width": 800,
            "height": 260
        }
        sct_img = sct.grab(monitor)
        frame = np.array(sct_img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        results = model.predict(source=frame)

        boxes = results[0].boxes.xyxy  # x1, y1, x2, y2 formatında
        if len(boxes) > 0:
            x1, y1, x2, y2 = boxes[0].tolist()
            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)
            return center_x, center_y
        return None, None

def metinchoose():
    with mss.mss() as sct:
        monitor = {
            "top": 0,
            "left": 0,
            "width": 565,
            "height": 110
        }
        frame = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        result = cv2.matchTemplate(frame, onmetin, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)
        found = False
        if loc[0].size > 0:
            found = True
        # if not found:
        #     #print("Metine tıklanmadı")
        # if found:
        #     #print("Metine Tıklandı")
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
        if loc[0].size > 0:
            found = True
        if found:
            print("can azaldı")
            escekran = resimsorgulama(escscreen)
            if not escekran:
                pyautogui.moveTo(781, 615)
                time.sleep(0.1)
                mouse_leftclick(wins[0], 781, 615)
                escekran = resimsorgulama(escscreen)
            if escekran:
                pyautogui.moveTo(410,385)
                time.sleep(0.1)
                mouse_leftclick(wins[0],410,385)
                time.sleep(1.2)

def metincan():
    with mss.mss() as sct:
        monitor = {
            "top": 0,
            "left": 0,
            "width": 800,
            "height": 600
        }
        frame = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        result = cv2.matchTemplate(frame, canazalma, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)
        found = False
        if loc[0].size > 0:
            found = True
        # if not found:
        #     print("Bot Koruma Kontrol Edildi ve Bot Koruma Yoktur.")
        if found:
            pass
        return found

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

def chsec(whichscreen):
    chtikx = whichscreen[0] + ch0x
    chtiky = ((chsecim * charaligi) + ch0y)
    print("ch seçimi yapılıyor tıklanacak yer=")
    print(chtikx)
    print(chtiky)
def sunucusec(whichscreen):
    sunucusecimtikx = whichscreen[0] + ebedisunucuxy[0]
    sunucusecimtiky = ebedisunucuxy[1]
    print("sunucu seçimi yapılıyor")
    print(sunucusecimtikx)
    print(sunucusecimtiky)
def sunucuchonay(whichscreen):
    sunucuonaytikx = whichscreen[0] + sunucuchonayxy[0]
    sunucuonaytiky = sunucuchonayxy[1]
    print("sunucu ch onayı yapıldı")
    print(sunucuonaytikx)
    print(sunucuonaytiky)
def hesapsecimi(whichscreen):
    print (whichscreen[0])
    hesapsecimtikx = whichscreen[0] + otohesapxy[0]
    hesapsecimtiky = otohesapxy[1]
    if whichscreen[0] < 100:
        print("1. ekranda 1. hesaba giriş yapılıyor")
    else:
        hesapsecimtiky = hesapsecimtiky + 20
        print("2. ekranda 2. hesaba giriş yapılıyor")
    print(hesapsecimtikx)
    print(hesapsecimtiky)

    # buraya pyautogui click event
    time.sleep(0.5)
    #press('enter') enter eventi

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

def mouse_rightclick(hwnd, x, y):
    try:
        bring_to_front(hwnd)
        time.sleep(0.5)
        lparam = win32api.MAKELONG(x, y)
        win32gui.SendMessage(hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, lparam)
        time.sleep(0.1)
        win32gui.SendMessage(hwnd, win32con.WM_RBUTTONUP, None, lparam)
        print(f"Tıklama gönderildi -> {win32gui.GetWindowText(hwnd)} | x={x}, y={y}")
    except Exception as e:
        print(f"Tıklama hatası: {e}")



ekrantoparlama()
#botkontrolsekme()
searchleme = 0
counter = 0
kameracounter = 0
x = None
tiklandimi = None
kameraduzeltme()
metincanazaliyomu = None
while True:
    canarama()
    kameracounter = kameracounter + 1
    if kameracounter >= 20:
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
        chsecimsorgu = resimsorgulama(chsecimresim)
        loginsorgu = resimsorgulama(loginekranresim)
        karaktersorgu = resimsorgulama(karakterekranresim)

        if chsecimsorgu or loginsorgu or karaktersorgu:
            autologin.autologin(wins)

    botkontrolsekme()
    if x == None:
        x, y = metindetect()
        counter = counter + 1
        if counter >= 14:
            pydirectinput.keyDown("w")
    if not x == None:
        counter = 0
        pydirectinput.keyUp("w")
        if len(wins) == 0:
            break
        elif len(wins) == 1:
            target = wins[0]
        else:
            target = wins[0] if x < 960 else wins[1]

        pyautogui.moveTo(x,y+5)
        time.sleep(0.05)
        mouse_leftclick(target, x, y+5)
        pydirectinput.keyDown("q") # bazen metine tıklayamıyor ve döngüde kalıyor
        time.sleep(0.05)
        pydirectinput.keyUp("q")
        time.sleep(0.5)
        tiklandimi = metinchoose()
        if not tiklandimi == False: # metine tıklandı anlamına geliyor
            pyautogui.moveTo(70, 70)
            for i in range(60): # 60 saniye dönecek
                canarama()
                botkontrolsekme()
                stuck = metinchoose()
                if i == 0:
                    i = 1
                    counter2 = 0
                if i % 5 == 0:
                    metinvarmi = metinchoose()
                    if metinvarmi:
                        metincanazaliyomu = metincan()
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
                        x, y = metindetectwhilekill()
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
                        esckontrol()
                        counter2 = 0

                if stuck == False:
                    #esyatoplama()
                    x = None
                    break
                time.sleep(1)
        if tiklandimi == False:
            time.sleep(1.5)
            pydirectinput.keyDown("s")  # bazen metine tıklayamıyor ve döngüde kalıyor
            time.sleep(0.1)
            pydirectinput.keyUp("s")
            time.sleep(1)
    x, y = metindetect()
    if x == None:
        pyautogui.moveTo(70,70)
        pydirectinput.keyDown("q")
        time.sleep(0.2)
        pydirectinput.keyUp("q")
        time.sleep(0.2)
        pydirectinput.keyDown("q")
        time.sleep(0.2)
        pydirectinput.keyUp("q")
        time.sleep(0.2)
        pydirectinput.keyDown("q")
        time.sleep(0.2)
        pydirectinput.keyUp("q")
        time.sleep(0.2)
        #pydirectinput.press("q", presses=5)
        #print(f"{sayi} geldi → 'q' basıldı.")


#def girisyap():



#chsec(ekran2xy)
#sunucusec(ekran2xy)
#sunucuchonay(ekran2xy)
#hesapsecimi(ekran2xy)