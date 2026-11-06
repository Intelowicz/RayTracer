import math
import sys

import pygame

pygame.init()

SZER, WYS = 900, 650
ekran = pygame.display.set_mode((SZER, WYS))
pygame.display.set_caption("Ray tracer 2D")
zegar = pygame.time.Clock()
czcionka = pygame.font.SysFont("dejavusans", 20)

EPS = 1e-4
SZARY = (120, 120, 140)
ZOLTY = (255, 230, 120)


class Kolo:
    def __init__(self, x, y, r=40):
        self.x, self.y, self.r = x, y, r

    def trafienie(self, ox, oy, dx, dy):
        fx, fy = ox - self.x, oy - self.y
        b = 2 * (fx * dx + fy * dy)
        c = fx * fx + fy * fy - self.r * self.r
        wyroznik = b * b - 4 * c
        if wyroznik < 0:
            return None
        s = math.sqrt(wyroznik)
        for t in ((-b - s) / 2, (-b + s) / 2):
            if t > EPS:
                hx, hy = ox + dx * t, oy + dy * t
                return t, (hx - self.x) / self.r, (hy - self.y) / self.r
        return None

    def rysuj(self):
        pygame.draw.circle(ekran, SZARY, (int(self.x), int(self.y)), self.r)


class Prostokat:
    def __init__(self, x, y, w=60, h=60):
        self.r = pygame.Rect(x, y, w, h)

    def trafienie(self, ox, oy, dx, dy):
        if abs(dx) < 1e-9:
            dx = 1e-9
        if abs(dy) < 1e-9:
            dy = 1e-9
        tx1 = (self.r.left - ox) / dx
        tx2 = (self.r.right - ox) / dx
        ty1 = (self.r.top - oy) / dy
        ty2 = (self.r.bottom - oy) / dy
        txmin, txmax = min(tx1, tx2), max(tx1, tx2)
        tymin, tymax = min(ty1, ty2), max(ty1, ty2)
        t_wejscie = max(txmin, tymin)
        t_wyjscie = min(txmax, tymax)
        if t_wejscie > t_wyjscie or t_wyjscie < EPS or t_wejscie < EPS:
            return None
        if txmin >= tymin:
            nx, ny = (-1 if dx > 0 else 1), 0
        else:
            nx, ny = 0, (-1 if dy > 0 else 1)
        return t_wejscie, nx, ny

    def rysuj(self):
        pygame.draw.rect(ekran, SZARY, self.r)


def sled(ox, oy, dx, dy, odbicia):
    """Zwraca listę punktów, przez które przechodzi promień."""
    punkty = [(ox, oy)]
    for krok in range(odbicia + 1):
        najblizej = None
        for ob in obiekty:
            wynik = ob.trafienie(ox, oy, dx, dy)
            if wynik and (najblizej is None or wynik[0] < najblizej[0]):
                najblizej = wynik
        if najblizej is None:
            punkty.append((ox + dx * 2000, oy + dy * 2000))
            break
        t, nx, ny = najblizej
        ox, oy = ox + dx * t, oy + dy * t
        punkty.append((ox, oy))
        if krok == odbicia:
            break
        dot = dx * nx + dy * ny
        dx, dy = dx - 2 * dot * nx, dy - 2 * dot * ny
    return punkty


def przelicz():
    warstwa = pygame.Surface((SZER, WYS), pygame.SRCALPHA)
    for i in range(liczba_promieni):
        kat = 2 * math.pi * i / liczba_promieni
        pkt = sled(slonce[0], slonce[1], math.cos(kat), math.sin(kat), odbicia)
        pkt = [(int(x), int(y)) for x, y in pkt]
        pygame.draw.lines(warstwa, (255, 240, 150, 60), False, pkt, 1)
    return warstwa


obiekty = []
slonce = [450, 325]
liczba_promieni = 300
odbicia = 0          # 0 = obiekty pochłaniają światło (cienie)
tryb = "kolo"
warstwa = przelicz()

while True:
    for zd in pygame.event.get():
        if zd.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if zd.type == pygame.MOUSEBUTTONDOWN:
            if zd.button == 1:
                slonce = list(zd.pos)
            elif zd.button == 3:
                x, y = zd.pos
                if tryb == "kolo":
                    obiekty.append(Kolo(x, y))
                else:
                    obiekty.append(Prostokat(x - 30, y - 30))
            warstwa = przelicz()
        if zd.type == pygame.KEYDOWN:
            if zd.key == pygame.K_UP:
                liczba_promieni = min(liczba_promieni + 50, 2000)
            elif zd.key == pygame.K_DOWN:
                liczba_promieni = max(liczba_promieni - 50, 10)
            elif zd.key == pygame.K_b:
                odbicia = (odbicia + 1) % 4
            elif zd.key == pygame.K_c:
                tryb = "kolo"
            elif zd.key == pygame.K_r:
                tryb = "kwadrat"
            elif zd.key == pygame.K_BACKSPACE:
                obiekty.clear()
            else:
                continue
            warstwa = przelicz()

    ekran.fill((0, 0, 0))
    ekran.blit(warstwa, (0, 0))
    for ob in obiekty:
        ob.rysuj()
    pygame.draw.circle(ekran, (255, 240, 120), slonce, 14)
    pygame.draw.circle(ekran, (255, 240, 120), slonce, 22, 2)

    tekst = [
        f"Promienie: {liczba_promieni}  (strzałki góra/dół)",
        f"Odbicia: {odbicia}  (B - zmiana)",
        f"Dodawanie: {'okrąg' if tryb == 'kolo' else 'kwadrat'}  (C/R)",
        "LPM - przesuń słońce, PPM - dodaj obiekt, Backspace - wyczyść",
    ]
    for i, linia in enumerate(tekst):
        ekran.blit(czcionka.render(linia, True, (230, 230, 230)), (10, 10 + i * 24))

    pygame.display.flip()
    zegar.tick(60)