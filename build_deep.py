# -*- coding: utf-8 -*-
"""深度章節：三層架構。

  index.html      全書總覽
  ch-NN.html      章總覽：① 研究問題、小節導覽、⊘ 誤解、④⑤⑥
  ch-NN-sM.html   一節一頁：該節的全部講解單元

為什麼要拆出小節頁：Ch1 全部塞進一頁時實測 118 屏，量測判定「均質長捲軸、
單色湯 81.8%、模糊灰階變異 8.5」——就是一堵字牆。A 站踩過一次，不回頭。

執行順序固定為 `python build_a.py && python build_deep.py`：先產生 22 章的六欄
淺版，再由本腳本覆蓋已深講的章，所以還沒深講的章仍有頁面可看。
"""
import json, io, os, re, importlib.util

BASE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('a', os.path.join(BASE, 'build_a.py'))
A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)
shell, e, META, GRADE, REL, CH = A.shell, A.e, A.META, A.GRADE, A.REL, A.CH

TIER = {'derived': ('補推導', 'tier--derived'),
        'mine':    ('我的判讀', 'tier--mine'),
        'ext':     ('延伸知識', 'tier--ext')}


# *斜體*：本書的單星號大多是複數共軛（n*₋ₚ、S*S、a*_i），不能無條件當斜體。
# 借 CommonMark 的側翼規則收緊：左星號前不可是英數／CJK、後不可是空白，右星號反之，
# 且配對之間不得再出現星號。共軛星號一定緊貼字母，因此永遠當不成斜體的開頭。
ITALIC = re.compile(r'(?<![^\W_])\*(?=[^\s*])([^*\n]+?)(?<=[^\s*])\*(?![^\W_])')


def md(t):
    """先轉義再處理 **粗體**／*斜體*／`行內碼`，最後還原 \\| 跳脫。"""
    t = e(t)
    t = re.sub(r'\*\*(.+?)\*\*', lambda m: '<strong>' + m.group(1) + '</strong>', t, flags=re.S)
    t = ITALIC.sub(lambda m: '<em>' + m.group(1) + '</em>', t)
    t = re.sub(r'`(.+?)`', lambda m: '<code>' + m.group(1) + '</code>', t)
    # \| 是「字面豎線」的跳脫（絕對值 \|G\|）；切完欄之後才還原成 |
    t = t.replace('\\|', '|')
    return t


def prose(body):
    """把多段文字轉成 <p>，其中的 Markdown 表格獨立成 <table>。"""
    if not body:
        return ''
    out, tbl, quo = [], [], []

    def flush_quote():
        # 連續的「> 」行併成一個引用區塊，沿用章總覽既有的 .quote 樣式
        if not quo:
            return
        out.append('<blockquote class="quote">'
                   + ''.join(f'<p>{md(x)}</p>' for x in quo) + '</blockquote>')
        quo.clear()

    def flush_table():
        # 表格連續行要收集完才輸出，並丟掉 |---|---| 這種分隔列
        if not tbl:
            return
        # 只在「沒被 \ 跳脫的豎線」切欄，否則絕對值 \|G\| 會把一列切成兩倍欄數
        rows = []
        for ln in tbl:
            s = re.sub(r'(?<!\\)\|\s*$', '', re.sub(r'^\s*\|', '', ln.strip()))
            rows.append([c.strip() for c in re.split(r'(?<!\\)\|', s)])
        rows = [r for r in rows if not all(set(c) <= set('-: ') for c in r)]
        if rows:
            head, rest = rows[0], rows[1:]
            out.append('<div class="tablewrap"><table><thead><tr>'
                       + ''.join(f'<th>{md(h)}</th>' for h in head) + '</tr></thead><tbody>'
                       + ''.join('<tr>' + ''.join(f'<td>{md(c)}</td>' for c in r) + '</tr>'
                                 for r in rest)
                       + '</tbody></table></div>')
        tbl.clear()

    for para in body.split('\n\n'):
        for ln in para.split('\n'):
            s = ln.strip()
            if s.startswith('|'):            # 表格列：交給 flush_table 收集
                flush_quote()
                tbl.append(ln)
                continue
            flush_table()
            if s.startswith('>'):            # 引用：連續行併成一塊
                quo.append(s.lstrip('>').strip())
                continue
            flush_quote()
            if not s:
                continue
            h = re.match(r'^(#{1,6})\s+(.+)$', s)
            if h:                            # ## / ### 小標；全部走同一級，字級表不變胖
                out.append(f'<h4 class="prose__h">{md(h.group(2).strip())}</h4>')
            elif re.fullmatch(r'-{3,}|\*{3,}|_{3,}', s):
                out.append('<hr class="prose__hr">')
            else:
                out.append(f'<p>{md(s)}</p>')
        flush_table()
        flush_quote()
    flush_table()
    flush_quote()
    return ''.join(out)


