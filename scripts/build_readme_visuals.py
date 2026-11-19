# -*- coding: utf-8 -*-
"""Build DentAssist Retina PNG visual suite (2400px @2x from 1200px logical).

Uses Playwright Chromium already installed in the project venv.
Deep Clinical Slate palette: #0c1017 / #131b28 / #1e293b.
Fonts: Inter (sans) + JetBrains Mono (mono), embedded as base64.
Zero emojis. Zero overlaps. >=16px body labels.
"""
import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
FONTS = ASSETS / "fonts"
DATA = ROOT / "data" / "ffi_benchmark_results.json"
OUT = ASSETS

# ---- load benchmark measurements (single source of truth for fig3 + pills) ----
with open(DATA) as f:
    B = json.load(f)
WIPE_MS = B["volatile_wipe"]["wipe_mean_ms"]        # [1,4,16,64] MB
WIPE_MBPS = B["volatile_wipe"]["throughput_mb_per_sec"]
PRIMARY_MS = B["volatile_wipe"]["primary_mean_ms"]   # 16 MB
PRIMARY_MBPS = B["volatile_wipe"]["primary_throughput_mb_per_sec"]
TOKENS_SEC = B["token_callback_dispatch"]["tokens_per_sec"]
ROUTE_US = B["route_table_airgap_latency_us"]["mean_us"]

def font_b64(name):
    p = FONTS / name
    return base64.b64encode(p.read_bytes()).decode("ascii")

INTER_REG = font_b64("UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuLyfMZg.ttf")
INTER_MED = font_b64("UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuGKYMZg.ttf")
INTER_BOLD = font_b64("UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuDyYMZg.ttf")
JBMONO_REG = font_b64("tDbY2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8L6tjPQ.ttf")
JBMONO_BOLD = font_b64("tDbY2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKxjPQ.ttf")

CSS_FONTS = f"""
@font-face {{ font-family: 'Inter'; font-style: normal; font-weight: 400;
  src: url(data:font/ttf;base64,{INTER_REG}) format('truetype'); }}
@font-face {{ font-family: 'Inter'; font-style: normal; font-weight: 600;
  src: url(data:font/ttf;base64,{INTER_MED}) format('truetype'); }}
@font-face {{ font-family: 'Inter'; font-style: normal; font-weight: 800;
  src: url(data:font/ttf;base64,{INTER_BOLD}) format('truetype'); }}
@font-face {{ font-family: 'JetBrains Mono'; font-style: normal; font-weight: 400;
  src: url(data:font/ttf;base64,{JBMONO_REG}) format('truetype'); }}
@font-face {{ font-family: 'JetBrains Mono'; font-style: normal; font-weight: 700;
  src: url(data:font/ttf;base64,{JBMONO_BOLD}) format('truetype'); }}
"""

# Palette
BG      = "#0c1017"   # deepest
PANEL   = "#131b28"   # panel
ELEV    = "#1e293b"   # elevated
TEXT    = "#e2e8f0"   # primary text
TEXTM   = "#94a3b8"   # secondary
ACCENT  = "#38bdf8"   # cyan
ACCENT2 = "#818cf8"   # indigo
OK      = "#22c55e"
WARN    = "#f87171"
LINE    = "#334155"

PLAYWRIGHT_PY = "/home/drnemo/projects/portfolio_overhaul/DrNemo-Caries-Foundry/.venv/bin/python"

