#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║   JPL DEEP SPACE NETWORK - PROBE MISSION SIMULATOR v1.0         ║
║   JET PROPULSION LABORATORY / CALIFORNIA INST. OF TECHNOLOGY    ║
║   © 1977  --  MISSION CONTROL SOFTWARE DIVISION                 ║
╚══════════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import scrolledtext
import random
import math

# ─── PALETTE ──────────────────────────────────────────────────────────────────
BLACK    = "#000000"
DARK     = "#080808"
GREEN    = "#33FF33"
DIM      = "#1A6B1A"
DIMMER   = "#0D3A0D"
AMBER    = "#FFB000"
BRIGHT   = "#99FF99"
RED      = "#FF3333"
ORANGE   = "#FF8800"
WHITE_G  = "#CCFFCC"

# ─── GAME CONSTANTS ───────────────────────────────────────────────────────────
CANVAS_W, CANVAS_H = 560, 290
PANEL_W             = 185
WIN_W               = CANVAS_W + PANEL_W + 20
WIN_H               = 700
AU_PER_SECTOR       = 0.45          # Astronomical units per sector
LIGHT_MIN_PER_AU    = 8.317         # Light-travel minutes per AU

STAR_COUNT          = 220
NEBULA_COUNT        = 6

# ─── CELESTIAL DATA ───────────────────────────────────────────────────────────
PLANET_NAMES = [
    "JUPITER","SATURN","URANUS","NEPTUNE","PLUTO","PROXIMA-IV",
    "KEPLER-7B","BARNARD-2","ROSS-128-B","WOLF-1061C","HD-40307G",
    "GLIESE-667C","TAU-CETI-E","YZ-CETI-D","TRAPPIST-1E",
]
ASTEROID_NAMES = [
    "1977-UX1","1977-BK3","1978-AA","1979-BC7","CERES-DELTA",
    "PALLAS-III","VESTA-BETA","HYGIEA-2","DAVIDA-C","INTERAMNIA-9",
    "CAMILLA-B","PSYCHE-7","EUPHROSYNE-A","SYLVIA-6","HERCULINA-3",
]
COMET_NAMES = [
    "KOHOUTEK-2","HALLEY-BETA","ENCKE-IV","BORRELLY-2","WILD-5",
    "TEMPEL-III","SHOEMAKER-A","IKEYA-SEKI-2","WEST-B","BRADFIELD-3",
]
MOON_NAMES = [
    "IO-ALPHA","EUROPA-BETA","GANYMEDE-C","CALLISTO-D","TITAN-II",
    "ENCELADUS-A","TRITON-B","CHARON-II","OBERON-A","TITANIA-C",
    "MIRANDA-B","ARIEL-D","UMBRIEL-A","DIONE-C","RHEA-II",
]

PLANET_COMP = [
    "HYDROGEN/HELIUM GAS GIANT","ROCKY SILICATE SURFACE",
    "ICE GIANT - METHANE ENVELOPE","NITROGEN/OXYGEN ATMOSPHERE",
    "SULFUR DIOXIDE VOLCANIC ATMOS","CARBON DIOXIDE DENSE ATMOS",
    "AMMONIA CLOUD BANDS DETECTED","WATER VAPOR SIGNATURE STRONG",
]
ASTEROID_COMP = [
    "CARBONACEOUS CHONDRITE","SILICATE ROCK TYPE-S",
    "IRON-NICKEL METALLIC CORE","STONY-IRON MIXED PALLSITE",
    "PRIMITIVE CHONDRITE TYPE-C","BASALTIC ACHONDRITE HED",
]
COMET_COMP = [
    "WATER ICE + SILICATE DUST COMA","CO2/METHANE ICE NUCLEUS",
    "HYDROGEN CYANIDE OUTGASSING","ETHYLENE GLYCOL TRACE DETECTED",
]

OBJ_POOL = (
    ["PLANET"] * 2 + ["ASTEROID"] * 5 + ["COMET"] * 2 + ["MOON"] * 3
)

REGIONS = [
    (0,   4,   "INNER SOLAR SYSTEM"),
    (4,   10,  "ASTEROID BELT REGION"),
    (10,  20,  "OUTER SOLAR SYSTEM"),
    (20,  50,  "KUIPER BELT REGION"),
    (50,  100, "HELIOSPHERE BOUNDARY"),
    (100, 999, "INTERSTELLAR SPACE"),
]