def tier_tag(tier):
    if tier in TIER:
        label, cls = TIER[tier]
        return f'<span class="tier {cls}">{label}</span>'
    return ''


def eq_html(q):
    rt = ([e(q['eqNumber'])] if q.get('eqNumber') else []) + [f'p.{q["bookPage"]}']
    rows = ''
    for key, lab in (('from', '出處推導'), ('limits', '極限行為'), ('numeric', '典型數值')):
        if q.get(key, '').strip():
            rows += (f'<div class="eq__row"><span class="eq__rk">{lab}</span>'
                     f'<span class="eq__rv">{md(q[key])}</span></div>')
    meta = f'<div class="eq__meta">{rows}</div>' if rows else ''
    return ('<div class="eq">'
            f'<p class="eq__l">{e(q["label"])}</p>'
            f'<p class="eq__f">{e(q["formula"])}</p>'
            f'<span class="eq__r">{" 　".join(rt)}</span>'
            # symbols 與 from／limits／numeric 同屬手寫散文，一律走 md()；
            # 只用 e() 會讓 **粗體** 以字面星號留在頁面上。
            + (f'<p class="eq__s">{md(q["symbols"])}</p>' if q.get('symbols') else '')
            + meta + '</div>')


def block_html(b):
    kind = b.get('kind', 'concept')
    tag = tier_tag(b.get('tier', 'book'))

    if kind == 'equation':
        return f'<div class="eqs">{eq_html(b["eq"])}</div>'

    head = f'<h3 class="blk__h">{md(b["heading"])}{tag}</h3>' if b.get('heading') else ''

    if kind == 'derivation':
        steps = ''.join(f'<li>{md(s)}</li>' for s in b.get('steps', []))
        return (f'<section class="deriv">{head}{prose(b.get("body", ""))}'
                + (f'<ol class="deriv__steps">{steps}</ol>' if steps else '')
                + (prose(b['after']) if b.get('after') else '') + '</section>')

    return f'<div class="blk">{head}{prose(b.get("body", ""))}</div>'


def stat(s):
    """小節的組成統計，給章頁的導覽卡與小節頁的頁眉用。"""
    c = {'concept': 0, 'derivation': 0, 'equation': 0}
    for b in s.get('blocks', []):
        k = b.get('kind', 'concept')
        if k in c:
            c[k] += 1
    return c


def secnav_html(n, sections, cur=None):
    lis = ''.join(
        f'<li><a href="ch-{n:02d}-s{i}.html"'
        + (' aria-current="page"' if i == cur else '')
        + f'><span class="n">{i:02d}</span><span>{e(s["titleZh"])}</span></a></li>'
        for i, s in enumerate(sections, 1))
    return (f'<nav class="secnav" aria-label="本章小節">'
            f'<p class="secnav__t"><a href="ch-{n:02d}.html">本章小節</a></p>'
            f'<ol>{lis}</ol></nav>')


CJK = re.compile(r'[一-鿿]')


def count_words(D):
    """統計中文字數，用於頁首標示規模。

    只數中文字——把英文、標點、公式一起算進去會讓數字灌水到兩倍以上，
    而頁面上寫「字」時讀者理解的就是中文字。
    """
    n = 0
    for s in D['sections']:
        n += len(CJK.findall(s.get('lede', '')))
        for b in s.get('blocks', []):
            n += len(CJK.findall(b.get('body', '') + b.get('after', '')))
            n += len(CJK.findall(''.join(b.get('steps', []))))
            q = b.get('eq')
            if q:
                n += len(CJK.findall(''.join(q.get(k, '')
                                             for k in ('symbols', 'from', 'limits', 'numeric'))))
    for m in D.get('misconceptions', []):
        n += len(CJK.findall(m.get('wrong', '') + m.get('why', '') + m.get('right', '')))
    return n + len(CJK.findall(D.get('cthLink', '')))


def stepnav(items):
    return ('<div class="wrap"><nav class="stepnav" aria-label="頁間導覽">'
            + ''.join(items) + '</nav></div>')


