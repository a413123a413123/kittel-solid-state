# -*- coding: utf-8 -*-
"""網站 B：熱容專題整理。
   thermal.html 為導覽（C(T) 曲線 ＋ 溫區分組 ＋ 知識地圖），每主題一頁 th-NN.html。
   資料：data/topics.json（PDF 擷取＋校對）、data/topics_meta.json（我寫的物理意義）、
        data/chapters.json（公式）、data/curve.svg.html（Debye 曲線）。"""
import json, io, html, os, importlib.util

BASE = os.path.dirname(os.path.abspath(__file__))
L = lambda f: json.load(io.open(os.path.join(BASE, f), encoding='utf-8'))
T    = L('data/topics.json')
M    = L('data/topics_meta.json')
CH   = L('data/chapters.json')
CURVE = io.open(os.path.join(BASE, 'data/curve.svg.html'), encoding='utf-8').read()

spec = importlib.util.spec_from_file_location('a', os.path.join(BASE, 'build_a.py'))
A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)
shell, e = A.shell, A.e

ORDER = M['order']
ZONES = M['zones']
ZONE_SEQ = ['base', 'low', 'mid', 'high']

def eqs_for(key):
    """依 topics_meta 的 eq 選擇器，從 chapters.json 取公式（去重、保序）。"""
    got, seen = [], set()
    for chn, kw in M['topics'][key].get('eq', []):
        for q in CH[str(chn)]['equations']:
            sig = (chn, q['formula'])
            if sig in seen: continue
            if kw in q['label'] or kw in q['formula'] or kw in str(q.get('eqNumber', '')):
                seen.add(sig); got.append((chn, q)); break
    return got

def aspect(no, key, body, cls=''):
    c = (' ' + cls) if cls else ''
    return f'<section class="aspect{c}"><p class="aspect__k"><b>{no}</b>{e(key)}</p>{body}</section>'

def topic_page(key):
    t = T[key]; m = M['topics'][key]
    n = m['n']; zone = ZONES[m['zone']]
    idx = ORDER.index(key)
    b = [f'<div class="wrap"><p class="crumb"><a href="thermal.html">熱容專題</a> ／ 主題 {n}</p></div>',
         f'<header class="uhead wrap"><span class="uhead__no num">{n:02d}</span>'
         f'<h1>{e(m["name"])}</h1>'
         f'<p class="topic__zone">溫區定位：{e(zone["name"])}　·　{e(zone["hint"])}</p>'
         '</header>',
         '<main id="main" class="wrap--text">']

    # ① 物理意義與直觀解釋（我寫的）
    para = ''.join(f'<p>{ln}</p>' for ln in m['intuition'].split('\n\n') if ln.strip() and not ln.strip().startswith('|'))
    tbl = [ln for ln in m['intuition'].split('\n') if ln.strip().startswith('|')]
    if tbl:
        rows = [[c.strip() for c in ln.strip().strip('|').split('|')] for ln in tbl]
        rows = [r for r in rows if not all(set(c) <= set('-: ') for c in r)]
        head, body_r = rows[0], rows[1:]
        para += ('<div class="tablewrap"><table><thead><tr>'
                 + ''.join(f'<th>{h}</th>' for h in head) + '</tr></thead><tbody>'
                 + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in body_r)
                 + '</tbody></table></div>')
    b.append(aspect('①', '物理意義與直觀解釋　（我寫的教學說明）', para))

    # ② 重要公式與符號定義（書中）
    eqs = eqs_for(key)
    if eqs:
        blocks = ['<div class="eqs">']
        for chn, q in eqs:
            rt = ([e(q['eqNumber'])] if q.get('eqNumber') else []) + [f'Ch{chn} p.{q["bookPage"]}']
            blocks.append('<div class="eq">'
                          f'<p class="eq__l">{e(q["label"])}</p>'
                          f'<p class="eq__f">{e(q["formula"])}</p>'
                          f'<span class="eq__r">{" 　".join(rt)}</span>'
                          + (f'<p class="eq__s">{e(q["symbols"])}</p>' if q.get('symbols') else '') + '</div>')
        blocks.append('</div>')
        b.append(aspect('②', '重要公式與符號定義　（書中）', ''.join(blocks)))

    b.append(aspect('③', '推導所使用的假設　（書中）',
                    '<ul>' + ''.join(f'<li>{e(x)}</li>' for x in t['assumptions']) + '</ul>'))
    b.append(aspect('④', '適用條件與限制　（書中）',
                    '<ul>' + ''.join(f'<li>{e(x)}</li>' for x in t['validity']) + '</ul>', 'aspect--limit'))
    b.append(aspect('⑤', '高溫與低溫行為　（書中）',
                    f'<h4>高溫　T ≫ θ</h4><p>{e(t["highT"])}</p>'
                    f'<h4>低溫　T ≪ θ</h4><p>{e(t["lowT"])}</p>'))

    srcs = ''.join(f'<li>Ch{s["chapter"]}　{e(s["section"])}　p.{s["page"]}</li>' for s in t['sections'])
    vq = ('<div class="quote"><p class="quote__k">書中逐字</p>'
          + ''.join(f'<p>{e(x)}</p>' for x in t['verbatim']) + '</div>') if t.get('verbatim') else ''
    b.append(aspect('⑥', '對應的 Kittel 章節、小節與頁碼',
                    f'<ul class="srcs">{srcs}</ul>{vq}'))

    if t.get('notInBook', '').strip():
        b.append('<div class="ext"><span class="ext__k">【延伸知識】書中沒有處理的部分</span>'
                 f'<p>{e(t["notInBook"])}</p></div>')

    b.append('</main>')

    nav = ['<div class="wrap"><nav class="stepnav" aria-label="主題之間">']
    if idx > 0:
        pk = ORDER[idx-1]; pm = M['topics'][pk]
        nav.append(f'<a href="th-{pm["n"]:02d}.html"><span class="dir">← 上一主題</span>'
                   f'<span class="t"><span class="n num">{pm["n"]:02d}</span> {e(pm["name"])}</span></a>')
    else:
        nav.append('<a href="thermal.html"><span class="dir">← 回到</span><span class="t">熱容專題導覽</span></a>')
    if idx < len(ORDER)-1:
        nk = ORDER[idx+1]; nm = M['topics'][nk]
        nav.append(f'<a href="th-{nm["n"]:02d}.html"><span class="dir">下一主題 →</span>'
                   f'<span class="t"><span class="n num">{nm["n"]:02d}</span> {e(nm["name"])}</span></a>')
    else:
        nav.append('<a href="thermal.html"><span class="dir">回到 →</span><span class="t">熱容知識地圖</span></a>')
    nav.append('</nav></div>')
    b.append('\n'.join(nav))

    return shell(f'{m["name"]} — Kittel 熱容專題',
                 f'Kittel 第 8 版的熱容專題：{m["name"]}。物理意義、公式與符號定義、推導假設、適用條件與限制、高低溫行為，以及對應的章節小節與頁碼。',
                 '\n'.join(b), current='thermal')