# ─── STATE ────────────────────────────────────────────────────────────────────
class ProbeState:
    def __init__(self):
        self.distance_au        = 0.0
        self.sector             = 0
        self.power              = 100.0
        self.fuel               = 100.0
        self.signal             = 100.0
        self.days               = 0
        self.speed_kms          = 17.0
        self.catalogue          = []
        self.encountered        = 0
        self.catalogued         = 0
        self.transmissions      = 0
        self.current_object     = None
        self.scanned            = False
        self.analyzed           = False
        self.probe_name         = "VOYAGER-SIM"
        self.mission            = "DEEP SPACE SURVEY"

    @property
    def region(self):
        for lo, hi, name in REGIONS:
            if lo <= self.distance_au < hi:
                return name
        return "DEEP SPACE"

    def navigate(self):
        self.sector      += 1
        self.distance_au += AU_PER_SECTOR
        self.days        += max(3, int(AU_PER_SECTOR * 149597870 /
                                       (self.speed_kms * 86400)) + random.randint(1, 4))
        self.power        = max(0.0, self.power - random.uniform(0.3, 0.7))
        self.fuel         = max(0.0, self.fuel  - random.uniform(0.4, 1.1))
        self.signal       = max(2.0, 100.0 - self.distance_au * 2.4)

        if random.random() < 0.65:
            self._spawn_object()
            self.encountered += 1
            return True
        else:
            self.current_object = None
            self.scanned        = False
            self.analyzed       = False
            return False

    def _spawn_object(self):
        ot   = random.choice(OBJ_POOL)
        comp = {
            "PLANET":   PLANET_COMP,
            "ASTEROID": ASTEROID_COMP,
            "COMET":    COMET_COMP,
            "MOON":     ASTEROID_COMP,
        }[ot]
        names = {
            "PLANET":   PLANET_NAMES,
            "ASTEROID": ASTEROID_NAMES,
            "COMET":    COMET_NAMES,
            "MOON":     MOON_NAMES,
        }[ot]

        # Determine visual sub-type
        c = random.choice(comp)
        if ot == "PLANET":
            art = "RINGED" if ("GAS GIANT" in c or "AMMONIA" in c or random.random() < 0.25) else "PLANET"
        else:
            art = ot

        self.current_object = {
            "type"       : ot,
            "name"       : random.choice(names),
            "art"        : art,
            "composition": c,
            "distance_au": round(random.uniform(0.001, 0.06), 4),
            "temp_k"     : random.randint(-230 + 273, 500 + 273),
            "mass_earth" : round(random.uniform(0.001, 318.0), 4),
            "diameter_km": round(random.uniform(0.8, 143000.0), 1),
            "magnetic"   : random.random() < 0.4,
            "radiation"  : round(random.uniform(0.1, 920.0), 1),
            "sector"     : self.sector,
            "probe_au"   : round(self.distance_au, 3),
            "bearing"    : random.randint(0, 359),
            "seed"       : random.randint(0, 9999),
        }
        self.scanned  = False
        self.analyzed = False