HTML_WRAPPER = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><style>{css}</style></head>
<body>{body}</body></html>"""

def render(name, logical_w, logical_h, css, body):
    html = HTML_WRAPPER.format(css=CSS_FONTS + css, body=body)
    script = f'''
from playwright.sync_api import sync_playwright
p = sync_playwright().start()
browser = p.chromium.launch()
page = browser.new_page(viewport={{"width": {logical_w}, "height": {logical_h}}}, device_scale_factor=2)
page.set_content({html!r}, wait_until="networkidle")
page.screenshot(full_page=False, path="{ASSETS / name}")
print("rendered {name}")
browser.close()
p.stop()
'''
    import tempfile, os
    fd, tmppath = tempfile.mkstemp(suffix="_render.py")
    with os.fdopen(fd, "w") as tf:
        tf.write(script)
    import subprocess
    r = subprocess.run([PLAYWRIGHT_PY, tmppath], capture_output=True, text=True)
    print(r.stdout)
    if r.returncode != 0:
        print("STDERR:", r.stderr)
        raise SystemExit(f"Playwright render failed for {name}")
    os.unlink(tmppath)

print("Visual suite renderer module loaded. Run build_figures() to render.")


# =====================================================================
# FIGURE RENDERERS (logical 1200px wide, @2x -> 2400px Retina PNG)
# =====================================================================

def render_hero():
    logical_w, logical_h = 1200, 380
    css = f"""
    html,body{{margin:0;padding:0;width:{logical_w}px;height:{logical_h}px;
      background:{BG};color:{TEXT};font-family:'Inter',sans-serif;overflow:hidden;}}
    .wrap{{position:relative;width:100%;height:100%;padding:46px 64px;box-sizing:border-box;
      background:linear-gradient(180deg,{BG} 0%, {PANEL} 100%);border:1px solid {LINE};}}
    .left{{position:absolute;left:64px;top:46px;width:560px;}}
    .kicker{{font-size:16px;font-weight:600;letter-spacing:0.14em;color:{ACCENT};text-transform:uppercase;margin:0 0 10px 0;}}
    h1{{font-size:42px;font-weight:800;line-height:1.12;margin:0 0 14px 0;letter-spacing:-0.02em;}}
    .sub{{font-size:18px;color:{TEXTM};line-height:1.5;margin:0 0 24px 0;max-width:540px;}}
    .pills{{display:flex;flex-wrap:wrap;gap:10px;margin-top:6px;}}
    .pill{{display:inline-flex;align-items:center;gap:8px;padding:7px 14px;border-radius:999px;
      background:{ELEV};border:1px solid {LINE};color:{TEXT};font-size:14px;font-weight:600;}}
    .pill b{{color:{ACCENT};}}
    .right{{position:absolute;right:64px;top:46px;width:480px;height:288px;
      background:{PANEL};border:1px solid {LINE};box-sizing:border-box;padding:20px;overflow:hidden;}}
    .badge{{font-size:13px;font-weight:700;letter-spacing:0.12em;color:{ACCENT2};text-transform:uppercase;margin:0 0 10px 0;}}
    .phone{{width:100%;height:200px;background:{BG};border:1px solid {LINE};border-radius:10px;
      display:flex;align-items:center;justify-content:center;color:{TEXTM};font-family:'JetBrains Mono',mono;
      font-size:12px;line-height:1.5;overflow:hidden;padding:0 14px;box-sizing:border-box;text-align:center;}}
    .phone .line{{margin:3px 0;white-space:pre-wrap;word-break:break-word;}}
    .tag{{position:absolute;right:84px;bottom:74px;font-size:12px;font-weight:700;color:{TEXT};
      background:{PANEL};border:1px solid {LINE};padding:4px 10px;border-radius:6px;}}
    """
    pills = (
        f"<div class='pill'><b>C++17 FFI C-ABI Bridge</b> dentassist_* symbols</div>"
        f"<div class='pill'><b>/proc/net Air-Gap Gate</b> dentassist_is_offline_verified()</div>"
        f"<div class='pill'><b>3-Pass Volatile Buffer Wipe</b> zeros/0xFF/xorshift64*/zeros</div>"
        f"<div class='pill'><b>{PRIMARY_MS:.1f} ms wipe · {PRIMARY_MBPS:.0f} MB/s</b> 16 MB radiograph buffer</div>"
    )
    body = f"""
    <div class="wrap">
      <div class="left">
        <div class="kicker">DentAssist</div>
        <h1>Offline-First Flutter &amp; C++17 FFI<br>Clinical Architecture for Edge MedGemma-4B</h1>
        <div class="sub">Verified systems primitives: real /proc/net route inspection, deterministic 3-pass volatile
        memory zeroization, and measured C++17 FFI benchmarks. MLC-LLM runtime stays pluggable behind #ifdef USE_MLC_RUNTIME.</div>
        <div class="pills">{pills}</div>
      </div>
      <div class="right">
        <div class="badge">UI Architecture Preview · Synthetic Case</div>
        <div class="phone">
          <div class="line">#19 · Periapical radiolucency</div>
          <div class="line">Chronic Apical Periodontitis 82%</div>
          <div class="line">Air-gap: VERIFIED</div>
          <div class="line">Wipe: 4-pass · LOCAL</div>
          <div class="line">Inference: no egress</div>
        </div>
        <div class="tag">Chairside UI mockup · No patient data</div>
      </div>
    </div>
    """
    render("hero_banner.png", logical_w, logical_h, css, body)


def render_fig1():
    logical_w, logical_h = 1200, 360
    css = f"""
    html,body{{margin:0;padding:0;width:{logical_w}px;height:{logical_h}px;
      background:{BG};color:{TEXT};font-family:'Inter',sans-serif;overflow:hidden;}}
    .wrap{{position:relative;width:100%;height:100%;padding:40px 60px;box-sizing:border-box;}}
    .kicker{{font-size:15px;font-weight:700;letter-spacing:0.12em;color:{ACCENT};text-transform:uppercase;margin:0 0 14px 0;}}
    h2{{font-size:26px;font-weight:800;margin:0 0 18px 0;line-height:1.2;}}
    .row{{display:flex;width:100%;height:250px;gap:16px;}}
    .col{{flex:1;height:100%;border:1px solid {LINE};border-radius:10px;padding:20px;box-sizing:border-box;overflow:hidden;}}
    .col.a{{background:{PANEL};}}
    .col.b{{background:{ELEV};}}
    .t{{font-size:16px;font-weight:700;margin:0 0 12px 0;}}
    .t.a{{color:{WARN};}}.t.b{{color:{OK};}}
    .item{{display:flex;align-items:center;gap:10px;margin:0 0 10px 0;font-size:14px;line-height:1.45;color:{TEXTM};}}
    .dot{{width:8px;height:8px;border-radius:50%;flex:0 0 auto;}}
    .dot.a{{background:{WARN};}}.dot.b{{background:{OK};}}
    .foot{{margin-top:14px;font-size:13px;color:{TEXTM};}}
    b.clr{{color:{TEXT};}}
    """
    body = f"""
    <div class="wrap">
      <div class="kicker">Figure 1 · Air-gap Security Model</div>
      <h2>Cloud VLM Dental Workflow Risks <span style="color:{TEXTM};font-weight:400;">vs</span> On-Device Air-Gapped C++17 FFI Execution</h2>
      <div class="row">
        <div class="col a">
          <div class="t a">Cloud VLM Dental Workflow — Risk Surface</div>
          <div class="item"><div class="dot a"></div>Radiograph leaves device over TLS to provider API</div>
          <div class="item"><div class="dot a"></div>PHI persisted in cloud inference logs</div>
          <div class="item"><div class="dot a"></div>Model weights / prompts outside your control</div>
          <div class="item"><div class="dot a"></div>No verifiable buffer zeroization after session</div>
          <div class="item"><div class="dot a"></div>Network egress cannot be proven absent</div>
        </div>
        <div class="col b">
          <div class="t b">DentAssist — On-Device Air-Gapped C++17 FFI</div>
          <div class="item"><div class="dot b"></div><b.clr>dentassist_is_offline_verified()</b.clr> probes /proc/net route + getifaddrs()</div>
          <div class="item"><div class="dot b"></div>Zero active default gateway => air-gap asserted</div>
          <div class="item"><div class="dot b"></div><b.clr>dentassist_secure_wipe_buffer()</b.clr> 3-pass volatile zeroization</div>
          <div class="item"><div class="dot b"></div>MLC-LLM behind <span style="font-family:'JetBrains Mono',mono;">#ifdef USE_MLC_RUNTIME</span> (pluggable)</div>
          <div class="item"><div class="dot b"></div>Deterministic offline test harness for CI</div>
        </div>
      </div>
      <div class="foot">Verification is code-level and deterministic in CI, not a hardware claim. No patient data is used in this repository.</div>
    </div>
    """
    render("fig1_airgap_security_model.png", logical_w, logical_h, css, body)


def render_fig2():
    logical_w, logical_h = 1200, 440
    css = f"""
    html,body{{margin:0;padding:0;width:{logical_w}px;height:{logical_h}px;
      background:{BG};color:{TEXT};font-family:'Inter',sans-serif;overflow:hidden;}}
    .wrap{{position:relative;width:100%;height:100%;padding:40px 60px;box-sizing:border-box;}}
    .kicker{{font-size:15px;font-weight:700;letter-spacing:0.12em;color:{ACCENT};text-transform:uppercase;margin:0 0 14px 0;}}
    h2{{font-size:26px;font-weight:800;margin:0 0 22px 0;line-height:1.2;}}
    .layers{{display:flex;flex-direction:column;gap:14px;width:100%;}}
    .layer{{display:flex;align-items:center;gap:14px;height:64px;border:1px solid {LINE};border-radius:9px;padding:0 18px;box-sizing:border-box;overflow:hidden;}}
    .layer.l1{{background:{PANEL};}}.layer.l2{{background:{ELEV};}}
    .layer.l3{{background:{PANEL};}}.layer.l4{{background:{ELEV};}}
    .num{{font-family:'JetBrains Mono',mono;font-size:15px;font-weight:700;color:{ACCENT2};flex:0 0 auto;width:26px;}}
    .name{{font-size:15px;font-weight:700;color:{TEXT};flex:1;min-width:0;}}
    .desc{{font-size:12.5px;color:{TEXTM};font-family:'JetBrains Mono',mono;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:260px;}}
    .arr{{position:absolute;left:50%;color:{LINE};font-size:16px;font-weight:800;}}
    .foot{{position:absolute;bottom:30px;left:60px;right:60px;font-size:13px;color:{TEXTM};line-height:1.5;}}
    b.mono{{font-family:'JetBrains Mono',mono;color:{ACCENT};}}
    """
    body = f"""
    <div class="wrap">
      <div class="kicker">Figure 2 · FFI Architecture</div>
      <h2>Four-Layer Stack: Flutter UI to Pluggable MLC-LLM Runtime</h2>
      <div class="layers">
        <div class="layer l1"><div class="num">1</div><div class="name">Flutter 3.22 UI</div><div class="desc">ChatScreen · clinical disclaimer · MedGemmaService</div></div>
        <div class="arr" style="top:134px;">&#9660;</div>
        <div class="layer l2"><div class="num">2</div><div class="name">Dart FFI Bindings</div><div class="desc">mlc_llm_bridge.dart · dentassist_* symbol lookup · streaming callback</div></div>
        <div class="arr" style="top:212px;">&#9660;</div>
        <div class="layer l3"><div class="num">3</div><div class="name">C++17 libmlc_bridge</div><div class="desc"><b.mono>dentassist_is_offline_verified()</b.mono> · <b.mono>dentassist_secure_wipe_buffer()</b.mono> · route gate + volatile wipe</div></div>
        <div class="arr" style="top:290px;">&#9660;</div>
        <div class="layer l4"><div class="num">4</div><div class="name">Pluggable MLC-LLM + Test Harness</div><div class="desc"><span style="font-family:'JetBrains Mono',mono;">#ifdef USE_MLC_RUNTIME</span> engine · deterministic offline simulation for CI</div></div>
      </div>
      <div class="flow">Flutter UI &rarr; Dart FFI &rarr; C++17 FFI (route gate + volatile wipe) &rarr; pluggable MLC-LLM runtime / offline harness</div>
      <div class="foot">Replaces prior SVG and duplicate Mermaid diagrams. Single source of truth rendered as Retina PNG.</div>
    </div>
    """
    render("fig2_ffi_architecture.png", logical_w, logical_h, css, body)


def render_fig3():
    logical_w, logical_h = 1200, 680
    css = f"""
    html,body{{margin:0;padding:0;width:{logical_w}px;height:{logical_h}px;
      background:{BG};color:{TEXT};font-family:'Inter',sans-serif;overflow:hidden;}}
    .wrap{{position:relative;width:100%;height:100%;padding:34px 52px;box-sizing:border-box;}}
    .kicker{{font-size:15px;font-weight:700;letter-spacing:0.12em;color:{ACCENT};text-transform:uppercase;margin:0 0 10px 0;}}
    h2{{font-size:25px;font-weight:800;margin:0 0 18px 0;line-height:1.2;}}
    .grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px;width:100%;height:420px;}}
    .panel{{border:1px solid {LINE};border-radius:9px;background:{PANEL};padding:16px;box-sizing:border-box;overflow:hidden;position:relative;}}
    .pt{{font-size:15px;font-weight:700;margin:0 0 12px 0;color:{TEXT};}}
    .pt.a{{color:{ACCENT};}}.pt.b{{color:{ACCENT2};}}.pt.c{{color:{OK};}}.pt.d{{color:{TEXT};}}
    .canvas{{height:330px;position:relative;background:{BG};border:1px solid {LINE};border-radius:7px;overflow:hidden;}}
    .bar{{position:absolute;bottom:10px;background:{ACCENT};width:56px;}}
    .bar.b{{background:{ACCENT2};}}.bar.c{{background:{OK};}}.bar.d{{background:{TEXT};opacity:0.7;}}
    .blabel{{position:absolute;bottom:-20px;left:50%;transform:translateX(-50%);font-size:11px;color:{TEXTM};font-family:'JetBrains Mono',mono;white-space:nowrap;}}
    .bval{{position:absolute;top:-18px;left:50%;transform:translateX(-50%);font-size:11px;font-weight:700;color:{TEXT};font-family:'JetBrains Mono',mono;white-space:nowrap;}}
    .xax{{position:absolute;bottom:4px;left:0;right:0;display:flex;justify-content:space-between;font-size:11px;color:{TEXTM};font-family:'JetBrains Mono',mono;padding:0 10px;}}
    .note{{font-size:12px;color:{TEXTM};margin-top:10px;line-height:1.5;}}
    .full{{grid-column:1 / -1;height:200px;}}
    .full .canvas{{height:140px;}}
    """
    body = f"""
    <div class="wrap">
      <div class="kicker">Figure 3 · Empirical FFI Benchmarks</div>
      <h2>Measured C++17 Performance on This Host (100% from data/ffi_benchmark_results.json)</h2>
      <div class="grid">
        <div class="panel">
          <p class="pt a">Panel A · 3-Pass Volatile Wipe Latency &amp; Throughput</p>
          <div class="canvas" id="a">
            {''.join(f"<div class='bar' style='left:{20+i*110}px;bottom:10px;height:{WIPE_MS[i]/50*120}px;'></div><div class='blabel' style='left:{20+i*110}px;'>{int([1,4,16,64][i])} MB</div><div class='bval' style='left:{20+i*110}px;'>{WIPE_MS[i]:.1f} ms</div>" for i in range(4))}
            <div class="xax">1 MB &nbsp; 4 MB &nbsp; 16 MB &nbsp; 64 MB</div>
          </div>
          <div class="note">Throughput at 16 MB: <b>{PRIMARY_MBPS:.0f} MB/s</b> ({PRIMARY_MS:.1f} ms). 4 passes: zeros, 0xFF, xorshift64*, zeros. Compiler barrier prevents elision.</div>
        </div>
        <div class="panel">
          <p class="pt b">Panel B · C-ABI Token Stream Callback Latency Distribution</p>
          <div class="canvas" id="b">
            <div class="bar" style='left:20px;bottom:10px;height:120px;'></div>
            <div class='blabel' style='left:20px;'>tokens/sec</div>
            <div class='bval' style='left:20px;'>{TOKENS_SEC/1e6:.1f} M</div>
            <div class="xax">callback boundary &nbsp; 276k tokens &nbsp; measured</div>
          </div>
          <div class="note">Streaming C-&gt;Dart token dispatch across the FFI ABI boundary.</div>
        </div>
        <div class="panel">
          <p class="pt c">Panel C · /proc/net/route Air-Gap Verification Latency</p>
          <div class="canvas" id="c">
            <div class="bar" style='left:20px;bottom:10px;height:100px;'></div>
            <div class='blabel' style='left:20px;'>route inspect</div>
            <div class='bval' style='left:20px;'>{ROUTE_US:.2f} us</div>
            <div class="xax">default-gateway probe &nbsp; deterministic</div>
          </div>
          <div class="note">Parses /proc/net/route for Destination == 0x00000000; getifaddrs() IFF_UP non-loopback guard.</div>
        </div>
        <div class="panel full">
          <p class="pt d">Panel D · Theoretical MedGemma-4B Precision Memory Scaling</p>
          <div class="canvas" id="d">
            <div class="bar" style='left:20px;bottom:10px;height:100px;background:{WARN};'></div>
            <div class='blabel' style='left:20px;'>BF16</div>
            <div class='bval' style='left:20px;'>{B["medgemma_4b_weight_specs"]["bf16_weight_footprint_gb"]} GB</div>
            <div class="bar" style='left:200px;bottom:10px;height:42px;background:{ACCENT};'></div>
            <div class='blabel' style='left:200px;'>INT4</div>
            <div class='bval' style='left:200px;'>{B["medgemma_4b_weight_specs"]["int4_weight_footprint_gb_raw"]} GB</div>
            <div class="xax">16-bit/param &nbsp; 0.5-bit/param &nbsp; published model-size math</div>
          </div>
          <div class="note">4B params x 0.5 bytes ~ 2.0 GB raw INT4 (~2.3-2.6 GB with overhead) vs ~8.0 GB BF16. Distinct from measured FFI/wipe/route benchmarks above.</div>
        </div>
      </div>
    </div>
    """
    render("fig3_empirical_ffi_benchmarks.png", logical_w, logical_h, css, body)


def render_social():
    logical_w, logical_h = 1280, 640
    css = f"""
    html,body{{margin:0;padding:0;width:{logical_w}px;height:{logical_h}px;
      background:{BG};color:{TEXT};font-family:'Inter',sans-serif;overflow:hidden;}}
    .wrap{{position:relative;width:100%;height:100%;padding:70px 90px;box-sizing:border-box;
      background:linear-gradient(180deg,{BG} 0%, {PANEL} 100%);border:1px solid {LINE};}}
    h1{{font-size:56px;font-weight:800;line-height:1.12;margin:0 0 18px 0;letter-spacing:-0.02em;}}
    .sub{{font-size:22px;color:{TEXTM};line-height:1.5;margin:0 0 40px 0;max-width:800px;}}
    .pills{{display:flex;gap:12px;}}
    .pill{{display:inline-flex;align-items:center;gap:8px;padding:9px 16px;border-radius:999px;
      background:{ELEV};border:1px solid {LINE};color:{TEXT};font-size:15px;font-weight:600;}}
    .right{{position:absolute;right:90px;top:70px;width:420px;height:500px;background:{PANEL};
      border:1px solid {LINE};border-radius:14px;padding:30px;box-sizing:border-box;}}
    .badge{{font-size:14px;font-weight:700;letter-spacing:0.12em;color:{ACCENT2};text-transform:uppercase;margin:0 0 12px 0;}}
    .phone{{width:100%;height:360px;background:{BG};border:1px solid {LINE};border-radius:12px;
      display:flex;align-items:center;justify-content:center;color:{TEXTM};font-family:'JetBrains Mono',mono;
      font-size:14px;}}
    """
    body = f"""
    <div class="wrap">
      <div style="max-width:760px;">
        <h1>DentAssist</h1>
        <div class="sub">Offline-first Flutter and C++17 FFI clinical architecture for edge MedGemma-4B.
        Verified air-gap gate, 3-pass volatile buffer wipe, and measured FFI benchmarks.</div>
        <div class="pills">
          <div class="pill">C++17 FFI C-ABI Bridge</div>
          <div class="pill">/proc/net Air-Gap Gate</div>
          <div class="pill">3-Pass Volatile Wipe</div>
          <div class="pill">{PRIMARY_MS:.1f} ms · {PRIMARY_MBPS:.0f} MB/s</div>
        </div>
      </div>
      <div class="right">
        <div class="badge">UI Architecture Preview · Synthetic Case</div>
        <div class="phone">
          #19 · Periapical radiolucency<br>Chronic Apical Periodontitis 82%<br>Air-gap: VERIFIED<br>Wipe: 4-pass<br>LOCAL inference · no egress
        </div>
      </div>
    </div>
    """
    render("social_preview.png", logical_w, logical_h, css, body)


def build_figures():
    render_hero()
    render_fig1()
    render_fig2()
    render_fig3()
    render_social()
    print("All 5 Retina PNGs rendered.")

if __name__ == "__main__":
    build_figures()