def zone_chips(zk):
    z = ZONES[zk]
    lis = ''.join(
        f'<li><a href="th-{M["topics"][k]["n"]:02d}.html">'
        f'<span class="n">{M["topics"][k]["n"]:02d}</span>{e(M["topics"][k]["name"])}</a></li>'
        for k in z['keys'])
    return f'<div class="zone"><p class="zone__t">{e(z["name"])}　·　{e(z["hint"])}</p><ul>{lis}</ul></div>'

def thermal_index():
    n_eq = sum(len(eqs_for(k)) for k in ORDER)
    n_src = sum(len(T[k]['sections']) for k in ORDER)
    chs = sorted({s['chapter'] for k in ORDER for s in T[k]['sections']})

    rows = ''.join(
        f'<tr><td class="mono">{M["topics"][k]["n"]:02d}</td>'
        f'<td><a href="th-{M["topics"][k]["n"]:02d}.html"><b>{e(M["topics"][k]["name"])}</b></a></td>'
        f'<td>{e(ZONES[M["topics"][k]["zone"]]["name"])}</td>'
        f'<td class="mono">{"、".join("Ch%d" % c for c in sorted({s["chapter"] for s in T[k]["sections"]}))}</td>'
        f'<td class="mono">{len(T[k]["assumptions"])} / {len(T[k]["validity"])}</td></tr>'
        for k in ORDER)

    b = f"""<main id="main">
  <header class="hero">
    <div class="wrap">
      <p class="kicker">從 Dulong–Petit 到 Debye T³</p>
      <h1>熱容，一條溫度軸</h1>
      <p class="hero__lede">11 個主題、每個六個固定面向：物理意義與直觀解釋／重要公式與符號定義／推導所使用的假設／適用條件與限制／高溫與低溫行為／對應的 Kittel 章節小節與頁碼。</p>
      <p class="hero__claim">熱容不是 Ch5 一章的事——它散在 {len(chs)} 章裡。</p>
      <p class="anchors__cap">這份專題的實際規模</p>
      <ul class="anchors">
        <li><span class="v num">11</span><span class="k">個主題，各六個固定面向</span></li>
        <li><span class="v num">{n_src}</span><span class="k">筆章節小節出處，逐筆核對頁碼</span></li>
        <li><span class="v num">{len(chs)}</span><span class="k">章：{"、".join("Ch%d" % c for c in chs)}</span></li>
      </ul>
    </div>
  </header>

  <section class="plate">
    <div class="wrap">
      <h2 style="margin-top:0">溫度軸上的 11 個主題</h2>
      <p style="max-width:38em">熱容的主題不是平行的分類——它們各自活在 C(T) 曲線的不同區段。下圖的曲線由 Debye 積分實際取樣繪出，不是示意圖。</p>
      {CURVE}
      <div class="zones">
        {zone_chips('low')}
        {zone_chips('mid')}
        {zone_chips('high')}
      </div>
      <div class="zone zone--base">
        <p class="zone__t">{e(ZONES['base']['name'])}　·　{e(ZONES['base']['hint'])}</p>
        <ul>{''.join(f'<li><a href="th-{M["topics"][k]["n"]:02d}.html"><span class="n">{M["topics"][k]["n"]:02d}</span>{e(M["topics"][k]["name"])}</a></li>' for k in ZONES['base']['keys'])}</ul>
      </div>
    </div>
  </section>

  <section class="sect wrap">
    <h2>主題總表</h2>
    <div class="tablewrap">
      <table>
        <thead><tr><th>#</th><th>主題</th><th>溫區</th><th>出處章</th><th>假設 / 限制</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
  </section>

  <section class="plate">
    <div class="wrap">
      <h2 style="margin-top:0">Kittel 熱容知識地圖</h2>
      <p style="max-width:38em">各章的概念如何串成一套完整的固體熱容理論。三條路徑最後在「低溫總熱容 C = γT + AT³」與「熱導率 k = ⅓C v Λ」兩處合流。</p>
      <div class="mapgrid">
        <div class="maplane">
          <h3>主線：晶格</h3>
          <ol>
            <li><b>Ch1–2</b> 晶格與倒晶格 → 給出原胞數 N/V 與第一 Brillouin 區（模式計數的定義域）</li>
            <li><b>Ch3</b> 彈性常數 → 給出聲速 v（Debye 模型與 k=⅓CvΛ 都要它）</li>
            <li><b>Ch4</b> 色散關係 ω(K)、聲學支與光學支</li>
            <li><b>Ch5</b> 態密度 D(ω) ＋ Planck 分佈 → <b>晶格熱容 C_lat</b></li>
            <li>兩個簡化：<b>Einstein</b>（單一頻率，近似光學支）與 <b>Debye</b>（ω=vK，近似聲學支）→ 高溫 Dulong–Petit、低溫 T³</li>
          </ol>
        </div>
        <div class="maplane">
          <h3>支線：其他自由度</h3>
          <ol>
            <li><b>Ch6</b> 費米氣 ＋ Pauli 原理 → <b>電子熱容 γT</b>（只有費米面附近能響應）</li>
            <li><b>Ch12</b> 磁振子色散 ω∝K² → <b>磁性熱容 ∝ T³ᐟ²</b></li>
            <li><b>Ch19</b> 非晶的二能階系統 → <b>TLS 線性項</b>（與電子項同冪次但無關）</li>
            <li><b>Ch10</b> 超導能隙 → 相變處的<b>熱容跳變</b>與指數衰減</li>
            <li><b>Ch18</b> 奈米結構：受限方向的模式在室溫仍被熱激發</li>
          </ol>
        </div>
        <div class="maplane">
          <h3>修正與橋接</h3>
          <ol>
            <li><b>Ch5 非諧性</b> → 熱膨脹、聲子互撞（簡諧近似下兩者都不存在）</li>
            <li>非諧性 → <b>C_p − C_v = 9α²BVT</b>（p.107 註腳）：理論算 C_v、實驗量 C_p</li>
            <li>非諧性 → 有限的平均自由徑 Λ → <b>熱導率 k = ⅓ C v Λ</b>（p.122 式 42）</li>
            <li>這條式子是全書唯一把<b>儲存</b>（C）與<b>輸運</b>（v、Λ）接起來的橋</li>
            <li><b>【延伸知識】</b>再往前是元件層級的 Cth 與 Rth、以及熱阻抗網路——<b>Kittel 全書皆無</b></li>
          </ol>
        </div>
      </div>
    </div>
  </section>

  <section class="sect wrap--text">
    <h2>姊妹頁：全書逐章</h2>
    <p>本頁按熱容這條主線走，跨章串接。若你要的是「這一章在講什麼」的定位，請看 <a href="index.html">全書逐章整理</a>：22 章每章六欄，199 條公式全部標到書本頁碼與式號。</p>
  </section>
</main>"""
    return shell('熱容專題整理 — Kittel 固態物理',
                 f'Kittel 第 8 版的熱容專題：11 個主題沿 C(T) 溫度軸排列，每主題六個固定面向，跨 {len(chs)} 章，附熱容知識地圖。', b, current='thermal')

def build():
    io.open(os.path.join(BASE, 'thermal.html'), 'w', encoding='utf-8', newline='').write(thermal_index())
    for k in ORDER:
        n = M['topics'][k]['n']
        io.open(os.path.join(BASE, f'th-{n:02d}.html'), 'w', encoding='utf-8', newline='').write(topic_page(k))
    n_eq = sum(len(eqs_for(k)) for k in ORDER)
    n_as = sum(len(T[k]['assumptions']) for k in ORDER)
    n_va = sum(len(T[k]['validity']) for k in ORDER)
    print(f'已生成 thermal.html ＋ 11 個主題頁｜公式 {n_eq} 條｜假設 {n_as} 條｜限制 {n_va} 條')

if __name__ == '__main__':
    build()
