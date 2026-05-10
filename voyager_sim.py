#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════╗
║   JPL DEEP SPACE NETWORK — PROBE MISSION SIMULATOR v2.0          ║
║   JET PROPULSION LABORATORY / CALIFORNIA INST. OF TECHNOLOGY     ║
║   © 1977  —  MISSION CONTROL SOFTWARE DIVISION                   ║
╠═══════════════════════════════════════════════════════════════════╣
║   NEW IN v2.0:                                                    ║
║    • SLINGSHOT gravity-assist maneuver                            ║
║    • Physics-based procedural object generation                   ║
║    • NASA Exoplanet Archive live database (auto-fetched)          ║
║    • QUIT command                                                 ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import scrolledtext
import random, math, threading, json
import urllib.request

# ─── PALETTE ──────────────────────────────────────────────────────────────────
BLACK  = "#000000";  DARK   = "#080808"
GREEN  = "#33FF33";  DIM    = "#1A6B1A";  DIMMER = "#0D3A0D"
AMBER  = "#FFB000";  BRIGHT = "#99FF99"
RED    = "#FF3333";  ORANGE = "#FF8800"

# ─── LAYOUT ───────────────────────────────────────────────────────────────────
CANVAS_W, CANVAS_H = 560, 290
PANEL_W             = 185
AU_PER_SECTOR       = 0.45
LIGHT_MIN_PER_AU    = 8.317
STAR_COUNT          = 220
NEBULA_COUNT        = 6

# ─── NASA EXOPLANET ARCHIVE TAP ───────────────────────────────────────────────
EXOPLANET_API = (
    "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
    "?query=SELECT+pl_name,pl_masse,pl_rade,pl_eqt,pl_orbsmax"
    "+FROM+pscomppars"
    "+WHERE+pl_masse+IS+NOT+NULL"
    "+AND+pl_eqt+IS+NOT+NULL"
    "+AND+pl_rade+IS+NOT+NULL"
    "+AND+pl_orbsmax+IS+NOT+NULL"
    "&format=json"
)

# Curated embedded fallback — real measured exoplanet values
# (name, mass_earth, radius_earth, temp_k, orbital_au)
EXOPLANET_FALLBACK = [
    ("51 PEGASI B",         149.9, 13.0, 1284, 0.052),
    ("HD 209458 B",         219.9, 15.6, 1459, 0.047),
    ("GJ 1214 B",             6.5,  2.7,  596, 0.014),
    ("KEPLER-22B",           13.8,  2.4,  295, 0.849),
    ("HD 40307 G",            7.1,  2.5,  226, 0.600),
    ("TRAPPIST-1E",           0.8,  0.9,  251, 0.028),
    ("TRAPPIST-1F",           1.0,  1.0,  219, 0.037),
    ("TRAPPIST-1D",           0.4,  0.8,  288, 0.021),
    ("PROXIMA CEN B",         1.2,  1.1,  234, 0.048),
    ("K2-18 B",               8.6,  2.7,  265, 0.143),
    ("55 CANCRI E",           8.0,  2.0, 1958, 0.015),
    ("KEPLER-452B",           5.0,  1.6,  265, 1.046),
    ("LHS 1140 B",            6.6,  1.4,  230, 0.088),
    ("WOLF 1061 C",           4.3,  1.7,  227, 0.089),
    ("YZ CETI D",             1.1,  1.1,  270, 0.028),
    ("ROSS 128 B",            1.4,  1.2,  294, 0.049),
    ("TAU CETI E",            3.9,  1.7,  256, 0.538),
    ("GLIESE 667C C",         4.5,  1.8,  277, 0.123),
    ("GLIESE 667C E",         2.7,  1.5,  212, 0.213),
    ("HD 40307 C",            6.7,  2.1,  355, 0.080),
    ("KEPLER-62F",            2.8,  1.4,  208, 0.718),
    ("KEPLER-62E",            4.5,  1.6,  270, 0.427),
    ("KEPLER-186F",           1.4,  1.1,  188, 0.432),
    ("HD 85512 B",            3.6,  1.7,  298, 0.260),
    ("KEPLER-442B",           2.3,  1.3,  233, 0.409),
    ("WASP-121B",          1136.0, 19.5, 2400, 0.025),
    ("HAT-P-7B",             598.0, 15.9, 2214, 0.038),
    ("COROT-7B",               6.0,  1.6, 1800, 0.017),
    ("HD 189733 B",          358.5, 13.6, 1191, 0.031),
    ("WASP-17B",             330.0, 24.0, 1771, 0.052),
    ("KEPLER-7B",            468.0, 18.1, 1631, 0.062),
    ("KEPLER-10B",             4.6,  1.5, 2169, 0.017),
    ("KEPLER-10C",            17.2,  2.4,  584, 0.241),
    ("KEPLER-16B",           105.8,  8.5,  188, 0.705),
    ("KEPLER-438B",            1.5,  1.1,  276, 0.166),
    ("KEPLER-442B",            2.1,  1.3,  275, 0.328),
    ("GLIESE 436 B",          21.4,  4.2,  649, 0.029),
    ("KEPLER-452B",            5.0,  1.6,  265, 1.046),
    ("KAPTEYN B",              4.8,  1.9,  209, 0.168),
    ("KAPTEYN C",              7.0,  2.2,  121, 0.311),
    ("TAU CETI F",             3.9,  1.7,  200, 1.350),
    ("LUYTEN B",               2.9,  1.5,  258, 0.091),
    ("KEPLER-283C",            4.8,  1.8,  248, 0.341),
    ("82 G. ERIDANI D",        4.8,  1.9,  224, 0.535),
    ("KEPLER-69C",             1.7,  1.7,  299, 0.640),
    ("GJ 667C F",              2.7,  1.5,  215, 0.156),
    ("HD 20794 D",             4.8,  1.9,  212, 0.509),
    ("KEPLER-705B",            4.1,  1.9,  253, 0.371),
    ("KEPLER-296E",            3.6,  1.8,  290, 0.255),
    ("55 CANCRI F",           144.0,  8.0,  141, 5.770),
]

# ─── REGIONS ──────────────────────────────────────────────────────────────────
REGIONS = [
    (0,   2,   "INNER SOLAR SYSTEM"),
    (2,   5,   "ASTEROID BELT REGION"),
    (5,   10,  "OUTER SOLAR SYSTEM"),
    (10,  20,  "GAS GIANT REGION"),
    (20,  50,  "KUIPER BELT REGION"),
    (50,  100, "HELIOSPHERE BOUNDARY"),
    (100, 999, "INTERSTELLAR SPACE"),
]

# ─── STATIC NAME POOLS ────────────────────────────────────────────────────────
ASTEROID_NAMES = [
    "1977-UX1","1977-BK3","1978-AA","1979-BC7","CERES-DELTA",
    "PALLAS-III","VESTA-BETA","HYGIEA-2","DAVIDA-C","INTERAMNIA-9",
    "CAMILLA-B","PSYCHE-7","EUPHROSYNE-A","SYLVIA-6","HERCULINA-3",
    "BAMBERGA-2","THISBE-A","WINCHESTER-4","CYBELE-3","AUSONIA-5",
]
COMET_NAMES = [
    "KOHOUTEK-2","HALLEY-BETA","ENCKE-IV","BORRELLY-2","WILD-5",
    "TEMPEL-III","SHOEMAKER-A","IKEYA-SEKI-2","WEST-B","BRADFIELD-3",
    "CHURYUMOV-4","GIACOBINI-C","SCHWASSMANN-2","TUTTLE-A","CROMMELIN-3",
]
MOON_NAMES = [
    "IO-ALPHA","EUROPA-BETA","GANYMEDE-C","CALLISTO-D","TITAN-II",
    "ENCELADUS-A","TRITON-B","CHARON-II","OBERON-A","TITANIA-C",
    "MIRANDA-B","ARIEL-D","UMBRIEL-A","DIONE-C","RHEA-II",
    "HYPERION-B","IAPETUS-C","PHOEBE-A","MIMAS-D","TETHYS-B",
]
KBO_NAMES = [
    "MAKEMAKE-B","HAUMEA-C","ERIS-BETA","QUAOAR-2","SEDNA-A",
    "ORCUS-B","VARUNA-C","IXION-D","SALACIA-A","VARDA-B",
    "2003-EL61-A","1997-CQ29","2002-TX300","2004-GV9","1996-TL66",
]