def link(href, dir_, title, num=None):
    n = f'<span class="n num">{num:02d}</span> ' if num else ''
    return (f'<a href="{href}"><span class="dir">{dir_}</span>'
            f'<span class="t">{n}{title}</span></a>')


def section_page(n, i, D):
    secs = D['sections']; s = secs[i - 1]
    en, zh, _ = META[n]
    st = stat(s)
    en_t = f'<p class="sec__en">{e(s["title"])}</p>' if s.get('title') else ''
    lede = f'<p class="sec__lede">{md(s["lede"])}</p>' if s.get('lede') else ''

    b = [f'<div class="wrap"><p class="crumb"><a href="index.html">全書逐章</a> ／ '
         f'<a href="ch-{n:02d}.html">第 {n} 章 {e(zh)}</a> ／ 小節 {i}</p></div>',
         '<section class="plate plate--sec"><div class="wrap--text">'
         f'<div class="sec__h"><h1 class="sec__t"><span class="n">{i:02d}</span>'
         f'{e(s["titleZh"])}</h1>{en_t}'
         f'<p class="sec__p">書本 p.{e(s["pages"])}　·　小節 {i} / {len(secs)}　·　'
         f'概念 {st["concept"]}　推導 {st["derivation"]}　公式 {st["equation"]}</p></div>'
         + lede + '</div></section>',
         '<main id="main" class="wrap layout layout--deep">',
         '<div>' + secnav_html(n, secs, cur=i) + '</div>',
         '<article>',
         '<section class="sec">',
         ''.join(block_html(x) for x in s.get('blocks', [])),
         '</section></article></main>']

    nav = []
    if i > 1:
        nav.append(link(f'ch-{n:02d}-s{i-1}.html', '← 上一節', e(secs[i-2]['titleZh']), i - 1))
    else:
        nav.append(link(f'ch-{n:02d}.html', '← 回到', f'第 {n} 章總覽'))
    if i < len(secs):
        nav.append(link(f'ch-{n:02d}-s{i+1}.html', '下一節 →', e(secs[i]['titleZh']), i + 1))
    else:
        nav.append(link(f'ch-{n:02d}.html#fmis', '讀完本章 →', '常見誤解與熱容關聯'))
    b.append(stepnav(nav))

    return shell(f'{s["titleZh"]} — 第 {n} 章 {zh}',
                 f'Kittel 第 8 版第 {n} 章「{en}」小節 {i}「{s["title"]}」'
                 f'（書本 p.{s["pages"]}）的深度講解：每個觀念的物理動機、'
                 f'書中省略的推導步驟，以及公式的出處、極限與典型數值。',
                 '\n'.join(b))


