# -*- coding: utf-8 -*-
"""網站 A：全書逐章整理。
   index.html 為總覽（22 格刻度尺＋總表），每章各自一頁 ch-NN.html。
   資料來源：data/chapters.json（PDF 擷取＋獨立校對）與 data/relations.json（我的判讀）。"""
import json, io, html, os

BASE = os.path.dirname(os.path.abspath(__file__))
CH  = json.load(io.open(os.path.join(BASE, 'data/chapters.json'), encoding='utf-8'))
REL = json.load(io.open(os.path.join(BASE, 'data/relations.json'), encoding='utf-8'))

META = {
 1:("Crystal Structure","晶體結構","1–22"),
 2:("Wave Diffraction and the Reciprocal Lattice","波繞射與倒晶格","23–45"),
 3:("Crystal Binding and Elastic Constants","晶體鍵結與彈性常數","47–87"),
 4:("Phonons I. Crystal Vibrations","聲子 I：晶格振動","89–103"),
 5:("Phonons II. Thermal Properties","聲子 II：熱性質","105–129"),
 6:("Free Electron Fermi Gas","自由電子費米氣","131–158"),
 7:("Energy Bands","能帶","161–183"),
 8:("Semiconductor Crystals","半導體晶體","185–219"),
 9:("Fermi Surfaces and Metals","費米面與金屬","221–255"),
 10:("Superconductivity","超導","257–296"),
 11:("Diamagnetism and Paramagnetism","反磁性與順磁性","297–319"),
 12:("Ferromagnetism and Antiferromagnetism","鐵磁性與反鐵磁性","321–359"),
 13:("Magnetic Resonance","磁共振","361–391"),
 14:("Plasmons, Polaritons, and Polarons","電漿子、極化子與極子","393–425"),
 15:("Optical Processes and Excitons","光學過程與激子","427–451"),
 16:("Dielectrics and Ferroelectrics","介電體與鐵電體","453–485"),
 17:("Surface and Interface Physics","表面與界面物理","487–513"),
 18:("Nanostructures","奈米結構","515–563"),
 19:("Noncrystalline Solids","非晶固體","565–582"),
 20:("Point Defects","點缺陷","583–595"),
 21:("Dislocations","差排","597–618"),
 22:("Alloys","合金","619–640"),
}

APPX = [
 ("A","Temperature Dependence of the Reflection Lines","反射線的溫度相依",641,0),
 ("B","Ewald Calculation of Lattice Sums","Ewald 晶格和計算",644,0),
 ("C","Quantization of Elastic Waves: Phonons","彈性波的量子化：聲子",648,1),
 ("D","Fermi-Dirac Distribution Function","費米–狄拉克分布函數",652,1),
 ("E","Derivation of the dk/dt Equation","dk/dt 方程的推導",655,0),
 ("F","Boltzmann Transport Equation","波茲曼輸運方程",656,1),
 ("G","Vector Potential, Field Momentum, and Gauge Transformations","向量位、場動量與規範變換",661,0),
 ("H","Cooper Pairs","Cooper 對",665,0),
 ("I","Ginzburg-Landau Equation","Ginzburg–Landau 方程",667,0),
 ("J","Electron-Phonon Collisions","電子—聲子碰撞",671,0),
]

GRADE = {"direct":("直接","tag--direct","g-direct"),
         "indirect":("間接","tag--indirect","g-indirect"),
         "none":("無明顯關聯","tag--none","g-none")}

e = lambda s: html.escape(str(s), quote=False)
FAVICON = ("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'>"
           "<rect width='32' height='32' fill='%23F0F1F5'/><rect x='5' y='7' width='4' height='18' fill='%233F4FA8'/>"
           "<rect x='11' y='11' width='4' height='14' fill='%233F4FA8'/><rect x='17' y='5' width='4' height='20' fill='%23B4541F'/>"
           "<rect x='23' y='15' width='4' height='10' fill='%233F4FA8'/></svg>")
THEME_JS = ("(function(){var r=document.documentElement,k='kittel-theme',s=null;try{s=localStorage.getItem(k)}catch(e){}\n"
            "if(s){r.setAttribute('data-theme',s)}\n"
            "document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('[data-toggle-theme]');if(!b)return;\n"
            "var cur=r.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');\n"
            "var n=cur==='dark'?'light':'dark';r.setAttribute('data-theme',n);try{localStorage.setItem(k,n)}catch(e){}\n"
            "b.setAttribute('aria-label',n==='dark'?'切換為淺色主題':'切換為深色主題')});})();")