# ═══════════════════════════════════════════════════════════════════════════════
#  PHYSICS-BASED PROCEDURAL GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════
class PhysicsGen:
    """
    Generates physically plausible objects using basic planetary science:
      • Equilibrium temperature: T ∝ d^(-0.5) (Stefan–Boltzmann)
      • Snow line at ~4 AU: composition transitions from rocky to icy
      • Type probabilities vary by heliocentric distance region
      • Mass–radius relations for each body class
    """
    EARTH_R_KM = 12742.0

    # (au_lo, au_hi, [ROCKY_PLT, GAS_GNT, ICE_GNT, ASTEROID, COMET, MOON, KBO])
    REGION_W = [
        (0,    2,   [20, 2,  0, 60, 5,  13, 0 ]),
        (2,    4,   [10, 5,  2, 65, 8,  10, 0 ]),
        (4,    10,  [5,  30, 10, 35, 10, 10, 0 ]),
        (10,   30,  [2,  20, 25, 20, 20, 13, 0 ]),
        (30,   100, [1,  5,  10, 15, 25,  5, 39]),
        (100,  9999,[2,  5,   5, 10, 30,  3, 45]),
    ]
    LABELS = ["ROCKY PLANET","GAS GIANT","ICE GIANT",
              "ASTEROID","COMET","MOON","TRANS-NEPTUNIAN OBJECT"]
    ART    = ["PLANET","RINGED","RINGED",
              "ASTEROID","COMET","MOON","ASTEROID"]

    @classmethod
    def temp(cls, au):
        return max(6, int(278 / math.sqrt(max(0.01, au))))

    @classmethod
    def _weights(cls, au):
        for lo, hi, w in cls.REGION_W:
            if lo <= au < hi:
                return w
        return cls.REGION_W[-1][2]

    @classmethod
    def _type_idx(cls, au):
        w    = cls._weights(au)
        pool = [i for i, wt in enumerate(w) for _ in range(wt)]
        return random.choice(pool)

    @classmethod
    def generate(cls, au, sector):
        idx    = cls._type_idx(au)
        otype  = cls.LABELS[idx]
        art    = cls.ART[idx]
        base_t = cls.temp(au)
        rng    = random.Random()

        if idx == 0:   # Rocky planet
            mass   = round(10 ** rng.uniform(-1.5, 1.0), 4)
            rad_e  = round(mass ** 0.27, 3)
            diam   = round(rad_e * cls.EARTH_R_KM, 1)
            temp   = base_t + rng.randint(-40, 60)
            comp   = cls._rocky(au, temp)
            mag    = rng.random() < 0.45

        elif idx == 1: # Gas giant
            mass   = round(10 ** rng.uniform(1.7, 3.5), 2)
            rad_e  = round(min(15.0, mass ** 0.15), 2)
            diam   = round(rad_e * cls.EARTH_R_KM, 1)
            temp   = base_t + rng.randint(-20, 80)
            comp   = rng.choice([
                "HYDROGEN/HELIUM ENVELOPE — GAS GIANT",
                "H2/He — AMMONIA CLOUD BANDS VISIBLE",
                "H2/He/CH4 — PHOTOCHEMICAL HAZE LAYERS",
            ])
            art    = "RINGED" if rng.random() < 0.55 else "PLANET"
            mag    = rng.random() < 0.75

        elif idx == 2: # Ice giant
            mass   = round(10 ** rng.uniform(0.8, 2.1), 2)
            rad_e  = round(mass ** 0.21, 2)
            diam   = round(rad_e * cls.EARTH_R_KM, 1)
            temp   = base_t + rng.randint(-15, 30)
            comp   = rng.choice([
                "WATER/AMMONIA/METHANE ICE MANTLE",
                "ICE GIANT — SUPERIONIC WATER CORE",
                "CH4/H2O ICE — DEEP CONVECTIVE OCEAN",
            ])
            mag    = rng.random() < 0.60

        elif idx == 3: # Asteroid
            mass   = round(10 ** rng.uniform(-12, -2), 10)
            diam   = round(10 ** rng.uniform(-0.3, 3.0), 1)
            temp   = base_t + rng.randint(-30, 30)
            comp   = rng.choice([
                "CARBONACEOUS CHONDRITE (TYPE-C)",
                "SILICATE ROCK (TYPE-S)",
                "IRON-NICKEL METALLIC (TYPE-M)",
                "STONY-IRON PALLASITE",
                "BASALTIC ACHONDRITE (HED)",
            ])
            mag    = rng.random() < 0.10
            name   = rng.choice(ASTEROID_NAMES) + f"-{rng.randint(10,99)}"
            return cls._pack(otype, art, name, mass, diam,
                             temp + 273, comp, mag, rng, au, sector)

        elif idx == 4: # Comet
            mass   = round(10 ** rng.uniform(-16, -9), 14)
            diam   = round(10 ** rng.uniform(-1.0, 1.8), 2)
            temp   = base_t + rng.randint(-10, 10)
            comp   = rng.choice([
                "WATER ICE + SILICATE DUST COMA",
                "CO2/METHANE/AMMONIA ICE NUCLEUS",
                "HYDROGEN CYANIDE OUTGASSING",
                "WATER ICE + REFRACTORY ORGANICS",
            ])
            mag    = False
            name   = rng.choice(COMET_NAMES) + f"-{rng.randint(10,99)}"
            return cls._pack(otype, art, name, mass, diam,
                             temp + 273, comp, mag, rng, au, sector)

        elif idx == 5: # Moon
            mass   = round(10 ** rng.uniform(-5, -0.5), 6)
            rad_e  = round(mass ** 0.30, 4)
            diam   = round(rad_e * cls.EARTH_R_KM, 1)
            temp   = base_t + rng.randint(-50, 20)
            comp   = cls._rocky(au, temp) if au < 5 else rng.choice([
                "WATER/AMMONIA ICE SURFACE",
                "SILICATE ROCK + ICE SHELL",
                "SULFUR DIOXIDE FROST",
            ])
            mag    = rng.random() < 0.20
            name   = rng.choice(MOON_NAMES) + f"-{rng.randint(10,99)}"
            return cls._pack(otype, art, name, mass, diam,
                             temp + 273, comp, mag, rng, au, sector)

        else:          # KBO
            mass   = round(10 ** rng.uniform(-7, -2), 8)
            diam   = round(10 ** rng.uniform(1.5, 3.4), 1)
            temp   = base_t + rng.randint(-5, 10)
            comp   = rng.choice([
                "METHANE/NITROGEN ICE SURFACE",
                "WATER ICE + THOLIN ORGANICS",
                "CO2 ICE + SILICATE ROCK",
                "AMMONIA HYDRATE ICE",
            ])
            mag    = False
            name   = rng.choice(KBO_NAMES) + f"-{rng.randint(10,99)}"
            return cls._pack(otype, art, name, mass, diam,
                             temp + 273, comp, mag, rng, au, sector)

        # Planet types
        name = cls._planet_name(rng)
        return cls._pack(otype, art, name, mass, diam,
                         temp + 273, comp, mag, rng, au, sector)

    @classmethod
    def _rocky(cls, au, temp):
        if temp > 1200: return "SILICATE MELT — ACTIVE LAVA OCEAN"
        if temp > 700:  return "SILICATE ROCK — VOLCANIC SURFACE"
        if 200 < temp < 380 and au < 2: return "SILICATE ROCK — POSSIBLE LIQUID WATER"
        if temp < 200:  return "SILICATE + WATER/CO2 ICE"
        return random.choice([
            "ROCKY SILICATE — THIN ATMOSPHERE",
            "IRON-RICH SILICATE MANTLE",
            "CARBONACEOUS SILICATE SURFACE",
        ])

    @classmethod
    def _planet_name(cls, rng):
        pfx = ["KEPLER","HD","GL","GJ","WOLF","ROSS","BARNARD",
               "LUYTEN","LACAILLE","LALANDE","GROOMBRIDGE","TOI"]
        suf = rng.choice(list("BCDEFG"))
        return f"{rng.choice(pfx)}-{rng.randint(1,9999)}{suf}"

    @classmethod
    def _pack(cls, otype, art, name, mass, diam, temp_k,
              comp, mag, rng, probe_au, sector):
        return {
            "type"       : otype,
            "art"        : art,
            "name"       : name,
            "source"     : "PROCEDURAL",
            "composition": comp,
            "distance_au": round(rng.uniform(0.001, 0.06), 4),
            "temp_k"     : int(temp_k),
            "mass_earth" : mass,
            "diameter_km": diam,
            "magnetic"   : mag,
            "radiation"  : round(10 ** rng.uniform(-1.0, 2.9), 1),
            "bearing"    : rng.randint(0, 359),
            "sector"     : sector,
            "probe_au"   : round(probe_au, 3),
            "seed"       : rng.randint(0, 9999),
        }


