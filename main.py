#!/usr/bin/env python3
"""The World in One Page -- Friday 20 November 2026.

Draws a newspaper front page summing up the day's world news as one
1024x1024 PNG, using only the Python standard library.

Everything is drawn in code: a hand-built 5x7 bitmap font for all text,
geometric pictograms for each story, and a PNG encoder written from
zlib + struct. No network, no timestamps, no randomness, no hash-order
dependence -- every run writes byte-identical output.

Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py
Writes out/entry.png (or /output/entry.png when the variable is unset).
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

# Palette -----------------------------------------------------------------
PAPER = (247, 243, 232)   # newsprint
INK = (24, 24, 24)        # body ink
RED = (164, 30, 30)       # accent red
BLUE = (30, 58, 110)      # deep blue
SKY = (28, 38, 52)        # night sky in the lead picture
GOLD = (214, 164, 32)     # lit windows, flag stars
GREY = (128, 122, 110)    # smoke, muted rules
EMBER = (232, 122, 32)    # missile glow
FLAME = (245, 196, 66)    # explosion core
CLOUD = (232, 226, 210)   # light panel fill

# 5x7 bitmap font -----------------------------------------------------------
# Each glyph is 7 rows of 5 cells; '1' is ink, '0' is blank. Lowercase
# letters sit on rows 2-6 (x-height), ascenders reach row 0, descenders
# dip into row 6.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    'a': ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    'b': ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    'c': ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    'd': ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    'e': ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    'f': ("00110", "01000", "01000", "11110", "01000", "01000", "01000"),
    'g': ("00000", "00000", "01110", "10001", "10001", "00001", "01110"),
    'h': ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    'i': ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    'j': ("00100", "00000", "00100", "00100", "00100", "10100", "01000"),
    'k': ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    'l': ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    'm': ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    'n': ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    'o': ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    'p': ("00000", "00000", "11110", "10001", "11110", "10000", "10000"),
    'q': ("00000", "00000", "01111", "10001", "01111", "00001", "00001"),
    'r': ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    's': ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    't': ("00100", "00100", "11110", "00100", "00100", "00100", "00110"),
    'u': ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    'v': ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    'w': ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    'x': ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    'y': ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    'z': ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '\u2014': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    '\u00d7': ("00000", "10001", "01010", "00100", "01010", "10001", "00000"),
    '\u00b7': ("00000", "00000", "00000", "01100", "01100", "00000", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
}
BLANK = ("00000", "00000", "00000", "00000", "00000", "00000", "00000")


class Page:
    """An RGB canvas with drawing primitives."""

    def __init__(self):
        self.buf = bytearray(bytes(PAPER) * (W * H))

    def px(self, x, y, color):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.buf[i] = color[0]
            self.buf[i + 1] = color[1]
            self.buf[i + 2] = color[2]

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(W, x + w), min(H, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * W + x0) * 3
            self.buf[i:i + len(row)] = row

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def outline(self, x, y, w, h, color, thick=1):
        self.rect(x, y, w, thick, color)
        self.rect(x, y + h - thick, w, thick, color)
        self.rect(x, y, thick, h, color)
        self.rect(x + w - thick, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        """Bresenham line; thick draws a square brush at each step."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        half = thick // 2
        while True:
            self.rect(x0 - half, y0 - half, thick, thick, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(r * r - dy * dy))
            self.hline(cx - dx, cy + dy, 2 * dx + 1, color)

    # -- text -------------------------------------------------------------
    def text_w(self, s, scale):
        if not s:
            return 0
        return len(s) * 6 * scale - scale

    def text(self, x, y, s, scale, color):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, BLANK)
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 6 * scale
        return cx

    def text_center(self, y, s, scale, color, x0=36, x1=988):
        w = self.text_w(s, scale)
        self.text(x0 + (x1 - x0 - w) // 2, y, s, scale, color)

    def wrap(self, s, maxw, scale):
        """Greedy word wrap; returns a list of lines."""
        lines = []
        for chunk in s.split("\n"):
            words = chunk.split(" ")
            cur = ""
            for word in words:
                trial = word if not cur else cur + " " + word
                if self.text_w(trial, scale) <= maxw or not cur:
                    cur = trial
                else:
                    lines.append(cur)
                    cur = word
            if cur:
                lines.append(cur)
        return lines

    def para(self, x, y, s, scale, maxw, color, leading):
        for line in self.wrap(s, maxw, scale):
            self.text(x, y, line, scale, color)
            y += leading
        return y


# Pictograms ---------------------------------------------------------------
def draw_scales(p, x, y):
    """Scales of justice, 56x56 at (x, y)."""
    p.rect(x + 18, y + 48, 20, 3, INK)          # base
    p.rect(x + 27, y + 8, 2, 40, INK)          # post
    p.rect(x + 8, y + 10, 40, 2, INK)          # beam
    p.circle(x + 28, y + 6, 3, RED)            # knob
    for side in (0, 1):
        ax = x + 12 + side * 32                 # beam end
        p.line(ax, y + 12, ax - 8, y + 28, INK)
        p.line(ax, y + 12, ax + 8, y + 28, INK)
        p.line(ax - 8, y + 28, ax + 8, y + 28, RED, 2)
        p.line(ax - 8, y + 28, ax, y + 33, RED)
        p.line(ax + 8, y + 28, ax, y + 33, RED)


def draw_chart(p, x, y):
    """Falling market chart, 56x56 at (x, y)."""
    p.vline(x + 6, y + 6, 44, INK, 2)           # y axis
    p.hline(x + 6, y + 50, 44, INK, 2)          # x axis
    pts = [(10, 14), (20, 20), (28, 18), (38, 34), (48, 46)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        p.line(x + ax, y + ay, x + bx, y + by, RED, 3)
    p.line(x + 48, y + 46, x + 42, y + 44, RED, 2)   # arrowhead
    p.line(x + 48, y + 46, x + 46, y + 40, RED, 2)


def draw_stack(p, x, y):
    """Smokestack crossed out, 56x56 at (x, y)."""
    p.circle(x + 26, y + 10, 5, GREY)
    p.circle(x + 34, y + 5, 4, GREY)
    p.rect(x + 18, y + 16, 20, 36, INK)        # stack
    p.rect(x + 14, y + 12, 28, 4, INK)         # rim
    p.line(x + 4, y + 4, x + 52, y + 52, RED, 3)
    p.line(x + 52, y + 4, x + 4, y + 52, RED, 3)


def draw_tower(p, x, y):
    """Cracked skyscraper, 56x56 at (x, y)."""
    p.rect(x + 20, y + 8, 16, 44, INK)         # tower
    for wy in range(12, 48, 8):
        for wx in (24, 30):
            p.rect(x + wx, y + wy, 3, 4, GOLD)
    # crack zigzag down the tower face
    crack = [(28, 8), (32, 16), (26, 24), (32, 32), (27, 40), (31, 48)]
    for (ax, ay), (bx, by) in zip(crack, crack[1:]):
        p.line(x + ax, y + ay, x + bx, y + by, RED, 2)
    # impact burst at the top
    p.circle(x + 28, y + 8, 6, EMBER)
    p.circle(x + 28, y + 8, 3, FLAME)


def draw_flags(p, x, y):
    """EU and UK flags side by side, 56x56 at (x, y)."""
    # EU flag
    p.rect(x, y + 14, 26, 18, BLUE)
    for k in range(12):
        a = 2 * math.pi * k / 12
        dx = int(round(8 * math.cos(a)))
        dy = int(round(6 * math.sin(a)))
        p.px(x + 13 + dx, y + 23 + dy, GOLD)
    # UK flag (simplified)
    p.rect(x + 30, y + 14, 26, 18, BLUE)
    p.line(x + 30, y + 14, x + 56, y + 32, (240, 240, 240), 2)
    p.line(x + 56, y + 14, x + 30, y + 32, (240, 240, 240), 2)
    p.rect(x + 30, y + 21, 26, 4, (240, 240, 240))
    p.rect(x + 41, y + 14, 4, 18, (240, 240, 240))
    p.rect(x + 30, y + 22, 26, 2, RED)
    p.rect(x + 42, y + 14, 2, 18, RED)


def draw_lead_scene(p, x, y, w, h):
    """Night sky over a city skyline under a missile barrage."""
    p.rect(x, y, w, h, SKY)
    # stars (fixed positions)
    stars = [(30, 14), (90, 26), (150, 10), (210, 30), (280, 12), (340, 24),
             (410, 10), (470, 28), (540, 12), (610, 26), (680, 10), (740, 28),
             (800, 12), (860, 24), (920, 10), (60, 44), (500, 44), (700, 46)]
    for sx, sy in stars:
        p.px(x + sx, y + sy, (220, 220, 200))
        p.px(x + sx + 1, y + sy, (220, 220, 200))
    # missile trails: bright heads falling toward the city
    trails = [((640, 6), (560, 78)), ((760, 2), (700, 66)),
              ((880, 10), (830, 74)), ((430, 4), (380, 70))]
    for (ax, ay), (bx, by) in trails:
        p.line(x + ax, y + ay, x + bx, y + by, (240, 200, 120), 2)
        p.circle(x + bx, y + by, 6, EMBER)
        p.circle(x + bx, y + by, 3, FLAME)
    # drones: small light crosses with a red eye
    for dx, dy in [(180, 34), (330, 52), (590, 40)]:
        p.line(x + dx - 6, y + dy, x + dx + 6, y + dy, (170, 170, 160), 2)
        p.line(x + dx, y + dy - 4, x + dx, y + dy + 4, (170, 170, 160), 2)
        p.px(x + dx, y + dy, RED)
    # skyline silhouettes along the bottom
    buildings = [(0, 62, 58, 78), (58, 44, 46, 96), (104, 70, 60, 70),
                 (164, 38, 40, 102), (204, 58, 66, 82), (270, 30, 44, 110),
                 (314, 52, 58, 88), (372, 66, 52, 74), (424, 40, 46, 100),
                 (470, 58, 60, 82), (530, 34, 42, 106), (572, 56, 56, 84),
                 (628, 70, 48, 70), (676, 44, 54, 96), (730, 62, 50, 78),
                 (780, 36, 44, 104), (824, 56, 58, 84), (882, 68, 40, 72),
                 (922, 52, 30, 88)]
    for bx, bt, bw, bh in buildings:
        p.rect(x + bx, y + h - bh, bw, bh, (10, 10, 12))
    # lit windows
    for wx in range(14, w - 10, 26):
        for wy in range(h - 96, h - 12, 16):
            if (wx * 7 + wy * 3) % 5 < 2:
                p.rect(x + wx, y + wy, 3, 4, GOLD)
    # explosions over two rooftops
    for ex, ey in [(300, h - 106), (800, h - 100)]:
        for k in range(8):
            a = math.pi * k / 4
            p.line(x + ex, y + ey, x + ex + int(12 * math.cos(a)),
                   y + ey + int(12 * math.sin(a)), EMBER, 2)
        p.circle(x + ex, y + ey, 5, EMBER)
        p.circle(x + ex, y + ey, 3, FLAME)


# Page assembly ---------------------------------------------------------------
def draw_story(p, x, y, w, kicker, headline, summary, icon):
    """One story block: kicker, headline, summary, pictogram at top right."""
    p.text(x, y, kicker, 2, RED)
    icon(p, x + w - 56, y)
    y2 = y + 20
    y2 = p.para(x, y2, headline, 3, w - 64, INK, 24)
    p.para(x, y2 + 4, summary, 2, w, INK, 17)


def draw_page():
    p = Page()
    x0, x1 = 36, 988
    w = x1 - x0

    # Masthead ------------------------------------------------------------
    p.text_center(30, "THE WORLD IN ONE PAGE", 6, INK, x0, x1)
    # date line with flanking rules
    date = "Friday 20 November 2026"
    dw = p.text_w(date, 3)
    dcx = (W - dw) // 2
    p.hline(x0, 90, dcx - 20 - x0, INK, 2)
    p.hline(dcx + dw + 20, 90, x1 - (dcx + dw + 20), INK, 2)
    p.text(dcx, 80, date, 3, RED)
    # double rule under the masthead
    p.hline(x0, 110, w, INK, 3)
    p.hline(x0, 116, w, INK, 1)

    # Lead story ----------------------------------------------------------
    y = 130
    p.text(x0, y, "LEAD STORY \u00b7 UKRAINE", 2, RED)
    y = 152
    p.text(x0, y, "RUSSIA'S BIGGEST", 5, INK)
    p.text(x0, y + 42, "BARRAGE OF THE WAR", 5, INK)
    y = 242
    draw_lead_scene(p, x0, y, w, 140)
    y = 396
    lead = ("More than 400 drones and 110 missiles \u2014 27 of them "
            "ballistic \u2014 were fired at Ukraine overnight, killing eight "
            "and wounding 28. Two missiles and a drone also came down in "
            "Poland, which Warsaw called a deliberate provocation.")
    p.para(x0, y, lead, 2, w, INK, 19)

    # Rule above the story grid
    p.hline(x0, 468, w, INK, 1)

    # Five stories, two columns ------------------------------------------
    col_w = 466
    lx, rx = x0, x0 + col_w + 20
    p.vline(lx + col_w + 10, 486, 384, GREY, 1)

    draw_story(p, lx, 486, col_w, "MYANMAR",
               "MYANMAR REJECTS ICJ GENOCIDE RULING",
               "Myanmar calls the ruling unfair, a day after the court "
               "found it guilty of genocide against the Rohingya.",
               draw_scales)
    draw_story(p, lx, 616, col_w, "MARKETS",
               "ANTHROPIC FALLS 10% AS ASIAN MARKETS SELL OFF",
               "Anthropic falls about 10% as "
               "Asian stocks slide to their worst week since 2020.",
               draw_chart)
    draw_story(p, lx, 746, col_w, "CLIMATE \u00b7 COP31",
               "COP31 DRAFT DROPS FOSSIL-FUEL LANGUAGE",
               "Negotiators strip all fossil-fuel language from the draft "
               "deal as the Antalya summit reaches its Friday deadline.",
               draw_stack)
    draw_story(p, rx, 486, col_w, "MIDDLE EAST",
               "HOUTHI MISSILE DAMAGES RIYADH'S PIF TOWER",
               "A Houthi missile hits the PIF Tower, Riyadh's tallest, "
               "blowing out windows over seven to eight floors.",
               draw_tower)
    draw_story(p, rx, 616, col_w, "EUROPE",
               "SECOND EU-UK SUMMIT HELD IN BRUSSELS",
               "The EU and Britain hold their second summit since the "
               "reset, with PM Keir Starmer meeting EU leaders in Brussels.",
               draw_flags)

    # By-the-numbers box ---------------------------------------------------
    bx, by, bw, bh = rx, 746, col_w, 124
    p.rect(bx, by, bw, bh, CLOUD)
    p.outline(bx, by, bw, bh, INK, 2)
    p.text_center(by + 10, "BY THE NUMBERS", 2, RED, bx, bx + bw)
    rows = [("400+", "drones fired at Ukraine"),
            ("110+", "missiles in the barrage"),
            ("27", "of them ballistic")]
    ry = by + 34
    for num, label in rows:
        p.text(bx + 24, ry, num, 4, RED)
        p.text(bx + 140, ry + 5, label, 2, INK)
        ry += 30

    # Briefs strip ---------------------------------------------------------
    bx, by, bw, bh = x0, 884, w, 88
    p.rect(bx, by, bw, bh, CLOUD)
    p.outline(bx, by, bw, bh, INK, 2)
    p.text(bx + 16, by + 9, "IN BRIEF", 2, RED)
    briefs = [
        "GTA VI \u2014 $3.79B on day one, the biggest launch ever.",
        "Haiti police kill 34 suspected gang members in a raid.",
        "Fiona the hippo dies at Cincinnati Zoo, aged nine.",
    ]
    bw3 = (bw - 32 - 2 * 12) // 3
    for i, b in enumerate(briefs):
        cx = bx + 16 + i * (bw3 + 12)
        if i:
            p.vline(cx - 6, by + 28, bh - 38, GREY, 1)
        p.para(cx, by + 28, b, 2, bw3, INK, 17)

    # Footer ---------------------------------------------------------------
    p.text_center(982, "THE WORLD IN ONE PAGE \u2014 FRIDAY 20 NOVEMBER 2026",
                  2, GREY, x0, x1)
    return p


# PNG encoder ---------------------------------------------------------------
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, page):
    raw = bytearray()
    for yy in range(H):
        raw.append(0)  # filter: none
        raw += page.buf[yy * W * 3:(yy + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    data = (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(data)


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    page = draw_page()
    write_png(os.path.join(outdir, "entry.png"), page)


if __name__ == "__main__":
    main()