def shell(title, desc, body, current='book'):
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="stylesheet" href="style.css">
<link rel="icon" href="{FAVICON}">
<script>
{THEME_JS}
</script>
</head>
<body>
<a class="skip" href="#main">跳到主要內容</a>
<div class="topbar">
  <div class="wrap topbar__in">
    <span class="topbar__id"><a href="index.html">Kittel</a><span class="topbar__sep">·</span>固態物理</span>
    <nav class="topbar__nav" aria-label="兩個入口">
      <a href="index.html"{' aria-current="page"' if current=='book' else ''}>全書逐章</a>
      <a href="thermal.html"{' aria-current="page"' if current=='thermal' else ''}>熱容專題</a>
    </nav>
    <button type="button" class="tbtn" data-toggle-theme aria-label="切換深淺色主題">深／淺</button>
  </div>
</div>
{body}
<footer class="foot">
  <div class="wrap--text">
    <p><b>版本與依據。</b>教材為 <strong>Kittel《Introduction to Solid State Physics》第 8 版</strong>（John Wiley &amp; Sons；第 18 章由 Paul McEuen 撰寫）。版本由 PDF 書名頁逐字辨識；章名、節名與頁碼逐字取自書本目錄 p.vii–xix。<strong>頁碼一律為書本頁碼</strong>（此 PDF 的 PDF 頁 = 書本頁 + 20）。</p>
    <ul class="lvl">
      <li class="is-book"><b>書中內容</b><span>①②③④ 四欄：主要內容與研究問題、核心物理概念、公式（含頁碼與式號）、結論與逐字引用。由 PDF 文字層擷取，並經獨立代理回原文逐條核對頁碼、式號與字句。</span></li>
      <li class="is-mine"><b>我的判讀</b><span>⑤⑥ 兩欄：與前後章的關係、與熱容的關聯程度。書中不會直說章與章的依賴，這是依實際內容所做的判斷。</span></li>
      <li><b>延伸知識</b><span>書中沒有直接討論但對讀者有用的補充，一律標明「【延伸知識】」。元件熱容 Cth 與元件熱阻 Rth 全書皆無，相關敘述都屬此類。</span></li>
    </ul>
    <p class="foot__tail">整理日期 2026-08-25。<a href="index.html">全書逐章</a>　·　<a href="thermal.html">熱容專題</a></p>
  </div>