def chapter_overview(n, D):
    c = CH[str(n)]; r = REL[str(n)]
    en, zh, pages = META[n]
    secs = D['sections']
    label, tagcls, _ = GRADE[r['grade']]
    n_eq = sum(1 for s in secs for x in s.get('blocks', []) if x.get('kind') == 'equation')
    n_der = sum(1 for s in secs for x in s.get('blocks', []) if x.get('kind') == 'derivation')
    words = count_words(D)

    cards = ''
    for i, s in enumerate(secs, 1):
        st = stat(s)
        cards += (f'<a class="seccard" href="ch-{n:02d}-s{i}.html">'
                  f'<span class="seccard__n num">{i:02d}</span>'
                  f'<span class="seccard__t">{e(s["titleZh"])}</span>'
                  f'<span class="seccard__en">{e(s["title"])}</span>'
                  f'<span class="seccard__p">書本 p.{e(s["pages"])}　·　'
                  f'概念 {st["concept"]}　推導 {st["derivation"]}　公式 {st["equation"]}</span>'
                  f'<span class="seccard__l">{e(s.get("lede", ""))}</span></a>')

    b = [f'<div class="wrap"><p class="crumb"><a href="index.html">全書逐章</a> ／ 第 {n} 章</p></div>',
         f'<header class="uhead wrap"><span class="uhead__no num">{n:02d}</span>'
         f'<h1>{e(zh)}</h1><p class="uhead__en">{e(en)}</p>'
         f'<p class="chap__meta"><span>書本 p.{e(pages)}</span>'
         f'<span><span class="big">{len(secs)}</span> 個小節</span>'
         f'<span><span class="big">{n_eq}</span> 條公式</span>'
         f'<span><span class="big">{n_der}</span> 段推導</span>'
         f'<span>約 <span class="big">{words:,}</span> 字</span>'
         f'<span>熱容關聯 <span class="tag {tagcls}">{label}</span></span></p></header>',
         '<main id="main">',
         '<div class="wrap--text">',
         '<section class="facet" id="f1"><p class="facet__k"><b>①</b>主要內容與研究問題</p>'
         + prose(D.get('intro') or c['researchQuestion']) + '</section>',
         '</div>',
         '<section class="plate" id="f23"><div class="wrap">'
         '<p class="plate__k"><b>②③</b>核心概念與公式　·　逐節深講</p>'
         '<p class="plate__lede">依書中實際小節切分，一節一頁。未標層級者為書中內容，'
         '頁碼與式號逐條核對；書中省略而由本站補上的代數步驟標為「補推導」。</p>'
         f'<div class="seclist">{cards}</div></div></section>',
         '<div class="wrap--text">']

    if D.get('misconceptions'):
        items = ''.join(
            f'<li class="misc__i"><p class="misc__w">{md(m["wrong"])}</p>'
            f'<p class="misc__why">{md(m["why"])}</p>'
            f'<p class="misc__r">{md(m["right"])}</p></li>'
            for m in D['misconceptions'])
        b.append('<section class="facet misc" id="fmis">'
                 '<p class="facet__k"><b>⊘</b>常見誤解與易錯點　（我的判讀）</p>'
                 f'<ul class="misc__l">{items}</ul></section>')

    q = f'<p>{e(c["mainConclusion"])}</p>'
    if c.get('verbatimQuotes'):
        q += ('<div class="quote"><p class="quote__k">書中逐字</p>'
              + ''.join(f'<p>{e(x)}</p>' for x in c['verbatimQuotes']) + '</div>')
    b.append(f'<section class="facet" id="f4"><p class="facet__k"><b>④</b>'
             f'本章最重要的結論</p>{q}</section>')
    b.append('<section class="facet facet--rel" id="f5">'
             '<p class="facet__k"><b>⑤</b>與前後章的關係　（我的判讀）</p>'
             f'<p>{e(r["relation"])}</p></section>')
    b.append('</div></main>')

    cth_extra = prose(D['cthLink']) if D.get('cthLink') else ''
    b.append('<section class="plate" id="f6"><div class="wrap--text">'
             '<p class="facet__k"><b>⑥</b>與熱容 Cth 的關聯程度　（我的判讀）</p>'
             f'<span class="lead">{label}</span><p>{e(r["cth"])}</p>{cth_extra}'
             '</div></section>')

    nav = []
    if n > 1:
        nav.append(link(f'ch-{n-1:02d}.html', '← 上一章', e(META[n-1][1]), n - 1))
    else:
        nav.append(link('index.html', '← 回到', '全書總覽'))
    if n < 22:
        nav.append(link(f'ch-{n+1:02d}.html', '下一章 →', e(META[n+1][1]), n + 1))
    else:
        nav.append(link('thermal.html', '接著看 →', '熱容專題整理'))
    b.append(stepnav(nav))

    return shell(f'第 {n} 章 {zh} — Kittel 全書逐章',
                 f'Kittel 第 8 版第 {n} 章「{en}」（書本 p.{pages}）的逐節深講總覽：'
                 f'{len(secs)} 個小節、{n_eq} 條公式、{n_der} 段補推導，'
                 f'另有常見誤解與熱容關聯。',
                 '\n'.join(b))


def main():
    d = os.path.join(BASE, 'data/deep')
    done = []
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        m = re.fullmatch(r'ch-(\d{2})\.json', f)
        if not m:
            continue
        n = int(m.group(1))
        D = json.load(io.open(os.path.join(d, f), encoding='utf-8'))

        def w(name, html):
            io.open(os.path.join(BASE, name), 'w', encoding='utf-8', newline='').write(html)

        w(f'ch-{n:02d}.html', chapter_overview(n, D))
        for i in range(1, len(D['sections']) + 1):
            w(f'ch-{n:02d}-s{i}.html', section_page(n, i, D))
        done.append((n, len(D['sections']), count_words(D)))

    for n, s, wd in done:
        print(f'  ch-{n:02d}.html ＋ {s} 個小節頁　約 {wd:,} 字')
    print(f'深度章節 {len(done)} 章')


if __name__ == '__main__':
    main()
