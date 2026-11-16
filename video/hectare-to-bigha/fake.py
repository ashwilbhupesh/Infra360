FAKE = [((80, 322, 240, 346), "सीता पुत्री मोहन"), ((80, 370, 224, 394), "गीता पुत्र मोहन"), ((80, 418, 232, 442), "रमेश पुत्र मोहन"),
        ((140, 124, 215, 150), "उदाहरणपुर"), ((150, 158, 225, 186), "नमूना"), ((150, 190, 215, 216), "नमूना"), ((118, 222, 215, 248), "उदाहरण")]
ROWS = [(322, 238, 350, "1/2"), (370, 222, 336, "1/3"), (418, 230, 343, "1/6")]   # y0, hissa-x, caste-x, share  (1/2+1/3+1/6 = 1)
def fake_overlay(k, hl=False):
    o = []
    for (x0, y0, x1, y1), t in FAKE:
        o.append(f'<div class="fk" style="left:{x0 * k:.1f}px;top:{y0 * k:.1f}px;width:{(x1 - x0 + 4) * k:.1f}px;height:{(y1 - y0) * k:.1f}px;font-size:{19 * k:.1f}px">{t}</div>')
    for y0, hx, cs, sh in ROWS:
        o.append(f'<div class="fk" style="left:{(hx - 2) * k:.1f}px;top:{y0 * k:.1f}px;width:{(cs - 30 - hx + 2) * k:.1f}px;height:{24 * k:.1f}px;font-size:{19 * k:.1f}px">हिस्सा- {sh}</div>')
        o.append(f'<div class="fk" style="left:{(cs - 30) * k:.1f}px;top:{y0 * k:.1f}px;width:{217 * k:.1f}px;height:{24 * k:.1f}px;font-size:{19 * k:.1f}px">&nbsp;जाति- ----&nbsp;&nbsp;सा. देह खातेदार</div>')
        o.append(f'<div class="fk" style="left:{62 * k:.1f}px;top:{(y0 + 24) * k:.1f}px;width:{645 * k:.1f}px;height:{24 * k:.1f}px"></div>')
    o.append(f'<div class="fk" style="left:{55 * k:.1f}px;top:{466 * k:.1f}px;width:{670 * k:.1f}px;height:{148 * k:.1f}px"></div>')
    for b in [(160, 1215, 450, 1305), (500, 1215, 720, 1305), (110, 1360, 880, 1388), (150, 1428, 400, 1482)]:
        o.append(f'<div class="fk" style="left:{b[0] * k:.1f}px;top:{b[1] * k:.1f}px;width:{(b[2] - b[0]) * k:.1f}px;height:{(b[3] - b[1]) * k:.1f}px;font-size:{19 * k:.1f}px">------</div>')
    if hl:
        for i, (y0, hx, cs, sh) in enumerate(ROWS):
            o.append(f'<div class="hlb" id="hlb{i}" style="left:{(hx - 8) * k:.1f}px;top:{(y0 - 4) * k:.1f}px;width:{(cs - 30 - hx + 14) * k:.1f}px;height:{32 * k:.1f}px"></div>')
    o.append(f'<div class="wm" style="font-size:{150 * k:.0f}px">उदाहरण · SAMPLE</div>')
    return "".join(o)