# ═══════════════════════════════════════════════════════════════════════════════
#  EXOPLANET DATABASE
# ═══════════════════════════════════════════════════════════════════════════════
class ExoplanetDB:
    """
    Loads real exoplanet data from the NASA Exoplanet Archive TAP service in
    a background thread. Falls back to the embedded curated list instantly.
    Once the live fetch completes, the pool is silently upgraded.
    """
    EARTH_R_KM = 12742.0

    def __init__(self):
        self.planets : list = []
        self.status  : str  = "LOADING…"
        self.count   : int  = 0
        self._load_fallback()
        threading.Thread(target=self._fetch, daemon=True).start()

    def _load_fallback(self):
        for row in EXOPLANET_FALLBACK:
            name, mass_e, rad_e, temp_k, orb_au = row
            self.planets.append(self._make(
                name, mass_e, rad_e, temp_k, orb_au, "EMBEDDED-CATALOGUE"
            ))
        self.count  = len(self.planets)
        self.status = f"EMBEDDED ({self.count})"

    def _fetch(self):
        try:
            req = urllib.request.Request(
                EXOPLANET_API,
                headers={"User-Agent": "VoyagerSim/2.0 JPL-Educational"},
            )
            with urllib.request.urlopen(req, timeout=14) as r:
                raw = json.loads(r.read().decode())
        except Exception:
            self.status = "OFFLINE — EMBEDDED ACTIVE"
            return

        fetched = []
        for row in raw:
            try:
                fetched.append(self._make(
                    str(row["pl_name"]).upper().strip(),
                    float(row["pl_masse"]),
                    float(row["pl_rade"]),
                    float(row["pl_eqt"]),
                    float(row["pl_orbsmax"]),
                    "NASA-EXOPLANET-ARCHIVE",
                ))
            except Exception:
                continue

        if fetched:
            random.shuffle(fetched)
            self.planets = fetched
            self.count   = len(fetched)
            self.status  = f"NASA ({self.count})"
        else:
            self.status = "PARSE ERR — EMBEDDED"

    def _make(self, name, mass_e, rad_e, temp_k, orb_au, source):
        diam_km = round(rad_e * self.EARTH_R_KM, 1)
        return {
            "type"       : self._type(mass_e, rad_e),
            "art"        : self._art(mass_e),
            "name"       : name,
            "source"     : source,
            "composition": self._comp(mass_e, temp_k),
            "distance_au": round(random.uniform(0.001, 0.06), 4),
            "temp_k"     : int(temp_k),
            "mass_earth" : round(mass_e, 4),
            "diameter_km": diam_km,
            "magnetic"   : mass_e > 50 or random.random() < 0.35,
            "radiation"  : round(10 ** random.uniform(-1, 2.8), 1),
            "bearing"    : random.randint(0, 359),
            "sector"     : 0,
            "probe_au"   : 0.0,
            "seed"       : random.randint(0, 9999),
            "real_au"    : orb_au,
        }

    @staticmethod
    def _type(m, r):
        if m > 300: return "GAS GIANT"
        if m > 10:  return "ICE GIANT"
        if r > 2.5: return "SUB-NEPTUNE"
        return "ROCKY PLANET"

    @staticmethod
    def _art(m):
        if m > 300 and random.random() < 0.55: return "RINGED"
        return "PLANET"

    @staticmethod
    def _comp(m, t):
        if m > 300: return "HYDROGEN/HELIUM ENVELOPE — GAS GIANT"
        if m > 10:  return "WATER/METHANE/AMMONIA ICE MANTLE"
        if t > 1500: return "SILICATE MELT — LAVA OCEAN WORLD"
        if t > 700:  return "SILICATE ROCK — VOLCANIC ATMOSPHERE"
        if 200 < t < 350: return "SILICATE ROCK — POTENTIAL LIQUID WATER"
        return "ROCKY SILICATE — THIN ATMOSPHERE"

    def random_planet(self, probe_au, sector):
        if not self.planets:
            return None
        p = random.choice(self.planets).copy()
        p["sector"]   = sector
        p["probe_au"] = round(probe_au, 3)
        p["bearing"]  = random.randint(0, 359)
        p["seed"]     = random.randint(0, 9999)
        return p


# ═══════════════════════════════════════════════════════════════════════════════
#  PROBE STATE
# ═══════════════════════════════════════════════════════════════════════════════
class ProbeState:
    def __init__(self, exodb):
        self.exodb          = exodb
        self.distance_au    = 0.0
        self.sector         = 0
        self.power          = 100.0
        self.fuel           = 100.0
        self.signal         = 100.0
        self.days           = 0
        self.speed_kms      = 17.0
        self.catalogue      = []
        self.encountered    = 0
        self.catalogued     = 0
        self.transmissions  = 0
        self.slingshots     = 0
        self.current_object = None
        self.scanned        = False
        self.analyzed       = False
        self.probe_name     = "VOYAGER-SIM"
        self.mission        = "DEEP SPACE SURVEY"

    @property
    def region(self):
        for lo, hi, name in REGIONS:
            if lo <= self.distance_au < hi:
                return name
        return "DEEP SPACE"

    def navigate(self):
        self.sector      += 1
        self.distance_au += AU_PER_SECTOR
        self.days        += max(3, int(AU_PER_SECTOR * 149_597_870 /
                                       (self.speed_kms * 86400)) + random.randint(1, 4))
        self.power        = max(0.0, self.power - random.uniform(0.25, 0.65))
        self.fuel         = max(0.0, self.fuel  - random.uniform(0.4,  1.0))
        self.signal       = max(2.0, 100.0 - self.distance_au * 2.4)

        if random.random() < 0.65:
            self._spawn()
            self.encountered += 1
            return True
        self.current_object = None
        self.scanned        = False
        self.analyzed       = False
        return False

    def _spawn(self):
        # ~25% chance of inserting a real exoplanet (if DB has loaded)
        if self.exodb.planets and random.random() < 0.25:
            obj = self.exodb.random_planet(self.distance_au, self.sector)
        else:
            obj = PhysicsGen.generate(self.distance_au, self.sector)
        self.current_object = obj
        self.scanned        = False
        self.analyzed       = False

    # ── Slingshot physics ──────────────────────────────────────────────────
    def slingshot_dv(self):
        """
        Simplified gravity assist delta-v:  Δv = 1.3 · √(M/r) · mag_bonus
        Calibrated so Jupiter (318 M⊕) at 5 AU gives ≈12 km/s, consistent
        with Voyager 1's actual gain at Jupiter flyby.
        """
        obj = self.current_object
        M   = obj["mass_earth"]
        r   = max(0.001, obj["distance_au"])
        dv  = 1.3 * math.sqrt(M / r)
        if obj["magnetic"]:
            dv *= 1.15          # magnetic field → stronger field = tighter orbit
        return min(28.0, dv)

    def slingshot_fuel(self):
        """Fuel cost for periapsis correction burn (1.5 – ~4 %)."""
        return round(1.5 + self.current_object["mass_earth"] / 400.0, 2)


