# Bill of Materials — UK Sourcing

Researched 2026-08-29, delivery to London. Prices verified on the day unless
marked *(unverified)* — Amazon UK and some distributor pages block automated
price checks; those show typical street prices.

## Core electronics

| Item | Pick | Price | Supplier | Notes |
|---|---|---|---|---|
| Servos ×5 | Feetech/Waveshare **ST3215 12 V, 30 kg·cm** | £21.75 ea (£108.75) | [Waveshare official eBay UK store](https://www.ebay.co.uk/itm/265782094249) | Ships Shenzhen, ~6–12 days. **Value path:** WowRobo/AliExpress 5-pack ≈ £12–14/servo (~£65), 1–2 wk wait |
| Servo driver | **Waveshare Serial Bus Servo Driver HAT (A)** | £18.30 | [The Pi Hut](https://thepihut.com/products/serial-bus-servo-driver-hat-for-raspberry-pi-with-esp32) | In stock. Sits on Pi header, 9–25 V in, drives whole ST-series chain, **onboard 5 V buck can power the Pi** |
| Compute | **Raspberry Pi 5 8 GB** | £168.00 | [The Pi Hut](https://thepihut.com/products/raspberry-pi-5) | In stock. ⚠ RAM-shortage-era pricing. Pimoroni lists **£140 but out of stock** — watch for restock. microSD ~£10 extra |
| Pi PSU (bench/dev) | Official 27 W USB-C | £11.50 | [The Pi Hut](https://thepihut.com/products/raspberry-pi-27w-usb-c-power-supply) | Optional in final build (HAT powers Pi from 12 V) |
| Cooling | Active Cooler for Pi 5 | £4.80 | [The Pi Hut](https://thepihut.com/products/active-cooler-for-raspberry-pi-5) | In stock |
| Mic array | **ReSpeaker XMOS XVF3800 USB 4-mic** | £52.80 | [The Pi Hut](https://thepihut.com/products/respeaker-xmos-xvf3800-ai-powered-4-mic-array-for-clear-voice-even-in-noise) | In stock. DOA exposed over USB (`AEC_AZIMUTH_VALUES` via host_control), VAD, LED ring. **v2.0 (XVF-3000) is discontinued** — don't chase it. ReSpeaker Lite is 2-mic (left/right only), not suitable |
| ToF sensor | **Pololu VL53L7CX carrier** (8×8, 60°×60° FoV, 350 cm) | £19.20 | [The Pi Hut](https://thepihut.com/products/vl53l7cx-time-of-flight-8x8-zone-wide-fov-distance-sensor-carrier-with-voltage-regulator-350cm-max) | In stock. Budget alt: Pimoroni VL53L5CX £16.25 (narrower 45°×45°) |
| Piezo | **PS1240** + enclosed piezo element | £1.30 + £0.90 | [The Pi Hut](https://thepihut.com/products/piezo-buzzer) | In stock. Optional PAM8904 driver amp £4.80 for louder chirps |

## Display module

Single-panel strategy: buy only the fine-pitch panel the head will actually
use, and bench-test optics directly on it. (Optics calibration — focal
length, lens distance, diffuser gap, focus LUT — is specific to the panel's
physical size, so nothing done on a cheap 10 mm-pitch panel would transfer;
the general gotchas below are already settled by prior art.)

| Item | Pick | Price | Supplier | Notes |
|---|---|---|---|---|
| Head matrix | **BTF WS2812B-2427 mini flexible panel** (fine pitch) | $50.99 (~£40) | [BTF direct](https://www.btf-lighting.com/products/ws2812b-mini-led-smd-2427-digital-11x44-22x22-digital-flexible-led-panel-screen-individually-addressable-dc5v) | 1–2 wk from China. Comes as 22×22/11×44 — order the 22×22 and use its **full native grid** (more pixels = better; software is grid-parametric). Verify pitch/layout on arrival. **Fallback if it disappoints:** rigid 16×16 boards on AliExpress ~£10–18, ordered later |
| Projection lens | 100 mm double-convex glass lens | £13.20 | [eBay UK "lens-store"](https://www.ebay.co.uk/sch/i.html?_nkw=100mm+biconvex+lens+condenser) | Many diameter/FL combos in stock |
| Fresnel | A4 Fresnel page-magnifier sheet | ~£4–8 *(unverified)* | Amazon UK / [magnifyingglasses.co.uk](https://magnifyingglasses.co.uk/product-category/page-sheet-magnifiers/) | Grooved side toward the wall |
| Diffuser | LED diffuser sheet / thin acrylic | ~£5 | Amazon UK | See optics gotcha below |
| Focus servo | any 9 g micro servo | ~£4 | Amazon UK / Pi Hut | Slides lens on printed rail |

**Optics gotchas from prior art** ([WS2812 8×8 projector on Printables](https://www.printables.com/model/1470198-ws2812-8x8-projector),
[Hackaday coverage](https://hackaday.com/2025/11/07/an-led-projector-as-a-lighting-effect/),
[Ikea projection lamp conversion](https://hackaday.com/2016/06/14/projection-lamp-makeover-adds-led-matrix-and-raspberry-pi-zero/)):

1. A sharp lens images the **LED dies themselves** — 256 tiny rectangles.
   A mild diffuser (or a printed per-LED lens array) makes soft round pixels.
2. **Mirror/flip the image in software** — projection inverts it.
3. Match Fresnel size to panel size or the corners vignette.

## Power

| Item | Pick | Price | Supplier | Notes |
|---|---|---|---|---|
| Main PSU | **Mean Well GST60A12-P1J** desktop brick, 12 V/5 A | £23.00 | [The Pi Hut](https://thepihut.com/products/meanwell-12v-5a-60w-power-supply-gst60a12-p1j) | In stock. Sealed brick — no mains wiring in the build. 60 W is fine with firmware torque/current limits |
| LED buck | Waveshare 6–14 V → 5 V/8 A | £8.40 | [The Pi Hut](https://thepihut.com/products/dc-dc-buck-converter-6-14v-to-5v-8a) | In stock. Dedicated to matrix; HAT's own buck feeds the Pi |

(Higher-headroom alt: Mean Well LRS-100-12, 12 V/8.5 A, ~£23 on eBay UK — but
it's an enclosed-frame PSU needing a fused IEC inlet; the brick keeps mains
out of the printed base.)

## Mechanical

| Item | Price | Supplier |
|---|---|---|
| 25T servo horn set (ST3215 spline is 25T/⌀5.9 mm) | £2.40 (metal £3.10) | [The Pi Hut](https://thepihut.com/products/standard-servo-arm-and-horn-set-25-spline) |
| 120 mm aluminium lazy-susan bearing (base yaw) | ~£8–12 *(unverified)* | Amazon UK / eBay UK |
| 608ZZ bearings ×4 (printed-ring alternative) | £6.70 | [The Pi Hut](https://thepihut.com/products/radial-ball-bearing-608zz-set-of-4) |
| M3 heat-set inserts, 50-pack | £5.90 | [The Pi Hut](https://thepihut.com/products/brass-heat-set-inserts-for-plastic-m3-x-3mm-50-pack) |
| M3 screw/nut assortment kit | ~£13–17 *(unverified)* | Amazon UK |
| Anglepoise spring kit (counterbalance, O2) | ~£15–25 | [anglepoise.com](https://www.anglepoise.com/product/original-1227-spring-kit/) / eBay UK |
| Filament: PLA (shell) + PETG (joints) | ~£30 | usual suspects |

## Totals

**Chosen path (2026-08-29): patient** — China lead times are fine, single
fine-pitch panel only.

| Path | Servos | Pi 5 | Everything else | Total |
|---|---|---|---|---|
| Fast (eBay UK servos, Pi Hut Pi) | £109 | £168 | ~£278 | **~£555** |
| Mixed (multipack servos, Pi Hut Pi, skip bench PSU) | ~£68 | £168 | ~£262 | **~£498** |
| **Patient — chosen** (multipack servos, Pimoroni Pi restock) | ~£68 | £140 | ~£250 | **~£458** |

The single biggest line is the Pi 5 8 GB at current shortage pricing. Levers:
catch the Pimoroni restock (−£28), drop to 4 GB (fine for our workload if
faster-whisper uses the small model; −£60 when stocked), or use any Pi 5
already owned.

## Akihabara option (researched 2026-08-31)

Verified in-person alternatives while in Tokyo: **Akizuki Denshi** stocks the
Feetech **STS3215 7.4 V / 19.5 kg·cm** (¥3,200, 13 on the Akihabara shelf,
2F shelf 72) plus the **FE-URT-1** bus driver, 5 V/6 A bucks, piezo discs and
JST pigtails — a same-day Phase-2 bench kit. Voltage trade-off: 7.4 V halves
torque headroom vs the 12 V/30 kg·cm variant (validated emote peak is
8.0 kg·cm, so choreography fits with 2.4x margin; worst-case dragged poses
~13 kg·cm lean on the shoulder spring, O2). Don't mix variants on one bus
rail. Skip in Japan: ToF breakouts (no Akiba retail), Pi 5 (no longer
cheaper: ~¥33,900 ≈ £173), AC PSU bricks (100 V/Type-A — unsafe on UK 230 V
unless labelled 100–240 V). Check shelves: Shigezone (Radio Depart 1F) for
WS2812 matrices; Marutsu counter for ReSpeaker XVF3800 (¥9,149 warehouse).
Vstone Robot Center and Tsukumo Robot Kingdom are both closed.

## Borrow-from list (open source prior art)

- **[LeLamp](https://github.com/humancomputerlab/LeLamp)** — open-source
  expressive lamp robot explicitly based on Apple's ELEGNT paper: 5 axes,
  STS3215 servos + Pi, ~$260 BOM, GPL-3.0. **Closest existing project to
  ours** — review its mechanics and motion stack before CAD (license: we can
  study it freely; if we *derive* code/CAD from it, that portion is GPL).
- [SO-ARM100/101](https://github.com/TheRobotStudio/SO-ARM100) — servo
  configs, wiring, CAD for the STS3215 chain.
- [Luci](https://github.com/jochenalt/Luci) — older Pixar-lamp robot,
  mechanics reference.
- [Cornell ECE5725 Pixar Lamp](https://courses.ece.cornell.edu/ece5990/ECE5725_Fall2019_Projects/Dec_04_Demo/Pixar_Lamp/Website/index.html)
  — Pi-based Luxo social robot course project.
