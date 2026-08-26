# Kittel 固態物理 — 全書逐章 × 熱容專題

以 **Kittel《Introduction to Solid State Physics》第 8 版**為依據的兩份導讀，給固態物理研究所學生使用。

| 入口 | 內容 |
|---|---|
| `index.html` **全書逐章** | 22 章逐章整理，每章六欄：①主要內容與研究問題 ②核心物理概念 ③重要模型與公式（199 條，全部標到書本頁碼與式號）④最重要的結論 ⑤與前後章的關係 ⑥與熱容的關聯程度。每章各自一頁 `ch-NN.html`。 |
| `thermal.html` **熱容專題** | 11 個熱容主題沿 C(T) 溫度軸排列，每主題六個固定面向 ＋ 熱容知識地圖。 |

## 版本辨識

版本由 PDF 書名頁逐字辨識為 **EIGHTH EDITION**（第 18 章 Nanostructures 由 Paul McEuen 撰寫）。
章名、節名與頁碼逐字取自書本目錄 p.vii–xix。**所有頁碼皆為書本頁碼**（該 PDF 的 PDF 頁 = 書本頁 + 20）。

## 三層信心標註

- **書中內容**（①②③④）：由 PDF 文字層擷取，並經獨立代理回原文逐條核對頁碼、式號與字句。
- **我的判讀**（⑤⑥）：與前後章的關係、與熱容的關聯程度。書中不會直說章與章的依賴。
- **延伸知識**：書中沒有直接討論的補充，行文中標明。**元件熱容 Cth 與元件熱阻 Rth 全書皆無**。

## 資料與產生方式

```
data/chapters.json    22 章的擷取結果（已套用 32 條校對更正）
data/relations.json   ⑤⑥ 兩欄的判讀
build_a.py            由上述兩份 JSON 產生 index.html 與 22 個章節頁
style.css             設計系統（單一檔案，所有頁面共用）
design-brief.md       設計簡報：概念、色票、招牌時刻與安全牌偵測
```

改內容請改 JSON 再跑 `python build_a.py`，不要直接改 HTML。

## 技術

純靜態、零依賴：無 CDN、無 webfont、無 JS 函式庫。唯一的 JavaScript 是約 8 行的深淺色主題切換。
支援深淺雙主題與 `prefers-reduced-motion`。整個 repo clone 下來直接開 `index.html` 即可離線使用。