</footer>
</body>
</html>"""

def scale_html(active=None):
    o = ['<nav class="scale" aria-label="章節刻度尺">', '<p class="scale__title">22 章 · 熱容關聯</p>', '<ol>']
    for n in range(1, 23):
        g = REL[str(n)]['grade']; _, _, cls = GRADE[g]
        en, zh, _ = META[n]
        cur = ' aria-current="page"' if active == n else ''
        o.append(f'<li class="{cls}"><a href="ch-{n:02d}.html"{cur} title="{e(zh)}｜{e(en)}">'
                 f'<span class="num">{n:02d}</span><span class="bar" aria-hidden="true"></span>'
                 f'<span class="vh">{e(zh)}</span></a></li>')
    o.append('</ol><div class="scale__key">'
             '<span><i style="background:var(--ember)"></i>直接</span>'
             '<span><i style="background:var(--indigo);width:56%"></i>間接</span>'
             '<span><i style="background:var(--line-strong);width:22%"></i>無</span></div></nav>')
    return '\n'.join(o)

def facet(no, key, body, anchor=None, cls=''):
    a = f' id="{anchor}"' if anchor else ''
    c = (' ' + cls) if cls else ''
    return f'<section class="facet{c}"{a}><p class="facet__k"><b>{no}</b>{e(key)}</p>{body}</section>'

def chapter_page(n):
    c = CH[str(n)]; r = REL[str(n)]
    en, zh, pages = META[n]
    label, tagcls, _ = GRADE[r['grade']]
    b = ['<div class="wrap"><p class="crumb"><a href="index.html">全書逐章</a> ／ '
         f'第 {n} 章</p></div>',
         f'<header class="uhead wrap"><span class="uhead__no num">{n:02d}</span>'
         f'<h1>{e(zh)}</h1><p class="uhead__en">{e(en)}</p>'
         f'<p class="chap__meta"><span>書本 p.{e(pages)}</span><span>公式 {len(c["equations"])} 條</span>'
         f'<span>核心概念 {len(c["coreConcepts"])} 條</span>'
         f'<span>熱容關聯 <span class="tag {tagcls}">{label}</span></span></p></header>',
         '<main id="main" class="wrap layout">', scale_html(active=n), '<article>']

    b.append(facet('①', '主要內容與研究問題', f'<p>{e(c["researchQuestion"])}</p>', 'f1'))
    b.append(facet('②', '核心物理概念', '<ul>' + ''.join(f'<li>{e(x)}</li>' for x in c['coreConcepts']) + '</ul>', 'f2'))

    eqs = ['<div class="eqs">']
    for q in c['equations']:
        rt = ([e(q['eqNumber'])] if q.get('eqNumber') else []) + [f'p.{q["bookPage"]}']
        eqs.append('<div class="eq">'
                   f'<p class="eq__l">{e(q["label"])}</p>'
                   f'<p class="eq__f">{e(q["formula"])}</p>'
                   f'<span class="eq__r">{" 　".join(rt)}</span>'
                   + (f'<p class="eq__s">{e(q["symbols"])}</p>' if q.get('symbols') else '') + '</div>')
    eqs.append('</div>')
    b.append(facet('③', '重要模型與公式', ''.join(eqs), 'f3'))

    q = f'<p>{e(c["mainConclusion"])}</p>'
    if c.get('verbatimQuotes'):
        q += ('<div class="quote"><p class="quote__k">書中逐字</p>'
              + ''.join(f'<p>{e(x)}</p>' for x in c['verbatimQuotes']) + '</div>')
    b.append(facet('④', '本章最重要的結論', q, 'f4'))
    b.append(facet('⑤', '與前後章的關係　（我的判讀）', f'<p>{e(r["relation"])}</p>', 'f5', 'facet--rel'))
    b.append('</article></main>')
    # ⑥ 移出欄外做成全幅板面：它是本專案的獨有貢獻，也是每頁的視覺地標
    b.append(f'''<section class="plate" id="f6">
  <div class="wrap--text">
    <p class="facet__k"><b>⑥</b>與熱容 Cth 的關聯程度　（我的判讀）</p>
    <span class="lead">{label}</span>
    <p>{e(r["cth"])}</p>
  </div>
</section>''')

    nav = ['<div class="wrap"><nav class="stepnav" aria-label="章之間">']
    if n > 1:
        pen, pzh, _ = META[n-1]
        nav.append(f'<a href="ch-{n-1:02d}.html"><span class="dir">← 上一章</span>'
                   f'<span class="t"><span class="n num">{n-1:02d}</span> {e(pzh)}</span></a>')
    else:
        nav.append('<a href="index.html"><span class="dir">← 回到</span><span class="t">全書總覽</span></a>')
    if n < 22:
        nen, nzh, _ = META[n+1]
        nav.append(f'<a href="ch-{n+1:02d}.html"><span class="dir">下一章 →</span>'
                   f'<span class="t"><span class="n num">{n+1:02d}</span> {e(nzh)}</span></a>')
    else:
        nav.append('<a href="thermal.html"><span class="dir">接著看 →</span><span class="t">熱容專題整理</span></a>')
    nav.append('</nav></div>')
    b.append('\n'.join(nav))

    return shell(f'第 {n} 章 {zh} — Kittel 全書逐章',
                 f'Kittel 第 8 版第 {n} 章「{en}」（書本 p.{pages}）的六欄整理：研究問題、核心概念、{len(c["equations"])} 條公式（含頁碼式號）、結論、與前後章的關係、與熱容的關聯程度。',
                 '\n'.join(b))

def index_page():
    neq = sum(len(c['equations']) for c in CH.values())
    nconc = sum(len(c['coreConcepts']) for c in CH.values())
    ndir = sum(1 for k in REL if k.isdigit() and REL[k]['grade'] == 'direct')
    nind = sum(1 for k in REL if k.isdigit() and REL[k]['grade'] == 'indirect')
    nnone = 22 - ndir - nind

    rows = []
    for n in range(1, 23):
        c = CH[str(n)]; r = REL[str(n)]
        en, zh, pages = META[n]
        label, tagcls, _ = GRADE[r['grade']]
        first = c['coreConcepts'][0] if c['coreConcepts'] else ''
        if len(first) > 46: first = first[:46] + '…'
        rows.append(f'<tr><td class="mono">{n:02d}</td>'
                    f'<td><a href="ch-{n:02d}.html"><b>{e(zh)}</b></a><br><span class="mine">{e(en)}</span></td>'
                    f'<td class="mono">{e(pages)}</td><td class="mono">{len(c["equations"])}</td>'
                    f'<td><span class="tag {tagcls}">{label}</span></td>'
                    f'<td>{e(first)}</td></tr>')

    apx = ''.join(f'<tr><td class="mono">{a}</td><td>{e(zh)}<br><span class="mine">{e(en)}</span></td>'
                  f'<td class="mono">p.{pg}</td><td>{"支撐" if g else "可略過"}</td></tr>'
                  for a, en, zh, pg, g in APPX)

    b = f"""<main id="main">
  <header class="hero">
    <div class="wrap">
      <p class="kicker">Kittel《Introduction to Solid State Physics》第 8 版</p>
      <h1>22 章，逐章拆解</h1>
      <p class="hero__lede">每章六欄：主要內容與研究問題／核心物理概念／重要模型與公式／最重要的結論／與前後章的關係／與熱容的關聯程度。</p>
      <p class="hero__claim">你不需要讀完 700 頁才知道哪一章與你有關。</p>
      <p class="anchors__cap">這份整理的實際規模</p>
      <ul class="anchors">
        <li><span class="v num">{neq}</span><span class="k">條公式，全部標到書本頁碼與式號</span></li>
        <li><span class="v num">{nconc}</span><span class="k">條核心概念，逐條回原文核對</span></li>
        <li><span class="v num">{ndir} / 22</span><span class="k">章與熱容直接相關</span></li>
      </ul>
    </div>
  </header>

  <div class="wrap layout">
    {scale_html()}
    <div>
      <h2 style="margin-top:0">全書總表</h2>
      <p>點章名進入該章的六欄整理。左側刻度尺的格子寬度就是「與熱容的關聯程度」——整本書的分佈一眼看完。</p>
      <div class="tablewrap">
        <table>
          <thead><tr><th>章</th><th>章名</th><th>書本頁</th><th>公式</th><th>熱容關聯</th><th>核心概念（首條）</th></tr></thead>
          <tbody>{''.join(rows)}</tbody>
        </table>
      </div>
    </div>
  </div>

  <section class="plate">
    <div class="wrap--text">
      <h2>整本書的熱容關聯分佈</h2>
      <p>把 22 章依「與熱容的關聯程度」分類，結果是嚴重偏斜的——這正是左側刻度尺想讓你一眼看到的事。</p>
      <div class="plate__grid">
        <div><span class="plate__n">{ndir}</span><p class="plate__k">章<strong>直接</strong>相關<br>Ch5 聲子熱容、Ch6 電子熱容、Ch18 奈米結構熱性質、Ch19 非晶低溫熱容</p></div>
        <div><span class="plate__n">{nind}</span><p class="plate__k">章<strong>間接</strong>相關<br>提供聲速、色散關係、模式計數或缺陷散射</p></div>
        <div><span class="plate__n">{nnone}</span><p class="plate__k">章<strong>無明顯關聯</strong><br>電子能帶、磁性、光學、缺陷力學</p></div>
      </div>
      <p style="margin-top:32px">分級與「與前後章的關係」是<strong>我依章節依賴所做的判讀</strong>，不是書中的說法。各章的公式、頁碼、式號與逐字引用則全部出自 PDF 文字層，並經獨立代理回原文逐條核對。</p>
    </div>
  </section>

  <section class="sect wrap--text">
    <h2>附錄 A–J</h2>
    <p>書末十個附錄。與熱容有間接價值的只有 C（彈性波量子化的正式處理）、D（費米–狄拉克分布）與 F（波茲曼輸運方程，可用來理解 K = ⅓Cvℓ 的來歷）。</p>
    <div class="tablewrap tablewrap--narrow">
      <table><thead><tr><th>附錄</th><th>標題</th><th>起始頁</th><th>對熱容</th></tr></thead><tbody>{apx}</tbody></table>
    </div>
  </section>

  <section class="sect wrap--text">
    <h2>姊妹頁：熱容專題</h2>
    <p>本頁按書的章序走。若你要的是「熱容」這條主線——它散在 Ch5、Ch6、Ch10、Ch12、Ch18、Ch19 六章裡——請看 <a href="thermal.html">熱容專題整理</a>：11 個主題沿 C(T) 溫度軸排列，每個主題六個固定面向，全部標到章節小節與頁碼。</p>
  </section>
</main>"""
    return shell('全書逐章整理 — Kittel 固態物理',
                 f'Kittel《Introduction to Solid State Physics》第 8 版全 22 章逐章整理：{neq} 條公式全部標到書本頁碼與式號，每章六欄，含與熱容的關聯分級。', b)

def build():
    io.open(os.path.join(BASE, 'index.html'), 'w', encoding='utf-8', newline='').write(index_page())
    for n in range(1, 23):
        io.open(os.path.join(BASE, f'ch-{n:02d}.html'), 'w', encoding='utf-8', newline='').write(chapter_page(n))
    neq = sum(len(c['equations']) for c in CH.values())
    sizes = [os.path.getsize(os.path.join(BASE, f'ch-{n:02d}.html')) for n in range(1, 23)]
    print(f'已生成 index.html ＋ 22 個章節頁｜公式 {neq} 條｜'
          f'章節頁大小 {min(sizes)//1024}–{max(sizes)//1024} KB')

if __name__ == '__main__':
    build()