# ═══════════════════════════════════════════════════════════════════════════════
#  VOYAGER APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════
class VoyagerApp:
    def __init__(self, root, exodb):
        self.root   = root
        self.exodb  = exodb
        self.state  = ProbeState(exodb)
        self.stars  = []
        self.nebulae= []
        self._ok    = True       # input enabled flag
        self._hist  = []
        self._hidx  = 0
        self._build_ui()
        self._gen_bg()
        self._redraw()
        self._boot()

    # ── BUILD UI ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.root.title("JPL DEEP SPACE NETWORK  |  PROBE SIMULATOR v2.0  |  1977")
        self.root.configure(bg=BLACK)
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._c_quit)

        mono   = ("Courier", 9)
        mono_b = ("Courier", 9, "bold")

        # Header
        hdr = tk.Frame(self.root, bg=BLACK, pady=3)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="JPL DEEP SPACE NETWORK  ──  PROBE MISSION SIMULATOR v2.0",
                 fg=GREEN, bg=BLACK, font=("Courier", 11, "bold")).pack()
        tk.Label(hdr,
                 text="JET PROPULSION LABORATORY  │  CALIFORNIA INST. OF TECHNOLOGY  │  1977",
                 fg=DIM, bg=BLACK, font=("Courier", 8)).pack()
        tk.Frame(self.root, bg=GREEN, height=1).pack(fill=tk.X, padx=4)

        # Main row: canvas + panel
        row = tk.Frame(self.root, bg=BLACK)
        row.pack(fill=tk.X, padx=4, pady=3)

        self.canvas = tk.Canvas(row, width=CANVAS_W, height=CANVAS_H,
                                bg=BLACK, highlightthickness=1,
                                highlightbackground=DIMMER)
        self.canvas.pack(side=tk.LEFT)

        sp = tk.Frame(row, bg=BLACK, padx=6, width=PANEL_W)
        sp.pack(side=tk.LEFT, fill=tk.Y)
        sp.pack_propagate(False)
        tk.Label(sp, text="[ PROBE TELEMETRY ]", fg=AMBER,
                 bg=BLACK, font=mono_b).pack(anchor=tk.W, pady=(0, 4))

        self._sv = {}
        panel_rows = [
            ("PROBE",    "probe"),  ("MISSION",   "mission"),
            ("DAY",      "day"),    ("DISTANCE",  "dist"),
            ("SECTOR",   "sector"), ("REGION",    "region"),
            ("SPEED",    "speed"),
            (None, None),
            ("RTG POWER","power"),  ("RCS FUEL",  "fuel"),
            ("DSN SIG",  "signal"),
            (None, None),
            ("DETECTED", "enc"),    ("CATALOGUED","cat"),
            ("TX BURSTS","tx"),     ("SLINGSHOTS","sl"),
            (None, None),
            ("EXODB",    "exodb"),
        ]
        for label, key in panel_rows:
            if key is None:
                tk.Frame(sp, bg=DIMMER, height=1).pack(fill=tk.X, pady=2)
                continue
            r = tk.Frame(sp, bg=BLACK)
            r.pack(fill=tk.X)
            tk.Label(r, text=f"{label}:", fg=DIM, bg=BLACK,
                     font=mono, width=10, anchor=tk.W).pack(side=tk.LEFT)
            v = tk.StringVar(value="--")
            self._sv[key] = v
            tk.Label(r, textvariable=v, fg=GREEN, bg=BLACK,
                     font=mono, anchor=tk.W).pack(side=tk.LEFT)

        tk.Frame(self.root, bg=DIMMER, height=1).pack(fill=tk.X, padx=4)

        # Terminal
        self.term = scrolledtext.ScrolledText(
            self.root, width=94, height=13, bg=DARK, fg=GREEN,
            font=("Courier", 10), insertbackground=GREEN,
            selectbackground=DIMMER, relief=tk.FLAT,
            state=tk.DISABLED, wrap=tk.WORD, padx=6, pady=4,
        )
        self.term.pack(padx=4, pady=(3, 0))
        for tag, col in [("hdr", AMBER), ("ok", BRIGHT), ("warn", ORANGE),
                         ("err", RED),   ("dim", DIM),   ("norm", GREEN)]:
            self.term.tag_config(tag, foreground=col)

        tk.Frame(self.root, bg=DIMMER, height=1).pack(fill=tk.X, padx=4)

        # Input
        inp = tk.Frame(self.root, bg=BLACK, pady=4)
        inp.pack(fill=tk.X, padx=4)
        tk.Label(inp, text="READY >", fg=AMBER, bg=BLACK,
                 font=("Courier", 10, "bold")).pack(side=tk.LEFT)
        self._ivar  = tk.StringVar()
        self._entry = tk.Entry(inp, textvariable=self._ivar, bg=BLACK,
                               fg=GREEN, font=("Courier", 10),
                               insertbackground=GREEN, relief=tk.FLAT, width=80)
        self._entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._entry.bind("<Return>", self._on_enter)
        self._entry.bind("<Up>",     self._hu)
        self._entry.bind("<Down>",   self._hd)
        self._entry.focus_set()

        tk.Frame(self.root, bg=DIMMER, height=1).pack(fill=tk.X, padx=4)
        tk.Label(self.root,
                 text="  DSN MADRID  │  DSN GOLDSTONE  │  DSN CANBERRA  │  SIGNAL LOCKED",
                 fg=DIMMER, bg=BLACK, font=("Courier", 7)).pack(anchor=tk.W, padx=4)

        self._poll_exodb()

    # ── BACKGROUND ────────────────────────────────────────────────────────────
    def _gen_bg(self):
        random.seed(42)
        self.stars = [
            (random.randint(0, CANVAS_W), random.randint(0, CANVAS_H),
             random.choice([1,1,1,2]),
             random.choice([DIMMER, DIM, "#224422", "#33AA33", GREEN]))
            for _ in range(STAR_COUNT)
        ]
        self.nebulae = [
            (random.randint(50, CANVAS_W-50), random.randint(20, CANVAS_H-20),
             random.randint(20,55), random.randint(10,30))
            for _ in range(NEBULA_COUNT)
        ]
        random.seed()

    # ── CANVAS ────────────────────────────────────────────────────────────────
    def _redraw(self):
        c = self.canvas
        c.delete("all")
        s = self.state

        for nx,ny,rx,ry in self.nebulae:
            c.create_oval(nx-rx,ny-ry,nx+rx,ny+ry,fill=DIMMER,outline="",stipple="gray12")
        for sx,sy,sz,col in self.stars:
            c.create_oval(sx,sy,sx+sz,sy+sz,fill=col,outline="")

        c.create_line(0,CANVAS_H//2,CANVAS_W,CANVAS_H//2,fill=DIMMER,dash=(2,10))

        # Probe
        px, py = 90, CANVAS_H//2
        c.create_arc(px-12,py-18,px+12,py+2,start=0,extent=180,style=tk.ARC,outline=GREEN,width=1)
        c.create_line(px,py-18,px,py-9,fill=DIM,width=1)
        c.create_rectangle(px-10,py-4,px+10,py+4,fill=DIMMER,outline=GREEN,width=1)
        for side in (-1, 1):
            x0, x1 = px + side*10, px + side*28
            c.create_line(x0,py,x1,py,fill=GREEN,width=1)
            c.create_rectangle(min(x0,x1)+abs(side*10)-8,py-6,
                               max(x0,x1)-abs(side*10)+8,py+6,
                               fill=DIMMER,outline=DIM,width=1)
        c.create_line(px+10,py+4,px+22,py+18,fill=DIM,width=1)
        c.create_oval(px+20,py+15,px+26,py+22,fill=AMBER,outline=DIM)
        glow = AMBER if s.speed_kms > 25 else DIM
        c.create_line(px+10,py,px+30,py,fill=glow,width=1,dash=(1,3))

        if s.current_object:
            self._draw_obj(c, px, py)

        # HUD text
        for i,(txt,val) in enumerate([
            ("DIST: ", f"{s.distance_au:.3f} AU"),
            ("DAY:  ", f"{s.days:04d}"),
            ("SEC:  ", f"{s.sector:04d}"),
            ("SPD:  ", f"{s.speed_kms:.1f} KM/S"),
        ]):
            col = AMBER if (i==3 and s.speed_kms>25) else DIM
            c.create_text(8, 8+i*10, anchor=tk.NW,
                          text=txt+val, fill=col, font=("Courier",8))

        self._bar(c, CANVAS_W-82, 8,  62, 7, s.power/100,  "PWR", GREEN)
        self._bar(c, CANVAS_W-82, 20, 62, 7, s.fuel/100,   "FUL", AMBER)
        self._bar(c, CANVAS_W-82, 32, 62, 7, s.signal/100, "SIG", DIM)

    def _bar(self, c, x, y, w, h, frac, label, col):
        c.create_rectangle(x,y,x+w,y+h,fill=BLACK,outline=DIMMER)
        c.create_rectangle(x,y,x+max(1,int(w*frac)),y+h,fill=col,outline="")
        c.create_text(x-3,y+h//2,anchor=tk.E,text=label,fill=DIM,font=("Courier",7))

    def _draw_obj(self, c, px, py):
        obj = self.state.current_object
        art = obj["art"]
        ox, oy = 400, CANVAS_H//2
        rng = random.Random(obj["seed"])
        src = obj.get("source","PROCEDURAL")

        # Source tag
        is_real = "NASA" in src or "EMBEDDED" in src
        c.create_text(ox, oy-65,
                      text="★ CONFIRMED EXOPLANET" if is_real else "GENERATED (PHYSICS MODEL)",
                      fill=AMBER if is_real else DIM, font=("Courier",7))

        r = 36
        if art == "PLANET":
            c.create_oval(ox-r,oy-r,ox+r,oy+r,fill="#001A00",outline=GREEN,width=2)
            for i in range(4):
                yb = oy-r+10+i*15
                c.create_line(ox-r+4,yb,ox+r-4,yb,fill=DIMMER,dash=(4,5))

        elif art == "RINGED":
            r = 28
            c.create_oval(ox-r-26,oy-8,ox+r+26,oy+8,fill="",outline=DIM,width=2)
            c.create_oval(ox-r-20,oy-5,ox+r+20,oy+5,fill="",outline=GREEN,width=1)
            c.create_oval(ox-r,oy-r,ox+r,oy+r,fill="#001A00",outline=GREEN,width=2)
            for i in range(3):
                yb = oy-r+10+i*14
                c.create_line(ox-r+4,yb,ox+r-4,yb,fill=DIMMER,dash=(3,4))
            c.create_arc(ox-r-26,oy-8,ox+r+26,oy+8,start=180,extent=180,
                         style=tk.ARC,outline=DIM,width=2)

        elif art == "ASTEROID":
            pts = []
            for i in range(9):
                a = (i/9)*2*math.pi
                rd = rng.randint(12,25)
                pts += [ox+rd*math.cos(a), oy+rd*math.sin(a)]
            c.create_polygon(pts,fill="#001000",outline=GREEN,width=1)
            for _ in range(3):
                cx=ox+rng.randint(-12,12); cy=oy+rng.randint(-12,12)
                cr=rng.randint(2,5)
                c.create_oval(cx-cr,cy-cr,cx+cr,cy+cr,fill="",outline=DIMMER)

        elif art == "COMET":
            c.create_oval(ox-9,oy-9,ox+9,oy+9,fill="#001A00",outline=GREEN,width=2)
            for i in range(1,11):
                tx=ox+9+i*10; ty=(9-i)*2
                c.create_line(tx,oy-ty,tx+6,oy+ty,fill=DIM if i>5 else GREEN)
            c.create_oval(ox-14,oy-14,ox+14,oy+14,fill="",outline=DIMMER,dash=(2,4))

        elif art == "MOON":
            r = 20
            c.create_oval(ox-r,oy-r,ox+r,oy+r,fill="#001000",outline=DIM,width=2)
            for _ in range(4):
                cx=ox+rng.randint(-13,13); cy=oy+rng.randint(-13,13)
                cr=rng.randint(2,5)
                c.create_oval(cx-cr,cy-cr,cx+cr,cy+cr,fill="",outline=DIMMER)

        # Status badge
        if not self.state.scanned:
            badge, bc = "[ UNCHARTED OBJECT ]", AMBER
        elif not self.state.analyzed:
            badge, bc = "[ SCANNED — ANALYZE? ]", GREEN
        else:
            badge, bc = "[ DATA ACQUIRED ]", BRIGHT
        c.create_text(ox, oy-54, text=badge, fill=bc, font=("Courier",8,"bold"))
        c.create_text(ox, oy+55,
                      text=f"{obj['name']}  [{obj['type']}]",
                      fill=GREEN, font=("Courier",8))

        # Slingshot hint
        if self.state.analyzed and obj["mass_earth"] >= 0.5:
            dv = self.state.slingshot_dv()
            c.create_text(ox, oy+67,
                          text=f"⇒ SLINGSHOT AVAIL  +{dv:.1f} KM/S  USE 'SL'",
                          fill=ORANGE, font=("Courier",7))

        # Range line
        c.create_line(px+40, CANVAS_H//2, ox-32, oy, fill=DIMMER, dash=(2,6))

    # ── STATUS PANEL ──────────────────────────────────────────────────────────
    def _upd(self):
        s = self.state
        self._sv["probe"].set(s.probe_name)
        self._sv["mission"].set(s.mission[:12])
        self._sv["day"].set(f"DAY {s.days:04d}")
        self._sv["dist"].set(f"{s.distance_au:.3f} AU")
        self._sv["sector"].set(f"{s.sector:04d}")
        self._sv["region"].set(s.region[:14])
        self._sv["speed"].set(f"{s.speed_kms:.1f} KM/S")
        self._sv["power"].set(f"{s.power:.1f}%")
        self._sv["fuel"].set(f"{s.fuel:.1f}%")
        self._sv["signal"].set(f"{s.signal:.1f}%")
        self._sv["enc"].set(str(s.encountered))
        self._sv["cat"].set(str(s.catalogued))
        self._sv["tx"].set(str(s.transmissions))
        self._sv["sl"].set(str(s.slingshots))
        self._sv["exodb"].set(self.exodb.status[:14])

    def _poll_exodb(self):
        self._upd()
        self.root.after(2000, self._poll_exodb)

    # ── TERMINAL ──────────────────────────────────────────────────────────────
    def _pr(self, text="", tag="norm"):
        self.term.configure(state=tk.NORMAL)
        self.term.insert(tk.END, text + "\n", tag)
        self.term.configure(state=tk.DISABLED)
        self.term.see(tk.END)

    def _sep(self):
        self._pr("─" * 76, "dim")

    def _clr(self):
        self.term.configure(state=tk.NORMAL)
        self.term.delete("1.0", tk.END)
        self.term.configure(state=tk.DISABLED)

    # ── INPUT ─────────────────────────────────────────────────────────────────
    def _on_enter(self, _e):
        if not self._ok: return
        raw = self._ivar.get().strip()
        if not raw: return
        cmd = raw.upper()
        self._hist.append(cmd)
        self._hidx = len(self._hist)
        self._ivar.set("")
        self._pr(f"  > {cmd}", "dim")
        self._dispatch(cmd)

    def _hu(self, _e):
        if self._hist and self._hidx > 0:
            self._hidx -= 1
            self._ivar.set(self._hist[self._hidx])

    def _hd(self, _e):
        if self._hidx < len(self._hist)-1:
            self._hidx += 1
            self._ivar.set(self._hist[self._hidx])
        else:
            self._hidx = len(self._hist)
            self._ivar.set("")

    # ── DISPATCH ──────────────────────────────────────────────────────────────
    def _dispatch(self, cmd):
        tbl = {
            "HELP": self._c_help,      "H":   self._c_help,
            "STATUS": self._c_status,  "ST":  self._c_status,
            "NAVIGATE": self._c_nav,   "NAV": self._c_nav,  "N": self._c_nav,
            "SCAN": self._c_scan,      "SC":  self._c_scan,
            "ANALYZE": self._c_analyze,"AN":  self._c_analyze,
            "SLINGSHOT": self._c_sl,   "SL":  self._c_sl,
            "CATALOGUE": self._c_cat,  "CAT": self._c_cat,
            "LOG": self._c_log,        "L":   self._c_log,
            "TRANSMIT": self._c_tx,    "TX":  self._c_tx,
            "CLEAR": self._clr,        "CLS": self._clr,
            "QUIT": self._c_quit,      "Q":   self._c_quit,
            "EXIT": self._c_quit,
        }
        fn = tbl.get(cmd.split()[0])
        if fn:
            fn()
        else:
            self._pr(f"  ** UNKNOWN COMMAND: {cmd}", "err")
            self._pr("  TYPE 'HELP' FOR COMMAND LIST.", "dim")

    # ═════════════════════════════════════════════════════════════════════════
    #  COMMANDS
    # ═════════════════════════════════════════════════════════════════════════
    def _c_help(self):
        self._sep()
        self._pr("  AVAILABLE COMMANDS — JPL INTERFACE v2.0", "hdr")
        self._sep()
        for cmd, desc in [
            ("NAVIGATE  NAV  N",  "ADVANCE PROBE TO NEXT SECTOR"),
            ("SCAN      SC",      "WIDE-FIELD SENSOR SWEEP"),
            ("ANALYZE   AN",      "DEEP SPECTRAL / COMPOSITION ANALYSIS"),
            ("SLINGSHOT SL",      "GRAVITY-ASSIST MANEUVER (NEEDS ANALYSIS)"),
            ("CATALOGUE CAT",     "LOG OBJECT TO MISSION RECORD"),
            ("STATUS    ST",      "FULL PROBE TELEMETRY"),
            ("LOG       L",       "VIEW MISSION CATALOGUE"),
            ("TRANSMIT  TX",      "SEND DATA BURST TO EARTH"),
            ("CLEAR     CLS",     "CLEAR TERMINAL"),
            ("QUIT      Q  EXIT", "TERMINATE MISSION"),
            ("HELP      H",       "THIS SCREEN"),
        ]:
            self._pr(f"  {cmd:<24} {desc}")
        self._sep()
        self._pr("  UP/DOWN ARROWS = COMMAND HISTORY", "dim")
        self._sep()

    def _c_status(self):
        s = self.state
        self._sep()
        self._pr("  PROBE TELEMETRY — FULL REPORT", "hdr")
        self._sep()
        for k,v in [
            ("PROBE DESIGNATION ", s.probe_name),
            ("MISSION NAME      ", s.mission),
            ("ELAPSED MISSION   ", f"DAY {s.days}"),
            ("DISTANCE FROM SOL ", f"{s.distance_au:.4f} AU"),
            ("CURRENT SECTOR    ", f"{s.sector:04d}"),
            ("REGION            ", s.region),
            ("CRUISE VELOCITY   ", f"{s.speed_kms:.2f} KM/S"),
            ("RTG POWER         ", f"{s.power:.2f}%"),
            ("RCS FUEL          ", f"{s.fuel:.2f}%"),
            ("DSN SIGNAL        ", f"{s.signal:.2f}%"),
            ("OBJECTS DETECTED  ", str(s.encountered)),
            ("OBJECTS CATALOGUED", str(s.catalogued)),
            ("DATA TRANSMISSIONS", str(s.transmissions)),
            ("SLINGSHOTS USED   ", str(s.slingshots)),
            ("EXOPLANET DB      ", self.exodb.status),
        ]:
            self._pr(f"  {k}: {v}")
        for cond, msg in [
            (s.power  < 20, "LOW RTG POWER"),
            (s.fuel   < 15, "LOW RCS FUEL"),
            (s.signal < 15, "WEAK DSN SIGNAL"),
        ]:
            if cond:
                self._pr(f"  *** WARNING: {msg} ***", "warn")
        self._sep()

    def _c_nav(self):
        s = self.state
        if s.fuel < 0.5:
            self._pr("  ** NAVIGATION ABORT: INSUFFICIENT RCS FUEL **", "err"); return
        if s.power < 1.5:
            self._pr("  ** NAVIGATION ABORT: CRITICAL POWER **", "err"); return

        self._pr(f"  NAVIGATION BURN — SECTOR {s.sector:04d}→{s.sector+1:04d}…", "dim")
        hit = s.navigate()
        self._upd(); self._redraw()
        self._pr(f"  COMPLETE.  SECTOR {s.sector:04d}  │  {s.distance_au:.3f} AU  │  {s.region}", "ok")

        if hit:
            obj = s.current_object
            src = obj.get("source","")
            self._sep()
            self._pr("  *** SENSOR ALERT — OBJECT IN RANGE ***", "warn")
            self._pr(f"  TYPE    : {obj['type']}")
            self._pr(f"  BEARING : {obj['bearing']:03d}°")
            self._pr(f"  RANGE   : {obj['distance_au']:.4f} AU")
            if "NASA" in src or "EMBEDDED" in src:
                self._pr("  SOURCE  : ★ CONFIRMED EXOPLANET MATCH", "hdr")
            else:
                self._pr("  SOURCE  : PHYSICS-GENERATED OBJECT", "dim")
            self._pr("  USE 'SCAN' TO BEGIN SENSOR SWEEP.", "dim")
        else:
            self._pr("  SENSOR SWEEP NEGATIVE — NO OBJECTS IN RANGE.", "dim")

    def _c_scan(self):
        s = self.state
        if not s.current_object:
            self._pr("  NO OBJECT IN RANGE. USE 'NAVIGATE'.", "dim"); return
        if s.scanned:
            self._pr("  SCAN DONE. USE 'ANALYZE'.", "dim"); return

        obj = s.current_object
        self._sep()
        self._pr("  SENSOR SWEEP ACTIVE…", "dim")
        self._pr(f"  DESIGNATION  : {obj['name']}", "hdr")
        self._pr(f"  OBJECT CLASS : {obj['type']}")
        self._pr(f"  RANGE        : {obj['distance_au']:.4f} AU")
        self._pr(f"  BEARING      : {obj['bearing']:03d}°")
        self._pr(f"  EST. DIAMETER: {obj['diameter_km']:.1f} KM")
        self._pr(f"  SURFACE TEMP : {obj['temp_k']} K")
        self._pr(f"  MAGNETOMETER : {'FIELD DETECTED' if obj['magnetic'] else 'NEGATIVE'}")
        self._pr(f"  RADIATION    : {obj['radiation']:.1f} RADS/HR")
        self._pr("  SWEEP COMPLETE. USE 'ANALYZE'.", "ok")
        s.scanned = True
        self._redraw()

    def _c_analyze(self):
        s = self.state
        if not s.current_object:
            self._pr("  NO OBJECT IN RANGE.", "dim"); return
        if not s.scanned:
            self._pr("  ** RUN 'SCAN' FIRST **", "err"); return
        if s.analyzed:
            self._pr("  ANALYSIS ON FILE. USE 'CATALOGUE' OR 'SLINGSHOT'.", "dim"); return

        obj = s.current_object
        src = obj.get("source","PROCEDURAL")
        self._sep()
        self._pr("  DEEP SPECTRAL ANALYSIS…", "dim")
        self._pr(f"  DESIGNATION  : {obj['name']}", "hdr")
        self._pr(f"  CLASS        : {obj['type']}")
        self._pr(f"  COMPOSITION  : {obj['composition']}")
        self._pr(f"  MASS         : {obj['mass_earth']:.4f} M⊕")
        self._pr(f"  DIAMETER     : {obj['diameter_km']:.1f} KM")
        self._pr(f"  TEMP         : {obj['temp_k']} K  /  {obj['temp_k']-273:.0f} °C")
        self._pr(f"  MAGNETIC FIELD: {'CONFIRMED' if obj['magnetic'] else 'ABSENT'}")
        self._pr(f"  RADIATION    : {obj['radiation']:.1f} RADS/HR")
        self._pr(f"  DATA SOURCE  : {src}")
        if "real_au" in obj:
            self._pr(f"  ACTUAL ORBIT : {obj['real_au']} AU (AROUND HOST STAR)")

        notes = []
        t = obj["temp_k"]
        if t > 1500:          notes.append("EXTREME HEAT — LAVA OCEAN POSSIBLE")
        if t < 60:            notes.append("CRYOGENIC SURFACE — VOLATILE ICES")
        if 200 < t < 350:     notes.append("TEMP IN HABITABLE ZONE RANGE")
        if obj["magnetic"]:   notes.append("MAGNETIC FIELD — POSSIBLE METALLIC CORE")
        if obj["radiation"] > 600: notes.append("HIGH RADIATION — INSTRUMENT RISK")
        if obj["mass_earth"] > 100: notes.append("HIGH MASS — STRONG GRAVITY WELL")
        if obj["mass_earth"] >= 0.5:
            dv = s.slingshot_dv()
            fc = s.slingshot_fuel()
            notes.append(f"GRAVITY VIABLE FOR ASSIST — 'SL' → +{dv:.1f} KM/S  (-{fc:.1f}% FUEL)")
        if "WATER" in obj["composition"].upper():
            notes.append("WATER SIGNATURE — FLAG FOR MISSION SCIENCE TEAM")

        if notes:
            self._pr("  SCIENCE NOTES:", "hdr")
            for n in notes:
                self._pr(f"    + {n}")

        self._pr("  ANALYSIS COMPLETE.", "ok")
        s.analyzed = True
        s.power = max(0.0, s.power - 1.5)
        self._redraw(); self._upd()

    # ── SLINGSHOT ─────────────────────────────────────────────────────────────
    def _c_sl(self):
        """
        Gravity-assist maneuver using the Oberth effect.

        Real-world basis: Voyager 1 gained ≈10–12 km/s from Jupiter flyby.
        Formula: Δv = 1.3 · √(M_planet / r_periapsis) · mag_bonus
          where M is in Earth masses, r in AU.
        Magnetic field bonus: +15% (field lines help constrain approach).
        Fuel cost: 1.5% base + M/400% for precision correction burns.
        Radiation risk: objects with >400 rads/hr may damage RTG.
        """
        s   = self.state
        obj = s.current_object

        if not obj:
            self._pr("  NO OBJECT IN RANGE.", "dim"); return
        if not s.analyzed:
            self._pr("  ** ANALYSIS REQUIRED BEFORE SLINGSHOT **", "err")
            self._pr("  ISSUE 'ANALYZE' FIRST TO CHARACTERIZE THE GRAVITY WELL.", "dim")
            return
        if obj["mass_earth"] < 0.5:
            self._pr("  ** SLINGSHOT ABORT: OBJECT TOO SMALL **", "err")
            self._pr(f"  MASS {obj['mass_earth']:.5f} M⊕ — MINIMUM 0.5 M⊕ REQUIRED.", "dim")
            self._pr("  GRAVITATIONAL WELL INSUFFICIENT FOR TRAJECTORY ASSIST.", "dim")
            return

        fc = s.slingshot_fuel()
        if s.fuel < fc:
            self._pr(f"  ** ABORT: NEED {fc:.1f}% FUEL FOR CORRECTION BURN **", "err"); return

        dv       = s.slingshot_dv()
        v_before = s.speed_kms
        v_after  = v_before + dv
        rad      = obj["radiation"]

        self._sep()
        self._pr("  GRAVITY-ASSIST TRAJECTORY COMPUTATION…", "dim")
        self._pr(f"  TARGET OBJECT    : {obj['name']}", "hdr")
        self._pr(f"  OBJECT MASS      : {obj['mass_earth']:.4f} M⊕")
        self._pr(f"  PERIAPSIS RANGE  : {obj['distance_au']:.4f} AU")
        self._pr(f"  MAGNETIC BONUS   : {'YES (+15% Δv)' if obj['magnetic'] else 'NO'}")
        self._pr("")
        self._pr("  TRAJECTORY SOLUTION:", "hdr")
        self._pr(f"  APPROACH ANGLE   : {obj['bearing']:03d}°  (HYPERBOLIC FLYBY)")
        self._pr(f"  COMPUTED Δv      : +{dv:.2f} KM/S  (OBERTH EFFECT)")
        self._pr(f"  FUEL COST        : -{fc:.2f}%  (PERIAPSIS CORRECTION BURN)")
        self._pr(f"  VELOCITY BEFORE  : {v_before:.2f} KM/S")
        self._pr(f"  VELOCITY AFTER   : {v_after:.2f} KM/S")
        self._pr("")

        # Radiation risk
        damage_msg = None
        if rad > 700 and random.random() < 0.28:
            dmg = round(random.uniform(8.0, 16.0), 1)
            s.power = max(0.0, s.power - dmg)
            damage_msg = (f"  *** RADIATION TRANSIT DAMAGE: -{dmg}% RTG OUTPUT"
                          f"  ({rad:.0f} RADS/HR) ***", "err")
        elif rad > 400 and random.random() < 0.10:
            dmg = round(random.uniform(3.0, 7.0), 1)
            s.power = max(0.0, s.power - dmg)
            damage_msg = (f"  ** MINOR RADIATION EXPOSURE: -{dmg}% POWER **", "warn")

        # Apply
        s.fuel      = max(0.0, s.fuel - fc)
        s.speed_kms = v_after
        s.slingshots += 1
        s.days      += random.randint(5, 20)   # flyby takes time

        self._pr("  PERIAPSIS TRANSIT COMPLETE. GRAVITY-ASSIST SUCCESSFUL.", "ok")
        if damage_msg:
            self._pr(damage_msg[0], damage_msg[1])

        if v_after > 40:
            self._pr("  >> PROBE EXCEEDS 40 KM/S — RECORD VELOCITY!", "warn")
        elif v_after > 30:
            self._pr("  >> VELOCITY EXCEEDS 30 KM/S — MISSION ACCELERATED.", "warn")

        self._pr(f"  NEW CRUISE VELOCITY: {s.speed_kms:.2f} KM/S", "ok")
        self._sep()

        # Probe has passed the object
        s.current_object = None
        s.scanned = s.analyzed = False
        self._redraw(); self._upd()

    def _c_cat(self):
        s   = self.state
        obj = s.current_object
        if not obj:
            self._pr("  NO OBJECT TO CATALOGUE.", "dim"); return
        if not s.analyzed:
            self._pr("  ** SCAN AND ANALYZE FIRST **", "err"); return
        for e in s.catalogue:
            if e["name"] == obj["name"]:
                self._pr(f"  {obj['name']} ALREADY IN CATALOGUE.", "dim"); return

        s.catalogue.append(obj.copy())
        s.catalogued += 1
        cid = f"DSO-{s.catalogued:04d}"
        self._sep()
        self._pr("  OBJECT LOGGED TO MISSION CATALOGUE", "ok")
        self._pr(f"  CATALOGUE ID : {cid}")
        self._pr(f"  DESIGNATION  : {obj['name']}")
        self._pr(f"  TOTAL LOGGED : {s.catalogued}")
        self._sep()
        self._upd()

    def _c_log(self):
        s = self.state
        if not s.catalogue:
            self._pr("  CATALOGUE EMPTY.", "dim"); return
        self._sep()
        self._pr("  MISSION CATALOGUE — DEEP SPACE SURVEY OBJECTS", "hdr")
        self._sep()
        self._pr(f"  {'ID':<10}{'NAME':<22}{'TYPE':<16}{'AU':>6}  {'K':>5}  {'KM':>9}  SRC","hdr")
        self._pr("  "+"─"*76,"dim")
        for i, obj in enumerate(s.catalogue):
            src = "★" if ("NASA" in obj.get("source","") or
                          "EMBEDDED" in obj.get("source","")) else "·"
            self._pr(
                f"  DSO-{i+1:04d}  {obj['name']:<22}"
                f"{obj['type']:<16}{obj['probe_au']:>6.3f}"
                f"  {obj['temp_k']:>5}  {obj['diameter_km']:>9.1f}  {src}"
            )
        self._sep()
        self._pr(f"  TOTAL: {s.catalogued}   ★ = CONFIRMED EXOPLANET   · = GENERATED","ok")

    def _c_tx(self):
        s = self.state
        if not s.catalogue:
            self._pr("  NO DATA TO TRANSMIT.", "dim"); return
        delay = int(s.distance_au * LIGHT_MIN_PER_AU)
        conf  = sum(1 for e in s.catalogue
                    if "NASA" in e.get("source","") or "EMBEDDED" in e.get("source",""))
        self._sep()
        self._pr("  DSN DATA BURST TRANSMISSION…", "dim")
        self._pr(f"  DSN SIGNAL LEVEL  : {s.signal:.1f}%")
        self._pr(f"  ONE-WAY LIGHT LAG : {delay} MIN  ({delay//60}H {delay%60}M)")
        self._pr(f"  CATALOGUE ENTRIES : {len(s.catalogue)}")
        self._pr(f"  CONFIRMED EXOPLANETS IN BURST: {conf}")
        if s.signal < 10:
            self._pr("  ** SIGNAL MARGINAL — PARTIAL DATA ONLY **", "warn")
        self._pr("  BURST TRANSMITTED.", "ok")
        self._pr(f"  JPL RECEIVES IN ~{delay} MIN.", "dim")
        s.transmissions += 1
        s.power = max(0.0, s.power - 2.0)
        self._upd()
        self._sep()

    # ── QUIT ──────────────────────────────────────────────────────────────────
    def _c_quit(self):
        s = self.state
        self._sep()
        self._pr("  MISSION TERMINATION SEQUENCE…", "warn")
        self._pr(f"  FINAL DISTANCE    : {s.distance_au:.3f} AU", "norm")
        self._pr(f"  MISSION DURATION  : DAY {s.days}", "norm")
        self._pr(f"  OBJECTS CATALOGUED: {s.catalogued}", "norm")
        self._pr(f"  SLINGSHOTS USED   : {s.slingshots}", "norm")
        self._pr(f"  MAX VELOCITY REACH: {s.speed_kms:.1f} KM/S", "norm")
        self._pr(f"  DATA TRANSMISSIONS: {s.transmissions}", "norm")
        self._pr("", "norm")
        self._pr("  SAFING PROBE SUBSYSTEMS…", "dim")
        self._pr("  DSN GOLDSTONE UPLINK TERMINATED.", "dim")
        self._pr("  MISSION COMPLETE. JPL MISSION CONTROL OUT.", "ok")
        self.root.after(1800, self.root.destroy)

    # ── BOOT ──────────────────────────────────────────────────────────────────
    def _boot(self):
        self._ok = False
        lines = [
            ("╔═══════════════════════════════════════════════════════════════════╗","dim"),
            ("║   JPL DEEP SPACE NETWORK — PROBE MISSION SIMULATOR v2.0         ║","hdr"),
            ("║   JET PROPULSION LABORATORY  ·  CALTECH  ·  1977                ║","dim"),
            ("╚═══════════════════════════════════════════════════════════════════╝","dim"),
            ("","norm"),
            ("  POWERING ON PROBE SUBSYSTEMS…","dim"),("","norm"),
            ("  PLASMA SCIENCE DETECTOR  . . . . . . . . . . OK","norm"),
            ("  LOW ENERGY CHARGED PARTICLE SYS . . . . . . OK","norm"),
            ("  MAGNETOMETER (MAG)  . . . . . . . . . . . . OK","norm"),
            ("  COSMIC RAY SCIENCE SUBSYSTEM . . . . . . . . OK","norm"),
            ("  INFRARED INTERFEROMETER SPECTROMETER  . . . OK","norm"),
            ("  PHOTOPOLARIMETER RADIOMETER  . . . . . . . . OK","norm"),
            ("  RADIO SCIENCE / DSN UPLINK SYSTEM . . . . . OK","norm"),
            ("  RTG THERMOELECTRIC POWER UNITS . . . . . . . OK","norm"),
            ("  RCS ATTITUDE CONTROL THRUSTERS . . . . . . . OK","norm"),
            ("  DSN GOLDSTONE — SIGNAL LOCKED  . . . . . . . OK","norm"),
            ("  PHYSICS ENGINE (PROCEDURAL GEN)  . . . . . . OK","norm"),
            ("  NASA EXOPLANET ARCHIVE . . . . . . . . . . . BACKGROUND","warn"),
            ("","norm"),
            ("  ALL SYSTEMS NOMINAL.","ok"),("","norm"),
            ("  MISSION: NAVIGATE DEEP SPACE. CATALOGUE OBJECTS.","norm"),
            ("  USE GRAVITY-ASSIST SLINGSHOTS TO ACCELERATE.","norm"),
            ("  TRANSMIT FINDINGS TO JPL VIA DSN.","norm"),("","norm"),
            ("  'HELP' or 'H' — COMMAND LIST","warn"),
            ("  'N'          — BEGIN MISSION","warn"),("","norm"),
        ]
        def step(i=0):
            if i >= len(lines):
                self._ok = True; self._upd(); return
            self._pr(*lines[i])
            self.root.after(55, lambda: step(i+1))
        self.root.after(300, step)


# ═══════════════════════════════════════════════════════════════════════════════
def main():
    exodb = ExoplanetDB()       # start background fetch immediately
    root  = tk.Tk()
    VoyagerApp(root, exodb)
    root.mainloop()

if __name__ == "__main__":
    main()
