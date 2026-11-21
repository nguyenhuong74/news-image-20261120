#!/usr/bin/env python3
"""The World in One Page -- Friday 20 November 2026.

Draws a one-page newspaper front page summing up 20 November 2026's
world news as a 1024x1024 PNG, using only the Python standard library.

Everything is drawn in code: a hand-written 5x7 bitmap font, simple
geometric pictograms, and a PNG encoder built from zlib + struct.
No network, no clock, no randomness -- two runs write byte-identical
files.

Run: MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs, one row per string, "#" = ink.  Only capitals are
# stored; draw_text() upper-cases its input first.

FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
}

# Colours (R, G, B).
PAPER = (253, 246, 227)   # newsprint cream
INK = (24, 24, 24)        # near-black
RED = (178, 34, 34)       # headline red
BLUE = (28, 68, 142)      # deep blue
GREY = (110, 108, 100)    # muted grey
LIGHT = (238, 228, 205)   # pale panel fill
GOLD = (196, 141, 26)     # accent gold
TEAL = (18, 110, 105)     # teal accent


class Canvas:
    """A plain RGB pixel buffer with tiny drawing helpers."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        self.fill(0, 0, w, h, bg)

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def fill(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def hline(self, x, y, length, c, thick=1):
        self.fill(x, y, length, thick, c)

    def vline(self, x, y, length, c, thick=1):
        self.fill(x, y, thick, length, c)

    def rect(self, x, y, w, h, c, thick=1):
        self.hline(x, y, w, c, thick)
        self.hline(x, y + h - thick, w, c, thick)
        self.vline(x, y, h, c, thick)
        self.vline(x + w - thick, y, h, c, thick)

    def line(self, x0, y0, x1, y1, c, thick=1):
        # Bresenham line.
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.fill(x0 - thick // 2, y0 - thick // 2, thick, thick, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, filled=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if filled:
                    if d2 <= r * r:
                        self.px(xx, yy, c)
                else:
                    if (r - 1) ** 2 <= d2 <= r * r:
                        self.px(xx, yy, c)

    def triangle(self, x0, y0, x1, y1, x2, y2, c):
        # Scanline fill of a triangle.
        ys = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = ys
        if ay == cy:
            return
        for y in range(ay, cy + 1):
            if y < by:
                t1 = (y - ay) / max(1, by - ay)
                xa = ax + (bx - ax) * t1
            else:
                t1 = (y - by) / max(1, cy - by)
                xa = bx + (cx - bx) * t1
            t2 = (y - ay) / (cy - ay)
            xb = ax + (cx - ax) * t2
            lo, hi = int(min(xa, xb)), int(max(xa, xb))
            for x in range(lo, hi + 1):
                self.px(x, y, c)


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(cv, x, y, s, scale, color):
    """Draw upper-cased text at (x, y); returns the x just past the text."""
    s = s.upper()
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    cv.fill(cx + col * scale, y + row * scale,
                            scale, scale, color)
        cx += 6 * scale
    return cx


def draw_centered(cv, cx, y, s, scale, color):
    draw_text(cv, cx - text_width(s, scale) // 2, y, s, scale, color)


def wrap_text(s, max_chars):
    """Greedy word wrap; returns a list of lines, each <= max_chars."""
    lines, cur = [], ""
    for word in s.split(" "):
        if cur and len(cur) + 1 + len(word) > max_chars:
            lines.append(cur)
            cur = word
        else:
            cur = cur + " " + word if cur else word
    if cur:
        lines.append(cur)
    return lines


def draw_para(cv, x, y, s, scale, color, max_chars, leading):
    """Draw a wrapped paragraph; returns the y just below it."""
    for line in wrap_text(s, max_chars):
        draw_text(cv, x, y, line, scale, color)
        y += 7 * scale + leading
    return y


# ------------------------------------------------------------------- PNG
def write_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.buf[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ------------------------------------------------------------- pictograms
def pic_barrage(cv, x, y, s):
    """Kyiv skyline under a missile barrage: the lead story."""
    base = y + 96 * s // 10
    # Skyline blocks, tallest in the middle.
    blocks = [(0, 46, 34, 50), (38, 30, 30, 66), (72, 58, 36, 38),
              (112, 22, 30, 74), (146, 40, 34, 56)]
    for bx, top, bw, bh in blocks:
        cv.fill(x + bx * s // 10, base - bh * s // 10,
                bw * s // 10, bh * s // 10, INK)
        for wy in range(2):
            for wx in range(bw // 14):
                cv.fill(x + (bx + 6 + wx * 14) * s // 10,
                        base - (bh - 8 - wy * 16) * s // 10,
                        5 * s // 10, 6 * s // 10, GOLD)
    # Three missile streaks diving from the top right.
    for sx, sy, ex, ey in ((150, 0, 96, 34), (176, 6, 128, 36),
                           (196, 16, 158, 40)):
        cv.line(x + sx * s // 10, y + sy * s // 10,
                x + ex * s // 10, y + ey * s // 10, RED, 3)
    # Blast burst over the tallest block.
    bx, by = x + 127 * s // 10, y + 22 * s // 10
    for dx, dy in ((-16, 0), (16, 0), (0, -16), (0, 12), (-11, -11),
                   (11, -11), (-11, 9), (11, 9)):
        cv.line(bx, by, bx + dx * s // 10, by + dy * s // 10, RED, 3)
    cv.circle(bx, by, 6 * s // 10, GOLD)
    cv.circle(bx, by, 3 * s // 10, RED)
    # Ground line and a small Polish flag marker at the right edge.
    cv.hline(x, base, 190 * s // 10, INK, 3)
    fx, fy = x + 168 * s // 10, base - 30 * s // 10
    cv.vline(fx, fy, 30 * s // 10, INK, 2)
    cv.fill(fx + 2, fy, 18 * s // 10, 5 * s // 10, PAPER)
    cv.rect(fx + 2, fy, 18 * s // 10, 10 * s // 10, INK, 1)
    cv.fill(fx + 2, fy + 5 * s // 10, 18 * s // 10, 5 * s // 10, RED)


def pic_scales(cv, x, y, s):
    """Scales of justice, tipped: Myanmar rejects the ICJ ruling."""
    cx = x + 60 * s // 10
    top = y + 8 * s // 10
    cv.vline(cx, top, 78 * s // 10, INK, 3)
    # Beam tilted: the left pan hangs lower.
    cv.line(cx - 46 * s // 10, top + 2 * s // 10,
            cx + 46 * s // 10, top + 12 * s // 10, INK, 3)
    cv.circle(cx, top + 4 * s // 10, 5 * s // 10, GOLD)
    for side, drop in ((-1, 10), (1, 0)):
        px = cx + side * 42 * s // 10
        py = top + (6 + drop) * s // 10
        cv.line(px, py, px - 16 * s // 10, py + 34 * s // 10, INK, 2)
        cv.line(px, py, px + 16 * s // 10, py + 34 * s // 10, INK, 2)
        cv.hline(px - 18 * s // 10, py + 34 * s // 10, 36 * s // 10, GOLD, 4)
    cv.hline(cx - 30 * s // 10, top + 82 * s // 10, 60 * s // 10, INK, 4)
    # A red "no" cross over the right pan.
    rx, ry = cx + 42 * s // 10, top + 46 * s // 10
    cv.line(rx - 8 * s // 10, ry - 8 * s // 10,
            rx + 8 * s // 10, ry + 8 * s // 10, RED, 3)
    cv.line(rx - 8 * s // 10, ry + 8 * s // 10,
            rx + 8 * s // 10, ry - 8 * s // 10, RED, 3)


def pic_fall(cv, x, y, s):
    """Falling bars and a down arrow: the AI sell-off."""
    base = y + 84 * s // 10
    heights = (74, 58, 40, 24)
    for i, hh in enumerate(heights):
        bx = x + 12 * s // 10 + i * 42 * s // 10
        col = RED if i < 2 else TEAL
        cv.fill(bx, base - hh * s // 10, 30 * s // 10, hh * s // 10, col)
    cv.hline(x + 6 * s // 10, base, 180 * s // 10, INK, 3)
    cv.line(x + 14 * s // 10, base - 78 * s // 10,
            x + 172 * s // 10, base - 22 * s // 10, RED, 3)
    cv.triangle(x + 172 * s // 10, base - 34 * s // 10,
                x + 150 * s // 10, base - 20 * s // 10,
                x + 172 * s // 10, base - 8 * s // 10, RED)


def pic_stack(cv, x, y, s):
    """Smokestack with its smoke crossed out: COP31 drops fossil fuels."""
    base = y + 88 * s // 10
    # Stack: a straight column, wider at the foot.
    cv.fill(x + 34 * s // 10, y + 22 * s // 10, 20 * s // 10,
            base - (y + 22 * s // 10), INK)
    cv.fill(x + 30 * s // 10, base - 8 * s // 10, 28 * s // 10,
            8 * s // 10, INK)
    cv.fill(x + 32 * s // 10, y + 18 * s // 10, 24 * s // 10, 5 * s // 10, INK)
    # Smoke puffs rising to the right.
    for px, py, r in ((78, 30, 10), (102, 20, 12), (128, 12, 9)):
        cv.circle(x + px * s // 10, y + py * s // 10, r * s // 10, GREY)
    # Red cross over the smoke.
    cx, cy = x + 104 * s // 10, y + 22 * s // 10
    cv.line(cx - 22 * s // 10, cy - 22 * s // 10,
            cx + 22 * s // 10, cy + 22 * s // 10, RED, 4)
    cv.line(cx - 22 * s // 10, cy + 22 * s // 10,
            cx + 22 * s // 10, cy - 22 * s // 10, RED, 4)
    # Small sun in the corner.
    cv.circle(x + 158 * s // 10, y + 66 * s // 10, 12 * s // 10, GOLD)


def pic_tower(cv, x, y, s):
    """A skyscraper with a cracked, burning crown: the PIF Tower hit."""
    base = y + 92 * s // 10
    tx, tw = x + 52 * s // 10, 62 * s // 10
    cv.fill(tx, y + 12 * s // 10, tw, base - (y + 12 * s // 10), BLUE)
    cv.rect(tx, y + 12 * s // 10, tw, base - (y + 12 * s // 10), INK, 2)
    # Window grid.
    for r in range(5):
        for c in range(3):
            cv.fill(tx + 8 * s // 10 + c * 20 * s // 10,
                    y + 22 * s // 10 + r * 14 * s // 10,
                    10 * s // 10, 7 * s // 10, PAPER)
    # Zigzag crack down the face.
    cx = tx + 31 * s // 10
    cv.line(cx, y + 14 * s // 10, cx - 8 * s // 10, y + 34 * s // 10, RED, 3)
    cv.line(cx - 8 * s // 10, y + 34 * s // 10, cx + 6 * s // 10,
            y + 54 * s // 10, RED, 3)
    cv.line(cx + 6 * s // 10, y + 54 * s // 10, cx - 6 * s // 10,
            y + 74 * s // 10, RED, 3)
    # Flame licking the crown.
    fx = tx + tw // 2
    cv.triangle(fx - 16 * s // 10, y + 14 * s // 10, fx, y - 6 * s // 10,
                fx + 16 * s // 10, y + 14 * s // 10, RED)
    cv.triangle(fx - 8 * s // 10, y + 14 * s // 10, fx + 2 * s // 10,
                y + 2 * s // 10, fx + 10 * s // 10, y + 14 * s // 10, GOLD)
    # Rooftop of a neighbour block.
    cv.fill(x + 130 * s // 10, base - 34 * s // 10, 46 * s // 10,
            34 * s // 10, GREY)
    cv.rect(x + 130 * s // 10, base - 34 * s // 10, 46 * s // 10,
            34 * s // 10, INK, 2)


def pic_flags(cv, x, y, s):
    """Two flags on one pole line: the EU and Britain meet in Brussels."""
    base = y + 88 * s // 10
    # EU flag: blue field, ring of gold stars.
    ex, ey = x + 8 * s // 10, y + 14 * s // 10
    cv.fill(ex, ey, 74 * s // 10, 48 * s // 10, BLUE)
    cv.rect(ex, ey, 74 * s // 10, 48 * s // 10, INK, 2)
    for k in range(8):
        ang = k * 3.14159 / 4
        sx = ex + 37 * s // 10 + int(16 * s // 10 * _cos(ang))
        sy = ey + 24 * s // 10 + int(14 * s // 10 * _sin(ang))
        cv.circle(sx, sy, 2 * s // 10, GOLD)
    # UK flag: blue field, white saltire and red cross.
    ux, uy = x + 102 * s // 10, y + 14 * s // 10
    cv.fill(ux, uy, 74 * s // 10, 48 * s // 10, BLUE)
    cv.rect(ux, uy, 74 * s // 10, 48 * s // 10, INK, 2)
    cv.line(ux, uy, ux + 74 * s // 10, uy + 48 * s // 10, PAPER, 4)
    cv.line(ux + 74 * s // 10, uy, ux, uy + 48 * s // 10, PAPER, 4)
    cv.hline(ux, uy + 20 * s // 10, 74 * s // 10, PAPER, 8)
    cv.vline(ux + 33 * s // 10, uy, 48 * s // 10, PAPER, 8)
    cv.hline(ux, uy + 22 * s // 10, 74 * s // 10, RED, 4)
    cv.vline(ux + 35 * s // 10, uy, 48 * s // 10, RED, 4)
    # Shared ground line and a handshake arc beneath.
    cv.hline(x, base, 184 * s // 10, INK, 3)
    cv.line(x + 62 * s // 10, base - 12 * s // 10,
            x + 92 * s // 10, base - 24 * s // 10, INK, 3)
    cv.line(x + 92 * s // 10, base - 24 * s // 10,
            x + 122 * s // 10, base - 12 * s // 10, INK, 3)


def _cos(a):
    # Tiny cosine for the star ring (a in radians, 8 points only).
    table = (1.0, 0.7071, 0.0, -0.7071, -1.0, -0.7071, 0.0, 0.7071)
    return table[int(round(a / 0.7853981633974483)) % 8]


def _sin(a):
    return _cos(a - 1.5707963267948966)


def pic_pad(cv, x, y, s):
    """A game controller: GTA VI's record launch day."""
    cv.fill(x + 2 * s // 10, y + 8 * s // 10, 32 * s // 10, 16 * s // 10, INK)
    cv.circle(x + 8 * s // 10, y + 16 * s // 10, 4 * s // 10, GOLD)
    cv.circle(x + 28 * s // 10, y + 16 * s // 10, 4 * s // 10, GOLD)
    cv.circle(x + 24 * s // 10, y + 12 * s // 10, 2 * s // 10, RED)
    cv.circle(x + 30 * s // 10, y + 20 * s // 10, 2 * s // 10, TEAL)


def pic_shield(cv, x, y, s):
    """A police shield: the Haiti operation."""
    sx, sy = x + 18 * s // 10, y + 2 * s // 10
    cv.triangle(sx - 15 * s // 10, sy, sx + 15 * s // 10, sy,
                sx, sy + 28 * s // 10, BLUE)
    cv.fill(sx - 15 * s // 10, sy, 30 * s // 10, 10 * s // 10, BLUE)
    cv.circle(sx, sy + 12 * s // 10, 4 * s // 10, GOLD)


def pic_hippo(cv, x, y, s):
    """Fiona the hippo: round body, big snout, small ears."""
    bx, by = x + 4 * s // 10, y + 12 * s // 10
    # Body and head.
    cv.circle(bx + 14 * s // 10, by + 8 * s // 10, 12 * s // 10, GREY)
    cv.circle(bx + 26 * s // 10, by + 6 * s // 10, 8 * s // 10, GREY)
    # Ears.
    cv.circle(bx + 22 * s // 10, by - 2 * s // 10, 3 * s // 10, GREY)
    cv.circle(bx + 30 * s // 10, by - 2 * s // 10, 3 * s // 10, GREY)
    # Snout and nostrils.
    cv.circle(bx + 32 * s // 10, by + 8 * s // 10, 4 * s // 10, INK)
    cv.px(bx + 31 * s // 10, by + 7 * s // 10, PAPER)
    cv.px(bx + 33 * s // 10, by + 7 * s // 10, PAPER)
    # Eye and legs.
    cv.circle(bx + 26 * s // 10, by + 2 * s // 10, 2 * s // 10, INK)
    cv.fill(bx + 6 * s // 10, by + 16 * s // 10, 4 * s // 10, 8 * s // 10, INK)
    cv.fill(bx + 18 * s // 10, by + 16 * s // 10, 4 * s // 10, 8 * s // 10, INK)
    # A small red heart above.
    hx, hy = bx + 12 * s // 10, by - 6 * s // 10
    cv.circle(hx - 3 * s // 10, hy, 3 * s // 10, RED)
    cv.circle(hx + 3 * s // 10, hy, 3 * s // 10, RED)
    cv.triangle(hx - 6 * s // 10, hy + 1 * s // 10,
                hx + 6 * s // 10, hy + 1 * s // 10,
                hx, hy + 7 * s // 10, RED)


# ---------------------------------------------------------------- layout
def story_block(cv, x, y, w, h, kicker, headline, body, pic, pic_s=10):
    """One story cell: kicker, headline, pictogram, body text."""
    cv.rect(x, y, w, h, INK, 2)
    cv.fill(x + 2, y + 2, w - 4, 20, LIGHT)
    draw_text(cv, x + 10, y + 7, kicker, 1, RED)
    hy = draw_para(cv, x + 10, y + 30, headline, 2, INK,
                   (w - 20) // 12, 4)
    px, py = x + 10, hy
    pic(cv, px, py, pic_s)
    tx = px + 200 * pic_s // 10 + 8
    draw_para(cv, tx, hy + 6, body, 1, INK, (x + w - tx - 10) // 6, 3)


def brief(cv, x, y, w, kicker, text, pic, pic_s=10):
    draw_text(cv, x + 48, y, kicker, 1, RED)
    draw_para(cv, x + 48, y + 12, text, 1, INK, (w - 58) // 6, 2)
    pic(cv, x, y - 2, pic_s)


def build():
    cv = Canvas(W, H, PAPER)
    M = 24                      # outer margin
    CW = W - 2 * M              # content width

    # ---- Masthead ------------------------------------------------------
    cv.hline(M, 18, CW, INK, 4)
    draw_centered(cv, W // 2, 30, "THE WORLD IN ONE PAGE", 5, INK)
    draw_centered(cv, W // 2, 74, "FRIDAY 20 NOVEMBER 2026", 2, RED)
    draw_centered(cv, W // 2, 96, "SIX STORIES AND THREE BRIEFS FROM ONE DAY",
                  1, GREY)
    cv.hline(M, 116, CW, INK, 4)
    cv.hline(M, 121, CW, INK, 1)

    # ---- Lead story: the barrage on Ukraine ----------------------------
    ly, lh = 132, 218
    cv.rect(M, ly, CW, lh, INK, 3)
    cv.fill(M + 3, ly + 3, CW - 6, 22, LIGHT)
    draw_text(cv, M + 12, ly + 10, "LEAD  -  KYIV AND POLAND", 1, RED)
    draw_text(cv, M + 12, ly + 36,
              "RUSSIA'S BIGGEST BARRAGE YET", 3, INK)
    pic_barrage(cv, M + 24, ly + 84, 10)
    tx = M + 260
    after = draw_para(cv, tx, ly + 84,
                      "More than 400 drones and 110 missiles, 27 of them "
                      "ballistic, rain down on Kyiv and nine other regions "
                      "overnight. Eight people are killed and 28 wounded; "
                      "three bridges in Kyiv are hit and power is cut.",
                      1, INK, (M + CW - tx - 16) // 6, 4)
    draw_para(cv, tx, after + 14,
              "Two missiles and a drone come down in Poland. Warsaw calls "
              "it a deliberate provocation; NATO calls it a violation.",
              1, GREY, (M + CW - tx - 16) // 6, 4)

    # ---- Grid of five stories + numbers box ---------------------------
    gy = 366
    gw = (CW - 16) // 2
    gh = 148
    rows = [
        ("THE HAGUE  -  JUSTICE",
         "MYANMAR CALLS RULING UNFAIR",
         "Myanmar rejects the World Court's genocide ruling as unfair. "
         "Britain expels its defence attache and seeks an urgent UN "
         "Security Council session on the judgment.",
         pic_scales),
        ("NEW YORK  -  MARKETS",
         "AI SELLOFF DEEPENS",
         "Anthropic slides about 10% on its second day, to $87, "
         "towards its $83 offer price. The Nikkei falls 5.1% and the "
         "Kospi 5.2%; Asia heads for its worst week since 2020.",
         pic_fall),
        ("ANTALYA  -  CLIMATE",
         "COP31 DROPS FOSSIL FUELS",
         "Talks hit their Friday deadline with fossil-fuel language "
         "stripped from the draft deal. For the first time, a COP text "
         "admits the 1.5C limit will be overshot.",
         pic_stack),
        ("RIYADH  -  MIDDLE EAST",
         "RIYADH'S TALLEST TOWER HIT",
         "Saudi civil defence confirms a Houthi missile damaged the "
         "PIF Tower, blowing out windows across seven to eight floors. "
         "No injuries are reported.",
         pic_tower),
        ("BRUSSELS  -  DIPLOMACY",
         "EU AND UK MEET AGAIN",
         "The EU and Britain hold their second summit since the reset. "
         "PM Andy Burnham meets Costa and von der Leyen on trade, "
         "youth mobility and defence.",
         pic_flags),
    ]
    for i, (kick, head, body, pic) in enumerate(rows):
        gx = M + (i % 2) * (gw + 16)
        gyy = gy + (i // 2) * (gh + 12)
        story_block(cv, gx, gyy, gw, gh, kick, head, body, pic)

    # Numbers box in the sixth cell.
    nx = M + gw + 16
    ny = gy + 2 * (gh + 12)
    cv.rect(nx, ny, gw, gh, INK, 2)
    cv.fill(nx + 2, ny + 2, gw - 4, 20, LIGHT)
    draw_text(cv, nx + 10, ny + 7, "THE DAY IN NUMBERS", 1, RED)
    nums = [("400+", "drones in the barrage"),
            ("110", "missiles, 27 ballistic"),
            ("-5.1%", "Nikkei on Friday"),
            ("$3.79B", "GTA VI day-one sales"),
            ("34", "killed in Haiti operation")]
    yy = ny + 32
    for big, small in nums:
        draw_text(cv, nx + 12, yy, big, 2, INK)
        draw_text(cv, nx + 130, yy + 3, small, 1, GREY)
        yy += 20

    # ---- Briefs strip ---------------------------------------------------
    by = gy + 3 * (gh + 12) + 4
    cv.hline(M, by, CW, INK, 3)
    draw_text(cv, M, by + 10, "IN BRIEF", 2, RED)
    bw = (CW - 32) // 3
    briefs = [
        ("GTA VI", "Take-Two says GTA VI made $3.79 billion in day-one "
         "sales, the biggest entertainment launch ever, after 32.5 "
         "million pre-orders.", pic_pad),
        ("HAITI", "Police say 34 suspected gang members were killed in "
         "an operation, as Haiti's security crisis grinds on.", pic_shield),
        ("FIONA", "Fiona, the Cincinnati Zoo's famous hippo, dies aged "
         "nine after swallowing a visitor's hat. Fans mourn worldwide.",
         pic_hippo),
    ]
    for i, (kick, text, pic) in enumerate(briefs):
        bx = M + i * (bw + 16)
        brief(cv, bx, by + 38, bw, kick, text, pic)
        if i:
            cv.vline(bx - 8, by + 36, 84, GREY, 1)

    # ---- Footer ----------------------------------------------------------
    fy = by + 136
    cv.hline(M, fy, CW, INK, 2)
    draw_centered(cv, W // 2, fy + 10,
                  "DRAWN IN CODE  -  NO PHOTOGRAPHS  -  SOURCES: REUTERS, "
                  "AP, BBC, UN NEWS, CBC", 1, GREY)
    draw_centered(cv, W // 2, fy + 24,
                  "THE WORLD IN ONE PAGE  -  20 NOVEMBER 2026", 1, GREY)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    path = os.path.join(out_dir, "entry.png")
    size = write_png(cv, path)
    print(f"wrote {path}: {cv.w}x{cv.h}, {size} bytes")


if __name__ == "__main__":
    main()