# ─── APPLICATION ──────────────────────────────────────────────────────────────
class VoyagerApp:
    def __init__(self, root: tk.Tk):
        self.root  = root
        self.state = ProbeState()
        self.stars: list  = []
        self.nebulae: list = []
        self._input_ok   = True
        self._cmd_hist   = []
        self._hist_idx   = 0
        self._build_ui()
        self._gen_background()
        self._redraw_canvas()
        self._boot()

    # ── UI CONSTRUCTION ───────────────────────────────────────────────────────
    def _build_ui(self):
        self.root.title("JPL DEEP SPACE NETWORK  |  PROBE SIMULATOR v1.0  |  1977")
        self.root.configure(bg=BLACK)
        self.root.resizable(False, False)

        mono   = ("Courier", 9)
        mono_b = ("Courier", 9, "bold")
        mono10 = ("Courier", 10)

        # ── TOP HEADER ──
        hdr = tk.Frame(self.root, bg=BLACK, pady=3)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="JPL DEEP SPACE NETWORK  ──  PROBE MISSION SIMULATOR v1.0",
                 fg=GREEN, bg=BLACK, font=("Courier", 11, "bold")).pack()
        tk.Label(hdr,
                 text="JET PROPULSION LABORATORY  │  CALIFORNIA INST. OF TECHNOLOGY  │  1977",
                 fg=DIM, bg=BLACK, font=("Courier", 8)).pack()
        tk.Frame(self.root, bg=GREEN, height=1).pack(fill=tk.X, padx=4)

        # ── MAIN ROW: CANVAS + STATUS PANEL ──
        row = tk.Frame(self.root, bg=BLACK)
        row.pack(fill=tk.X, padx=4, pady=3)

        # Canvas
        self.canvas = tk.Canvas(row, width=CANVAS_W, height=CANVAS_H,
                                bg=BLACK, highlightthickness=1,
                                highlightbackground=DIMMER)
        self.canvas.pack(side=tk.LEFT)

        # Status panel
        sp = tk.Frame(row, bg=BLACK, padx=6, width=PANEL_W)
        sp.pack(side=tk.LEFT, fill=tk.Y)
        sp.pack_propagate(False)

        tk.Label(sp, text="[ PROBE TELEMETRY ]", fg=AMBER,
                 bg=BLACK, font=mono_b).pack(anchor=tk.W, pady=(0, 4))

        self._svars = {}
        rows = [
            ("PROBE",    "probe"),
            ("MISSION",  "mission"),
            ("DAY",      "day"),
            ("DISTANCE", "dist"),
            ("SECTOR",   "sector"),
            ("REGION",   "region"),
            ("SPEED",    "speed"),
            ("",         None),
            ("RTG POWER","power"),
            ("RCS FUEL", "fuel"),
            ("DSN SIGNAL","signal"),
            ("",         None),
            ("DETECTED", "enc"),
            ("CATALOGUED","cat"),
            ("TRANSMIT",  "tx"),
        ]
        for label, key in rows:
            if key is None:
                tk.Frame(sp, bg=DIMMER, height=1).pack(fill=tk.X, pady=2)
                continue
            r = tk.Frame(sp, bg=BLACK)
            r.pack(fill=tk.X, pady=0)
            tk.Label(r, text=f"{label}:", fg=DIM, bg=BLACK,
                     font=mono, width=10, anchor=tk.W).pack(side=tk.LEFT)
            v = tk.StringVar(value="--")
            self._svars[key] = v
            tk.Label(r, textvariable=v, fg=GREEN, bg=BLACK,
                     font=mono, anchor=tk.W).pack(side=tk.LEFT)

        tk.Frame(self.root, bg=DIMMER, height=1).pack(fill=tk.X, padx=4)

        # ── TERMINAL ──
        self.term = scrolledtext.ScrolledText(
            self.root, width=94, height=13,
            bg=DARK, fg=GREEN, font=mono10,
            insertbackground=GREEN, selectbackground=DIMMER,
            relief=tk.FLAT, state=tk.DISABLED, wrap=tk.WORD,
            padx=6, pady=4,
        )
        self.term.pack(padx=4, pady=(3, 0))
        for tag, color in [
            ("hdr",  AMBER), ("ok", BRIGHT), ("warn", ORANGE),
            ("err",  RED),   ("dim", DIM),   ("norm", GREEN),
        ]:
            self.term.tag_config(tag, foreground=color)

        tk.Frame(self.root, bg=DIMMER, height=1).pack(fill=tk.X, padx=4)

        # ── INPUT LINE ──
        inp = tk.Frame(self.root, bg=BLACK, pady=4)
        inp.pack(fill=tk.X, padx=4)
        tk.Label(inp, text="READY >", fg=AMBER, bg=BLACK,
                 font=("Courier", 10, "bold")).pack(side=tk.LEFT)
        self._ivar = tk.StringVar()
        self._entry = tk.Entry(inp, textvariable=self._ivar,
                               bg=BLACK, fg=GREEN,
                               font=("Courier", 10),
                               insertbackground=GREEN, relief=tk.FLAT, width=80)
        self._entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._entry.bind("<Return>",   self._on_enter)
        self._entry.bind("<Up>",       self._hist_up)
        self._entry.bind("<Down>",     self._hist_dn)
        self._entry.focus_set()

        # ── BOTTOM FOOTER ──
        tk.Frame(self.root, bg=DIMMER, height=1).pack(fill=tk.X, padx=4)
        tk.Label(self.root,
                 text="  DSN MADRID  │  DSN GOLDSTONE  │  DSN CANBERRA  │  SIGNAL LOCKED",
                 fg=DIMMER, bg=BLACK, font=("Courier", 7)).pack(anchor=tk.W, padx=4)

    # ── BACKGROUND GENERATION ─────────────────────────────────────────────────
    def _gen_background(self):
        random.seed(42)
        self.stars = [
            (random.randint(0, CANVAS_W),
             random.randint(0, CANVAS_H),
             random.choice([1, 1, 1, 2]),
             random.choice([DIMMER, DIM, "#224422", "#33AA33", GREEN]))
            for _ in range(STAR_COUNT)
        ]
        self.nebulae = [
            (random.randint(50, CANVAS_W - 50),
             random.randint(20, CANVAS_H - 20),
             random.randint(20, 55),
             random.randint(10, 30))
            for _ in range(NEBULA_COUNT)
        ]
        random.seed()

    # ── CANVAS DRAWING ────────────────────────────────────────────────────────
    def _redraw_canvas(self):
        c = self.canvas
        c.delete("all")

        # Nebulae (dim blobs for ambience)
        for nx, ny, rx, ry in self.nebulae:
            c.create_oval(nx - rx, ny - ry, nx + rx, ny + ry,
                          fill=DIMMER, outline="", stipple="gray12")

        # Stars
        for sx, sy, sz, col in self.stars:
            c.create_oval(sx, sy, sx + sz, sy + sz, fill=col, outline="")

        # Trajectory line
        c.create_line(0, CANVAS_H // 2, CANVAS_W, CANVAS_H // 2,
                      fill=DIMMER, dash=(2, 10))

        # Probe
        px, py = 90, CANVAS_H // 2
        # Dish
        c.create_arc(px - 12, py - 18, px + 12, py + 2,
                     start=0, extent=180, style=tk.ARC, outline=GREEN, width=1)
        c.create_line(px, py - 18, px, py - 9, fill=DIM, width=1)
        # Body
        c.create_rectangle(px - 10, py - 4, px + 10, py + 4,
                            fill=DIMMER, outline=GREEN, width=1)
        # Solar panel arms
        c.create_line(px - 10, py, px - 28, py, fill=GREEN, width=1)
        c.create_rectangle(px - 35, py - 6, px - 28, py + 6,
                            fill=DIMMER, outline=DIM, width=1)
        c.create_line(px + 10, py, px + 28, py, fill=GREEN, width=1)
        c.create_rectangle(px + 28, py - 6, px + 35, py + 6,
                            fill=DIMMER, outline=DIM, width=1)
        # RTG boom
        c.create_line(px + 10, py + 4, px + 22, py + 18, fill=DIM, width=1)
        c.create_oval(px + 20, py + 15, px + 26, py + 22,
                      fill=AMBER, outline=DIM)
        # Thruster glow
        c.create_line(px + 10, py, px + 30, py, fill=AMBER, width=1, dash=(1, 3))

        # Current object
        if self.state.current_object:
            self._draw_obj(c)

        # HUD overlays
        dist_txt = f"DIST: {self.state.distance_au:.3f} AU"
        day_txt  = f"DAY:  {self.state.days:04d}"
        c.create_text(8, 8,  anchor=tk.NW, text=dist_txt, fill=DIM, font=("Courier", 8))
        c.create_text(8, 18, anchor=tk.NW, text=day_txt,  fill=DIM, font=("Courier", 8))
        c.create_text(8, 28, anchor=tk.NW,
                      text=f"SEC:  {self.state.sector:04d}", fill=DIM, font=("Courier", 8))

        # Power/fuel bars
        self._draw_bar(c, CANVAS_W - 80, 8,  60, 7,
                       self.state.power / 100, "PWR", GREEN)
        self._draw_bar(c, CANVAS_W - 80, 20, 60, 7,
                       self.state.fuel  / 100, "FUL", AMBER)
        self._draw_bar(c, CANVAS_W - 80, 32, 60, 7,
                       self.state.signal / 100, "SIG", DIM)

    def _draw_bar(self, c, x, y, w, h, frac, label, color):
        c.create_rectangle(x, y, x + w, y + h, fill=BLACK, outline=DIMMER)
        fw = max(1, int(w * frac))
        c.create_rectangle(x, y, x + fw, y + h, fill=color, outline="")
        c.create_text(x - 3, y + h // 2, anchor=tk.E,
                      text=label, fill=DIM, font=("Courier", 7))

    def _draw_obj(self, c):
        obj = self.state.current_object
        art = obj["art"]
        ox, oy = 400, CANVAS_H // 2

        rng = random.Random(obj["seed"])

        if art == "PLANET":
            r = 38
            c.create_oval(ox - r, oy - r, ox + r, oy + r,
                          fill="#001A00", outline=GREEN, width=2)
            for i in range(4):
                yb = oy - r + 12 + i * 16
                c.create_line(ox - r + 4, yb, ox + r - 4, yb,
                               fill=DIMMER, dash=(4, 5))
            c.create_oval(ox - 8, oy - 8, ox + 8, oy + 8,
                          fill=DIMMER, outline=DIM)

        elif art == "RINGED":
            r = 30
            # Rings (behind)
            c.create_oval(ox - r - 24, oy - 7, ox + r + 24, oy + 7,
                          fill="", outline=DIM, width=2)
            c.create_oval(ox - r - 18, oy - 5, ox + r + 18, oy + 5,
                          fill="", outline=GREEN, width=1)
            # Planet body
            c.create_oval(ox - r, oy - r, ox + r, oy + r,
                          fill="#001A00", outline=GREEN, width=2)
            for i in range(3):
                yb = oy - r + 12 + i * 14
                c.create_line(ox - r + 4, yb, ox + r - 4, yb,
                               fill=DIMMER, dash=(3, 4))
            # Rings (front overlay)
            c.create_arc(ox - r - 24, oy - 7, ox + r + 24, oy + 7,
                         start=180, extent=180, style=tk.ARC,
                         outline=DIM, width=2)

        elif art == "ASTEROID":
            pts = []
            n = 8
            for i in range(n):
                angle = (i / n) * 2 * math.pi
                rad   = rng.randint(14, 26)
                pts.append(ox + rad * math.cos(angle))
                pts.append(oy + rad * math.sin(angle))
            c.create_polygon(pts, fill="#001000", outline=GREEN, width=1)
            # Craters
            for _ in range(3):
                cx = ox + rng.randint(-12, 12)
                cy = oy + rng.randint(-12, 12)
                cr = rng.randint(2, 5)
                c.create_oval(cx - cr, cy - cr, cx + cr, cy + cr,
                              fill="", outline=DIMMER)

        elif art == "COMET":
            # Nucleus
            c.create_oval(ox - 9, oy - 9, ox + 9, oy + 9,
                          fill="#001A00", outline=GREEN, width=2)
            # Tail
            for i in range(1, 10):
                tx1 = ox + 9 + i * 10
                ty_off = (9 - i) * 2
                col = DIM if i > 5 else GREEN
                c.create_line(tx1, oy - ty_off, tx1 + 6, oy + ty_off,
                               fill=col, width=1)
            # Coma
            c.create_oval(ox - 14, oy - 14, ox + 14, oy + 14,
                          fill="", outline=DIMMER, dash=(2, 4))

        elif art == "MOON":
            r = 22
            c.create_oval(ox - r, oy - r, ox + r, oy + r,
                          fill="#001000", outline=DIM, width=2)
            for _ in range(4):
                cx = ox + rng.randint(-14, 14)
                cy = oy + rng.randint(-14, 14)
                cr = rng.randint(2, 6)
                c.create_oval(cx - cr, cy - cr, cx + cr, cy + cr,
                              fill="", outline=DIMMER)

        # Status badge
        if not self.state.scanned:
            badge, bc = "[ UNCHARTED OBJECT ]", AMBER
        elif not self.state.analyzed:
            badge, bc = "[ SCANNED — ANALYZE? ]", GREEN
        else:
            badge, bc = "[ DATA ACQUIRED ]", BRIGHT

        c.create_text(ox, oy - 55, text=badge, fill=bc, font=("Courier", 8, "bold"))
        c.create_text(ox, oy + 55,
                      text=f"{obj['name']}  [{obj['type']}]",
                      fill=GREEN, font=("Courier", 8))

        # Range indicator line
        c.create_line(px := 90 + 40, CANVAS_H // 2,
                      ox - (30 if art in ("PLANET","RINGED") else 24), oy,
                      fill=DIMMER, dash=(2, 6))

    # ── STATUS PANEL UPDATE ───────────────────────────────────────────────────
    def _upd_status(self):
        s = self.state
        self._svars["probe"].set(s.probe_name)
        self._svars["mission"].set(s.mission[:12])
        self._svars["day"].set(f"DAY {s.days:04d}")
        self._svars["dist"].set(f"{s.distance_au:.3f} AU")
        self._svars["sector"].set(f"{s.sector:04d}")
        self._svars["region"].set(s.region[:14])
        self._svars["speed"].set(f"{s.speed_kms:.1f} KM/S")
        pwr_col = RED if s.power < 20 else (ORANGE if s.power < 40 else GREEN)
        flt_col = RED if s.fuel  < 15 else (ORANGE if s.fuel  < 30 else GREEN)
        sig_col = RED if s.signal < 15 else (ORANGE if s.signal < 30 else GREEN)
        self._svars["power"].set(f"{s.power:.1f}%")
        self._svars["fuel"].set(f"{s.fuel:.1f}%")
        self._svars["signal"].set(f"{s.signal:.1f}%")
        self._svars["enc"].set(str(s.encountered))
        self._svars["cat"].set(str(s.catalogued))
        self._svars["tx"].set(str(s.transmissions))

    # ── TERMINAL OUTPUT ───────────────────────────────────────────────────────
    def _pr(self, text="", tag="norm"):
        self.term.configure(state=tk.NORMAL)
        self.term.insert(tk.END, text + "\n", tag)
        self.term.configure(state=tk.DISABLED)
        self.term.see(tk.END)

    def _sep(self, char="─", tag="dim"):
        self._pr(char * 76, tag)

    def _clear_term(self):
        self.term.configure(state=tk.NORMAL)
        self.term.delete("1.0", tk.END)
        self.term.configure(state=tk.DISABLED)

    # ── INPUT HANDLING ────────────────────────────────────────────────────────
    def _on_enter(self, _event):
        if not self._input_ok:
            return
        raw = self._ivar.get().strip()
        if not raw:
            return
        cmd = raw.upper()
        self._cmd_hist.append(cmd)
        self._hist_idx = len(self._cmd_hist)
        self._ivar.set("")
        self._pr(f"  > {cmd}", "dim")
        self._dispatch(cmd)

    def _hist_up(self, _e):
        if self._cmd_hist and self._hist_idx > 0:
            self._hist_idx -= 1
            self._ivar.set(self._cmd_hist[self._hist_idx])

    def _hist_dn(self, _e):
        if self._hist_idx < len(self._cmd_hist) - 1:
            self._hist_idx += 1
            self._ivar.set(self._cmd_hist[self._hist_idx])
        else:
            self._hist_idx = len(self._cmd_hist)
            self._ivar.set("")

    # ── COMMAND DISPATCH ─────────────────────────────────────────────────────
    def _dispatch(self, cmd):
        table = {
            "HELP": self._c_help,    "H": self._c_help,
            "STATUS": self._c_status,"ST": self._c_status,
            "NAVIGATE": self._c_nav, "NAV": self._c_nav, "N": self._c_nav,
            "SCAN": self._c_scan,    "SC": self._c_scan,
            "ANALYZE": self._c_analyze,"AN": self._c_analyze,
            "CATALOGUE": self._c_catalogue,"CAT": self._c_catalogue,
            "LOG": self._c_log,      "L": self._c_log,
            "TRANSMIT": self._c_transmit,"TX": self._c_transmit,
            "CLEAR": self._clear_term,"CLS": self._clear_term,
        }
        fn = table.get(cmd.split()[0])
        if fn:
            fn()
        else:
            self._pr(f"  ** COMMAND NOT RECOGNIZED: {cmd}", "err")
            self._pr("  TYPE 'HELP' FOR AVAILABLE COMMANDS.", "dim")

    # ── COMMANDS ──────────────────────────────────────────────────────────────
    def _c_help(self):
        self._sep()
        self._pr("  AVAILABLE COMMANDS", "hdr")
        self._sep()
        entries = [
            ("NAVIGATE   NAV  N", "ADVANCE PROBE TO NEXT SECTOR"),
            ("SCAN       SC",     "WIDE-FIELD SENSOR SWEEP OF OBJECT"),
            ("ANALYZE    AN",     "DEEP SPECTRAL/COMPOSITION ANALYSIS"),
            ("CATALOGUE  CAT",    "LOG ANALYZED OBJECT TO MISSION RECORD"),
            ("STATUS     ST",     "FULL PROBE TELEMETRY REPORT"),
            ("LOG        L",      "DISPLAY MISSION OBJECT CATALOGUE"),
            ("TRANSMIT   TX",     "SEND DATA BURST TO EARTH / JPL"),
            ("CLEAR      CLS",    "CLEAR TERMINAL DISPLAY"),
            ("HELP       H",      "THIS HELP SCREEN"),
        ]
        for cmd, desc in entries:
            self._pr(f"  {cmd:<22}  {desc}")
        self._sep()
        self._pr("  TIP: USE UP/DOWN ARROW KEYS TO RECALL PREVIOUS COMMANDS.", "dim")
        self._sep()

    def _c_status(self):
        s = self.state
        self._sep()
        self._pr("  PROBE TELEMETRY — FULL REPORT", "hdr")
        self._sep()
        lines = [
            ("PROBE DESIGNATION ", s.probe_name),
            ("MISSION NAME      ", s.mission),
            ("ELAPSED MISSION   ", f"DAY {s.days}"),
            ("DISTANCE FROM SOL ", f"{s.distance_au:.4f} AU"),
            ("CURRENT SECTOR    ", f"{s.sector:04d}"),
            ("OPERATIONAL REGION", s.region),
            ("CRUISE VELOCITY   ", f"{s.speed_kms:.2f} KM/S"),
            ("RTG POWER OUTPUT  ", f"{s.power:.2f} %"),
            ("RCS FUEL RESERVE  ", f"{s.fuel:.2f} %"),
            ("DSN SIGNAL LEVEL  ", f"{s.signal:.2f} %"),
            ("OBJECTS DETECTED  ", str(s.encountered)),
            ("OBJECTS CATALOGUED", str(s.catalogued)),
            ("DATA TRANSMISSIONS", str(s.transmissions)),
        ]
        for k, v in lines:
            self._pr(f"  {k}: {v}")
        warns = []
        if s.power  < 20: warns.append("LOW RTG POWER — SYSTEMS AT RISK")
        if s.fuel   < 15: warns.append("LOW RCS FUEL — MANEUVERS LIMITED")
        if s.signal < 15: warns.append("WEAK DSN SIGNAL — DATA LOSS POSSIBLE")
        if warns:
            self._pr("", "norm")
            for w in warns:
                self._pr(f"  *** WARNING: {w} ***", "warn")
        self._sep()

    def _c_nav(self):
        s = self.state
        if s.fuel < 0.5:
            self._pr("  ** NAVIGATION ABORT: INSUFFICIENT RCS FUEL **", "err")
            return
        if s.power < 1.5:
            self._pr("  ** NAVIGATION ABORT: CRITICAL POWER FAILURE **", "err")
            return

        self._pr(f"  INITIATING NAVIGATION BURN — SECTOR {s.sector:04d}…", "dim")
        hit = s.navigate()
        self._upd_status()
        self._redraw_canvas()

        self._pr(f"  NAVIGATION COMPLETE.  SECTOR {s.sector:04d}  |  {s.distance_au:.3f} AU", "ok")
        self._pr(f"  OPERATIONAL REGION: {s.region}", "dim")

        if hit:
            obj = s.current_object
            self._sep()
            self._pr("  *** SENSOR ALERT — OBJECT IN RANGE ***", "warn")
            self._pr(f"  OBJECT TYPE  : {obj['type']}", "norm")
            self._pr(f"  BEARING      : {obj['bearing']:03d}°", "norm")
            self._pr(f"  RANGE        : {obj['distance_au']:.4f} AU", "norm")
            self._pr("  ISSUE 'SCAN' COMMAND TO BEGIN SENSOR SWEEP.", "dim")
        else:
            self._pr("  SENSOR SWEEP NEGATIVE — NO OBJECTS IN RANGE.", "dim")
            self._pr("  CONTINUE NAVIGATING TO NEXT SECTOR.", "dim")

    def _c_scan(self):
        s = self.state
        if not s.current_object:
            self._pr("  NO OBJECT IN SENSOR RANGE.", "dim")
            self._pr("  USE 'NAVIGATE' TO ADVANCE TO NEXT SECTOR.", "dim")
            return
        if s.scanned:
            self._pr("  SCAN ALREADY COMPLETE FOR THIS OBJECT.", "dim")
            self._pr("  PROCEED WITH 'ANALYZE' FOR SPECTRAL ANALYSIS.", "dim")
            return

        obj = s.current_object
        self._sep()
        self._pr("  INITIATING SENSOR SWEEP…", "dim")
        self._pr(f"  DESIGNATION  : {obj['name']}", "hdr")
        self._pr(f"  OBJECT CLASS : {obj['type']}")
        self._pr(f"  RANGE        : {obj['distance_au']:.4f} AU")
        self._pr(f"  BEARING      : {obj['bearing']:03d}°")
        self._pr(f"  EST. DIAMETER: {obj['diameter_km']:.1f} KM")
        self._pr(f"  SURFACE TEMP : {obj['temp_k']} K")
        self._pr(f"  MAGNETOMETER : {'FIELD DETECTED' if obj['magnetic'] else 'NO FIELD'}")
        self._pr(f"  RADIATION    : {obj['radiation']:.1f} RADS/HR")
        self._pr("  SWEEP COMPLETE. USE 'ANALYZE' FOR FULL ANALYSIS.", "ok")

        s.scanned = True
        self._redraw_canvas()

    def _c_analyze(self):
        s = self.state
        if not s.current_object:
            self._pr("  NO OBJECT IN SENSOR RANGE.", "dim")
            return
        if not s.scanned:
            self._pr("  ** ERROR: SCAN MUST PRECEDE ANALYSIS **", "err")
            self._pr("  ISSUE 'SCAN' COMMAND FIRST.", "dim")
            return
        if s.analyzed:
            self._pr("  ANALYSIS COMPLETE — DATA ON FILE.", "dim")
            self._pr("  USE 'CATALOGUE' TO LOG THIS OBJECT.", "dim")
            return

        obj = s.current_object
        self._sep()
        self._pr("  DEEP SPECTRAL ANALYSIS IN PROGRESS…", "dim")
        self._pr(f"  OBJECT DESIGNATION : {obj['name']}", "hdr")
        self._pr(f"  CLASSIFICATION     : {obj['type']}")
        self._pr(f"  COMPOSITION        : {obj['composition']}")
        self._pr(f"  MASS               : {obj['mass_earth']:.4f} EARTH MASSES")
        self._pr(f"  DIAMETER           : {obj['diameter_km']:.1f} KM")
        self._pr(f"  SURFACE TEMP       : {obj['temp_k']} K  /  {obj['temp_k']-273:.0f} °C")
        self._pr(f"  MAGNETIC FIELD     : {'YES — FIELD CONFIRMED' if obj['magnetic'] else 'NO'}")
        self._pr(f"  RADIATION INDEX    : {obj['radiation']:.1f} RADS/HR")
        self._pr(f"  SECTOR LOGGED      : {obj['sector']:04d}")
        self._pr(f"  PROBE POSITION     : {obj['probe_au']:.3f} AU")

        notes = []
        if obj["temp_k"] > 673:
            notes.append("EXTREME HEAT — POSSIBLE ACTIVE VOLCANISM")
        if obj["temp_k"] < 50:
            notes.append("CRYOGENIC SURFACE — VOLATILE ICE COMPOUNDS PROBABLE")
        if obj["magnetic"]:
            notes.append("MAGNETIC FIELD IMPLIES LIQUID METALLIC INTERIOR")
        if obj["radiation"] > 600:
            notes.append("INTENSE RADIATION BELT — INSTRUMENTATION RISK")
        if obj["mass_earth"] > 100:
            notes.append("HIGH MASS — SIGNIFICANT GRAVITATIONAL INFLUENCE")
        if "WATER" in obj["composition"]:
            notes.append("WATER SIGNATURE — FLAG FOR MISSION SCIENCE TEAM")

        if notes:
            self._pr("  SCIENCE NOTES:", "hdr")
            for n in notes:
                self._pr(f"    + {n}")

        self._pr("  ANALYSIS COMPLETE. USE 'CATALOGUE' TO LOG.", "ok")
        s.analyzed = True
        s.power = max(0.0, s.power - 1.5)
        self._redraw_canvas()
        self._upd_status()

    def _c_catalogue(self):
        s = self.state
        if not s.current_object:
            self._pr("  NO OBJECT AVAILABLE FOR CATALOGUING.", "dim")
            return
        if not s.analyzed:
            self._pr("  ** INSUFFICIENT DATA: SCAN AND ANALYZE FIRST **", "err")
            return
        obj = s.current_object
        for e in s.catalogue:
            if e["name"] == obj["name"]:
                self._pr(f"  OBJECT {obj['name']} ALREADY IN CATALOGUE.", "dim")
                return

        s.catalogue.append(obj.copy())
        s.catalogued += 1
        cid = f"DSO-{s.catalogued:04d}"
        self._sep()
        self._pr("  OBJECT LOGGED TO MISSION CATALOGUE", "ok")
        self._pr(f"  CATALOGUE ID : {cid}")
        self._pr(f"  DESIGNATION  : {obj['name']}")
        self._pr(f"  TOTAL LOGGED : {s.catalogued}")
        self._sep()
        self._upd_status()

    def _c_log(self):
        s = self.state
        if not s.catalogue:
            self._pr("  MISSION CATALOGUE IS EMPTY.", "dim")
            self._pr("  NAVIGATE, SCAN, ANALYZE, AND CATALOGUE OBJECTS.", "dim")
            return
        self._sep()
        self._pr("  MISSION CATALOGUE — DEEP SPACE OBJECTS SURVEY", "hdr")
        self._sep()
        self._pr(f"  {'ID':<10} {'NAME':<20} {'TYPE':<10} {'AU':>7}  {'TEMP(K)':>7}  {'DIAM(KM)'}", "hdr")
        self._pr("  " + "─" * 70, "dim")
        for i, obj in enumerate(s.catalogue):
            cid = f"DSO-{i+1:04d}"
            self._pr(
                f"  {cid:<10} {obj['name']:<20} {obj['type']:<10} "
                f"{obj['probe_au']:>7.3f}  {obj['temp_k']:>7}  {obj['diameter_km']:>10.1f}"
            )
        self._sep()
        self._pr(f"  TOTAL OBJECTS IN CATALOGUE: {s.catalogued}", "ok")
        self._sep()

    def _c_transmit(self):
        s = self.state
        if not s.catalogue:
            self._pr("  NO DATA TO TRANSMIT — CATALOGUE IS EMPTY.", "dim")
            return
        delay = int(s.distance_au * LIGHT_MIN_PER_AU)
        self._sep()
        self._pr("  INITIATING DSN DATA BURST TRANSMISSION…", "dim")
        self._pr(f"  DSN SIGNAL STRENGTH : {s.signal:.1f}%")
        self._pr(f"  ONE-WAY LIGHT DELAY : {delay} MIN  ({delay//60}H {delay%60}M)")
        self._pr(f"  CATALOGUE ENTRIES   : {len(s.catalogue)}")
        if s.signal < 10:
            self._pr("  ** WARNING: SIGNAL MARGINAL — PARTIAL TRANSMISSION **", "warn")
        self._pr("  BURST TRANSMITTED SUCCESSFULLY.", "ok")
        self._pr(f"  JPL WILL RECEIVE DATA IN APPROXIMATELY {delay} MINUTES.", "dim")
        s.transmissions += 1
        s.power = max(0.0, s.power - 2.0)
        self._upd_status()
        self._sep()

    # ── BOOT SEQUENCE ─────────────────────────────────────────────────────────
    def _boot(self):
        self._input_ok = False
        lines = [
            ("╔══════════════════════════════════════════════════════════════════╗", "dim"),
            ("║   JPL DEEP SPACE NETWORK — PROBE MISSION SIMULATOR v1.0        ║", "hdr"),
            ("║   JET PROPULSION LABORATORY  ·  CALTECH  ·  1977               ║", "dim"),
            ("╚══════════════════════════════════════════════════════════════════╝", "dim"),
            ("", "norm"),
            ("  POWERING ON PROBE SUBSYSTEMS…", "dim"),
            ("", "norm"),
            ("  PLASMA SCIENCE DETECTOR  . . . . . . . . . . OK", "norm"),
            ("  LOW ENERGY CHARGED PARTICLE SYS . . . . . . OK", "norm"),
            ("  MAGNETOMETER (MAG)  . . . . . . . . . . . . OK", "norm"),
            ("  COSMIC RAY SCIENCE SUBSYSTEM . . . . . . . . OK", "norm"),
            ("  ULTRAVIOLET SPECTROMETER  . . . . . . . . . OK", "norm"),
            ("  PHOTOPOLARIMETER RADIOMETER  . . . . . . . . OK", "norm"),
            ("  INFRARED INTERFEROMETER SPECTROMETER  . . . OK", "norm"),
            ("  RADIO SCIENCE SYSTEM . . . . . . . . . . . . OK", "norm"),
            ("  RTG THERMOELECTRIC POWER UNITS . . . . . . . OK", "norm"),
            ("  ATTITUDE CONTROL — RCS THRUSTERS  . . . . . OK", "norm"),
            ("  DSN UPLINK/DOWNLINK — GOLDSTONE LOCKED  . . OK", "norm"),
            ("", "norm"),
            ("  ALL SYSTEMS NOMINAL.  PROBE IS FULLY OPERATIONAL.", "ok"),
            ("", "norm"),
            ("  MISSION OBJECTIVE:", "hdr"),
            ("  NAVIGATE DEEP SPACE AND CATALOGUE ALL SIGNIFICANT OBJECTS.", "norm"),
            ("  TRANSMIT FINDINGS TO JPL VIA THE DEEP SPACE NETWORK.", "norm"),
            ("", "norm"),
            ("  TYPE  'HELP'      FOR A LIST OF COMMANDS.", "warn"),
            ("  TYPE  'NAVIGATE'  (OR JUST 'N') TO BEGIN MISSION.", "warn"),
            ("  USE ARROW KEYS TO SCROLL COMMAND HISTORY.", "dim"),
            ("", "norm"),
        ]

        def step(i=0):
            if i >= len(lines):
                self._input_ok = True
                self._upd_status()
                return
            txt, tag = lines[i]
            self._pr(txt, tag)
            self.root.after(55, lambda: step(i + 1))

        self.root.after(300, step)


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────
def main():
    root = tk.Tk()
    app  = VoyagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
