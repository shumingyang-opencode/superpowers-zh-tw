#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the bilingual (EN/ZH-TW) static site for superpowers-zh-tw.

Reads the translated (zh-TW) Markdown in this repo + fetches the English
originals from upstream obra/superpowers, aligns them block-by-block, and
writes static HTML at the repo root (served by GitHub Pages):

  index.html            — landing page (entry cards)
  map.html              — the "basic workflow" highway skill map
  learning-path.html    — the leveled learning-path card view
  install.html          — install guide for all supported harnesses
  about.html            — about Jesse Vincent / Prime Radiant / license
  <skill>/SKILL.html    — bilingual skill page per skill
  <skill>/<NAME>.html   — bilingual page per attached doc
  assets/skills-data.json — machine-readable skill registry

Run:  python scripts/build-site.py
English sources are cached under .site-cache/ so re-runs work offline.
"""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".site-cache" / "en"
UPSTREAM_BASE = "https://raw.githubusercontent.com/obra/superpowers/main"
BLOB_BASE = "https://github.com/shumingyang-opencode/superpowers-zh-tw/blob/main"

# --------------------------------------------------------------------------
# Skill registry: name -> metadata
# cat: process | discipline | meta
# level: L0 | L1 | L2 | L3 | L4 | support
# inv: boot | model
# --------------------------------------------------------------------------
SKILLS = {
    "using-superpowers":             {"cat": "meta",      "level": "L0", "inv": "boot",  "blurb": "開場白技能：任何對話開始時先檢查有沒有技能適用，先呼叫再行動。"},
    "brainstorming":                 {"cat": "process",   "level": "L1", "inv": "model", "blurb": "動工前的第一站：把你的點子敲成具體設計，問到你講清楚為止。"},
    "using-git-worktrees":           {"cat": "process",   "level": "L1", "inv": "model", "blurb": "開工先開一個隔離的 git worktree，主分支不被打擾。"},
    "writing-plans":                 {"cat": "process",   "level": "L2", "inv": "model", "blurb": "把定稿的設計拆成一步一步、小到 2–5 分鐘的任務，每個都標好檔案與驗證方式。"},
    "executing-plans":               {"cat": "process",   "level": "L3", "inv": "model", "blurb": "照寫好的計畫，在另開的 session 分批執行，每批有人類檢查點。"},
    "subagent-driven-development":   {"cat": "process",   "level": "L3", "inv": "model", "blurb": "照計畫逐任務派全新的子代理實作，先對規格再對品質的兩階段審查。"},
    "dispatching-parallel-agents":   {"cat": "process",   "level": "L3", "inv": "model", "blurb": "面對 2+ 個互不依賴的任務，平行派子代理同時做。"},
    "requesting-code-review":        {"cat": "process",   "level": "L4", "inv": "model", "blurb": "任務完成、發合併前，送審查確認有沒有照需求做。"},
    "receiving-code-review":         {"cat": "process",   "level": "L4", "inv": "model", "blurb": "收到審查意見，先想清楚再動手——不是照單全收也不是硬撐。"},
    "finishing-a-development-branch":{"cat": "process",   "level": "L4", "inv": "model", "blurb": "全部測過、都綠了之後，決定要合併、發 PR 還是留著。"},
    "test-driven-development":       {"cat": "discipline", "level": "L3", "inv": "model", "blurb": "先寫會失敗的測試，再看它紅、寫最小程式讓它綠、重構——回饋逼出好程式。"},
    "systematic-debugging":          {"cat": "discipline", "level": "L3", "inv": "model", "blurb": "遇到 bug 先別急著修：四階段根因流程，先鎖住再挖根。"},
    "verification-before-completion":{"cat": "discipline", "level": "L4", "inv": "model", "blurb": "宣告完成之前，先真的跑驗證指令、親眼看到輸出——證據優先於斷言。"},
    "writing-skills":                {"cat": "meta",      "level": "support", "inv": "model", "blurb": "怎麼寫、怎麼測、怎麼部署一個技能——寫技能本身也是 TDD。"},
}

ATTACHED = {
    "brainstorming": ["spec-document-reviewer-prompt", "visual-companion"],
    "using-superpowers": [],
    "writing-plans": ["plan-document-reviewer-prompt"],
    "subagent-driven-development": ["implementer-prompt", "re-review-prompt", "task-reviewer-prompt"],
    "requesting-code-review": ["code-reviewer"],
    "test-driven-development": ["writing-good-tests"],
    "systematic-debugging": ["root-cause-tracing", "defense-in-depth", "condition-based-waiting", "CREATION-LOG", "test-academic", "test-pressure-1", "test-pressure-2", "test-pressure-3"],
    "writing-skills": ["anthropic-best-practices", "testing-skills-with-subagents", "persuasion-principles"],
}

# Attached docs living in a subdirectory of the skill (e.g. harness references).
# key = skill name, value = list of subdirectories whose *.md become pages.
REFERENCE_DOCS = {
    "using-superpowers": ["references"],
}

# Map: the basic workflow highway
PRECONDITION = "using-superpowers"
MAINLINE = [
    {"center": ["brainstorming"]},
    {"center": ["using-git-worktrees"]},
    {"center": ["writing-plans"]},
    {"center": ["subagent-driven-development"], "right": ["executing-plans"]},
    {"center": ["test-driven-development"], "right": ["dispatching-parallel-agents"]},
    {"center": ["requesting-code-review"], "right": ["receiving-code-review"]},
    {"center": ["finishing-a-development-branch"]},
]
SERVICES = ["systematic-debugging", "verification-before-completion"]
META = ["writing-skills"]

LEVELS = [
    ("L0", "開場", "裝好 Superpowers 之後，每個 session 自動生效", "lv-cyan", ["using-superpowers"]),
    ("L1", "動手之前", "想清楚要做什麼、把場地隔離好", "lv-blue", ["brainstorming", "using-git-worktrees"]),
    ("L2", "把設計變計畫", "拆成能照做的小任務", "lv-violet", ["writing-plans"]),
    ("L3", "執行與除錯", "派代理逐任務實作，邊寫邊測", "lv-pink", ["subagent-driven-development", "executing-plans", "test-driven-development", "dispatching-parallel-agents", "systematic-debugging"]),
    ("L4", "審查與收尾", "送出審查、處理意見、合併上線", "lv-amber", ["requesting-code-review", "receiving-code-review", "finishing-a-development-branch", "verification-before-completion"]),
    ("support", "怎麼寫技能", "meta：把技能本身當產品來寫", "lv-green", ["writing-skills"]),
]

# --------------------------------------------------------------------------
# Parsing / rendering
# --------------------------------------------------------------------------
def parse_frontmatter(text: str):
    fm = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm_text, body = parts[1], parts[2]
            for line in fm_text.split("\n"):
                line = line.strip()
                if not line or ":" not in line:
                    continue
                k, v = line.split(":", 1)
                v = v.strip()
                if v.startswith('"') and v.endswith('"'):
                    v = v[1:-1]
                fm[k.strip()] = v
    return fm, body.lstrip("\n")


def split_blocks(body: str):
    """Split markdown body into top-level blocks (blank-line separated, fence/html aware)."""
    lines = body.split("\n")
    blocks = []
    i, n = 0, len(lines)
    while i < n:
        stripped = lines[i].strip()
        if stripped == "":
            i += 1
            continue
        if stripped.startswith("```"):
            j = i + 1
            while j < n and not lines[j].strip().startswith("```"):
                j += 1
            blocks.append("\n".join(lines[i: min(j + 1, n)]))
            i = j + 1
            continue
        if stripped.startswith("<") and not stripped.startswith("</") and not stripped.startswith("<!--"):
            m = re.match(r"<([a-zA-Z0-9\-]+)[\s>]", stripped) or re.match(r"<([a-zA-Z0-9\-]+)>", stripped)
            if m:
                tag = m.group(1)
                closing = f"</{tag}>"
                if closing in stripped:
                    blocks.append(lines[i]); i += 1; continue
                j = i + 1
                while j < n and closing not in lines[j]:
                    j += 1
                blocks.append("\n".join(lines[i: min(j + 1, n)]))
                i = j + 1
                continue
        j = i + 1
        while j < n and lines[j].strip() != "":
            j += 1
        blocks.append("\n".join(lines[i:j]))
        i = j
    return blocks


def render_md(md_text: str) -> str:
    import markdown
    return markdown.markdown(md_text, extensions=["fenced_code", "tables", "sane_lists"])


def pair_blocks(en_body, zh_body):
    en_blocks = split_blocks(en_body)
    zh_blocks = split_blocks(zh_body)
    if len(en_blocks) != len(zh_blocks):
        print(f"  [warn] block count mismatch: EN={len(en_blocks)} ZH={len(zh_blocks)}")
    pairs = []
    n = max(len(en_blocks), len(zh_blocks))
    for i in range(n):
        en = en_blocks[i] if i < len(en_blocks) else ""
        zh = zh_blocks[i] if i < len(zh_blocks) else ""
        pairs.append((en, zh))
    return pairs


# --------------------------------------------------------------------------
# Fetching (offline cache)
# --------------------------------------------------------------------------
def fetch(path: str) -> str:
    cached = CACHE / (path.replace("/", "__") + ".md")
    if cached.exists():
        return cached.read_text(encoding="utf-8")
    url = f"{UPSTREAM_BASE}/{path}"
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            data = r.read().decode("utf-8")
        CACHE.mkdir(parents=True, exist_ok=True)
        cached.write_text(data, encoding="utf-8")
        return data
    except Exception as e:
        print(f"  [err] could not fetch {url}: {e}")
        return ""


# --------------------------------------------------------------------------
# Page templates
# --------------------------------------------------------------------------
def page_open(title: str, prefix: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} · superpowers-zh-tw</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=Noto+Serif+TC:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}assets/site.css">
</head>
<body>
<div class="container">
"""


def page_close() -> str:
    return """
</div>
</body>
</html>
"""


def breadcrumb(name: str, is_skill: bool, prefix: str, parent_href: str = "SKILL.html") -> str:
    parent = f'<a href="{parent_href}">← 技能主頁 {name}</a> ' if not is_skill else ""
    return f"""<div class="back-link">
  <a href="{prefix}index.html">首頁</a>
  <a href="{prefix}map.html">全景圖</a>
  <a href="{prefix}learning-path.html">學習路線</a>
  {parent}
</div>
"""


def rewrite_links(html: str, skill: str) -> str:
    """Rewrite relative links in a rendered skill page.

    - `.md` / `.html` links to files that exist in this repo -> sibling `.html`
      (site mirrors the skills/ directory, so relative paths are preserved,
      including cross-skill `../<skill>/<doc>.md` links).
    - `.md` links whose target does not exist (illustrative examples such as
      FORMS.md / REFERENCE.md) -> plain text, so they never 404.
    - other files (scripts, assets) -> GitHub blob URL of this repo.
    """
    blob_dir = f"{BLOB_BASE}/skills/{skill}"
    skill_root = ROOT / "skills" / skill
    skills_root = ROOT / "skills"

    def is_within_skills(path: Path) -> bool:
        try:
            path.relative_to(skills_root)
            return True
        except ValueError:
            return False

    def strip_missing(m):
        href, inner = m.group(1), m.group(2)
        if not href.startswith(("http", "#", "mailto", "/", "data:", "javascript:")):
            target = (skill_root / href).resolve()
            if is_within_skills(target) and not target.exists():
                return inner
        return m.group(0)

    html = re.sub(r'<a\s+href="([^"]+)"[^>]*>(.*?)</a>', strip_missing, html, flags=re.S)

    def repl(m):
        attr, href = m.group(1), m.group(2)
        if href.startswith(("http", "#", "mailto", "/", "data:", "javascript:")):
            return m.group(0)
        if href.startswith("../"):
            target = (skill_root / href).resolve()
            try:
                rel = target.relative_to(skills_root)
            except ValueError:
                return m.group(0)
            new_href = os.path.relpath(str(rel.parent / rel.stem) + ".html", skill)
        else:
            target = href.lstrip("./")
            if target.endswith(".md"):
                new_href = target[:-3] + ".html"
            elif target.endswith(".html"):
                new_href = target
            else:
                new_href = f"{blob_dir}/{target}"
        return f'{attr}="{new_href}"'

    return re.sub(r'(href|src)="([^"]+)"', repl, html)


def fm_table(en_fm, zh_fm) -> str:
    rows = ""
    name = en_fm.get("name", zh_fm.get("name", ""))
    rows += f'<tr><td>name</td><td><code>{name}</code></td></tr>\n'
    if en_fm.get("description"):
        rows += f'<tr><td>description (EN)</td><td>{en_fm["description"]}</td></tr>\n'
    if zh_fm.get("description"):
        rows += f'<tr><td>說明 (繁中)</td><td>{zh_fm["description"]}</td></tr>\n'
    return f'<table class="fm-table">\n{rows}</table>\n'


def attached_links(name: str) -> str:
    docs = ATTACHED.get(name, [])
    links = "　·　".join(f'<a href="{d}.html">{d}</a>' for d in docs)
    for subdir in REFERENCE_DOCS.get(name, []):
        ref_dir = ROOT / "skills" / name / subdir
        if not ref_dir.exists():
            continue
        for p in sorted(ref_dir.glob("*.md")):
            links += (("　·　" if links else "") + f'<a href="{subdir}/{p.stem}.html">{p.stem}</a>')
    if not links:
        return ""
    return f'<div class="back-link" style="margin-top:-0.6rem">附屬文件：{links}</div>\n'


# --------------------------------------------------------------------------
# Skill / attached pages
# --------------------------------------------------------------------------
def skill_page(name: str):
    meta = SKILLS.get(name, {})
    src_dir = f"skills/{name}"
    en_full = fetch(f"{src_dir}/SKILL.md")
    zh_full = (ROOT / src_dir / "SKILL.md").read_text(encoding="utf-8")
    en_fm, en_body = parse_frontmatter(en_full)
    zh_fm, zh_body = parse_frontmatter(zh_full)
    pairs = pair_blocks(en_body, zh_body)

    html = page_open(name, "../")
    html += breadcrumb(name, is_skill=True, prefix="../")
    html += fm_table(en_fm, zh_fm)
    html += f"<h1>{name}</h1>\n"
    html += f'<div class="subtitle">{meta.get("blurb", "")}</div>\n'
    html += attached_links(name)
    for en, zh in pairs:
        if not en and not zh:
            continue
        en_html = render_md(en) if en else '<p class="zh-only">（無英文對照）</p>'
        zh_html = render_md(zh) if zh else '<p class="en-only">（無繁中對照）</p>'
        en_html = rewrite_links(en_html, name)
        zh_html = rewrite_links(zh_html, name)
        html += f'<div class="pair"><div class="col-en" lang="en">{en_html}</div><div class="col-zh" lang="zh-Hant">{zh_html}</div></div>\n'
    html += page_close()
    out = ROOT / name / "SKILL.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"  ✓ {out.relative_to(ROOT)}")


def attached_page(name: str, doc: str):
    src_dir = f"skills/{name}"
    en_full = fetch(f"{src_dir}/{doc}.md")
    zh_full = (ROOT / src_dir / f"{doc}.md").read_text(encoding="utf-8")
    en_fm, en_body = parse_frontmatter(en_full)
    zh_fm, zh_body = parse_frontmatter(zh_full)
    pairs = pair_blocks(en_body, zh_body)

    html = page_open(f"{name} / {doc}", "../")
    html += breadcrumb(name, is_skill=False, prefix="../")
    html += f"<h1>{doc}</h1>\n"
    html += f'<div class="subtitle">{name} · 附屬文件</div>\n'
    for en, zh in pairs:
        if not en and not zh:
            continue
        en_html = render_md(en) if en else '<p class="zh-only">（無英文對照）</p>'
        zh_html = render_md(zh) if zh else '<p class="en-only">（無繁中對照）</p>'
        en_html = rewrite_links(en_html, name)
        zh_html = rewrite_links(zh_html, name)
        html += f'<div class="pair"><div class="col-en" lang="en">{en_html}</div><div class="col-zh" lang="zh-Hant">{zh_html}</div></div>\n'
    html += page_close()
    out = ROOT / name / f"{doc}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"  ✓ {out.relative_to(ROOT)}")


def reference_page(name: str, subdir: str, doc: str):
    """Bilingual page for an attached doc in a skill subdirectory (e.g. references/)."""
    src_dir = f"skills/{name}/{subdir}"
    en_full = fetch(f"{src_dir}/{doc}.md")
    zh_full = (ROOT / src_dir / f"{doc}.md").read_text(encoding="utf-8")
    en_fm, en_body = parse_frontmatter(en_full)
    zh_fm, zh_body = parse_frontmatter(zh_full)
    pairs = pair_blocks(en_body, zh_body)

    html = page_open(f"{name} / {doc}", "../../")
    html += breadcrumb(name, is_skill=False, prefix="../../", parent_href="../SKILL.html")
    html += f"<h1>{doc}</h1>\n"
    html += f'<div class="subtitle">{name} · {subdir} · 附屬文件</div>\n'
    for en, zh in pairs:
        if not en and not zh:
            continue
        en_html = render_md(en) if en else '<p class="zh-only">（無英文對照）</p>'
        zh_html = render_md(zh) if zh else '<p class="en-only">（無繁中對照）</p>'
        en_html = rewrite_links(en_html, name)
        zh_html = rewrite_links(zh_html, name)
        html += f'<div class="pair"><div class="col-en" lang="en">{en_html}</div><div class="col-zh" lang="zh-Hant">{zh_html}</div></div>\n'
    html += page_close()
    out = ROOT / name / subdir / f"{doc}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"  ✓ {out.relative_to(ROOT)}")


# --------------------------------------------------------------------------
# Map / learning path / index
# --------------------------------------------------------------------------
def node_html(skill: str, kind: str = "mainline", small: bool = False) -> str:
    meta = SKILLS[skill]
    cls = f"node {kind}" + (" small" if small else "")
    return (f'<a class="{cls}" href="{skill}/SKILL.html">'
            f'<span class="label">{skill}</span>'
            f'<span class="tag">{meta["blurb"]}</span>'
            f'<span class="pill">{meta["inv"]}</span>'
            f'</a>')


def map_page():
    html = page_open("技能全景圖 · Skill Atlas", "")
    html += """<div class="back-link"><a href="index.html">← 首頁</a><a href="learning-path.html">學習路線</a></div>
<header>
  <h1>技能全景圖</h1>
  <div class="subtitle">Skill Atlas · Superpowers 的基本工作流：從點子到上線，一條路走到底</div>
  <div class="badge-line">點任何一格，進到逐段中英對照頁</div>
</header>
"""
    html += f"""<div class="precondition">
  <a href="using-superpowers/SKILL.html"><span class="label">using-superpowers</span><span class="tag">開場白自動生效：先檢查技能，再行動</span></a>
  <div class="precondition-hint">每個 session 啟動時注入：任何回應之前先呼叫相關技能</div>
</div>
"""
    html += '<div class="zone"><div class="zone-label">主線：從點子到上線 · idea → ship</div><div class="highway">\n'
    for row in MAINLINE:
        html += '<div class="hwy-row">\n'
        html += '  <div class="col-left">'
        if row.get("left"):
            html += '<div class="ramp-cluster">' + "".join(node_html(s, "on-ramp", small=True) for s in row["left"]) + "</div>"
        html += '</div>\n'
        html += '  <div class="col-center"><div class="pair-main">'
        center = row["center"]
        if isinstance(center, list) and any(x in ("↔", "→") for x in center):
            idx = next(i for i, x in enumerate(center) if x in ("↔", "→"))
            left, arrow, right = center[:idx], center[idx], center[idx + 1:]
            for s in left:
                html += node_html(s, "mainline")
            html += f'<span class="pair-arrow">{arrow}</span>'
            for s in right:
                html += node_html(s, "mainline", small=True)
        else:
            for s in center:
                html += node_html(s, "mainline")
        html += '</div></div>\n'
        html += '  <div class="col-right">'
        if row.get("right"):
            right_nodes = row["right"] if isinstance(row["right"], list) else [row["right"]]
            html += "".join(node_html(s, "on-ramp") for s in right_nodes)
        html += '</div>\n'
        html += '</div>\n'
        html += '<div class="flow-arrow"></div>\n'
    html += "</div></div>\n"

    html += '<div class="zone"><div class="zone-label">隨取隨用 · 遇到問題再進來</div><div class="h-zone"><div class="h-row">'
    for s in SERVICES:
        html += node_html(s, "standalone")
    html += '</div><div class="h-note">除錯與驗證：隨時遇到隨時用，不必進主線</div></div></div>\n'

    html += '<div class="zone"><div class="zone-label">meta 技能：怎麼寫、怎麼測、怎麼部署技能</div><div class="h-zone"><div class="h-row">'
    for s in META:
        html += node_html(s, "meta")
    html += '</div><div class="h-note">寫技能本身也是 TDD——先有會失敗的測試，再寫技能</div></div></div>\n'

    html += '<div class="legend">'
    html += '<span class="legend-item"><span class="legend-dot mainline"></span>主線（必走）</span>'
    html += '<span class="legend-item"><span class="legend-dot on-ramp"></span>替代入口（擇一）</span>'
    html += '<span class="legend-item"><span class="legend-dot standalone"></span>隨取隨用</span>'
    html += '<span class="legend-item"><span class="legend-dot meta"></span>meta</span>'
    html += '</div>\n'

    html += '<div class="zone"><div class="zone-label">深讀解說 · 教學中心</div><div class="h-zone"><div class="h-row">'
    html += '<a class="node meta" href="docs/teaching/methodology.html"><span class="label">方法論總覽</span><span class="tag">它跟一般技能包差在哪</span><span class="pill">teaching</span></a>'
    html += '<a class="node meta" href="docs/teaching/workflow.html"><span class="label">工作流拆解</span><span class="tag">七個階段每一步</span><span class="pill">teaching</span></a>'
    html += '<a class="node meta" href="docs/teaching/philosophy.html"><span class="label">哲學四原則</span><span class="tag">四原則如何落地</span><span class="pill">teaching</span></a>'
    html += '<a class="node meta" href="docs/teaching/subagent-driven.html"><span class="label">SDD 深入</span><span class="tag">為什麼全新子代理最快</span><span class="pill">teaching</span></a>'
    html += '<a class="node meta" href="docs/teaching/skill-authoring.html"><span class="label">如何寫 Skill</span><span class="tag">寫技能也是 TDD</span><span class="pill">teaching</span></a>'
    html += '</div><div class="h-note">策展式中文深讀——比翻譯多一層的教學解說</div></div></div>\n'

    html += footer()
    html += page_close()
    out = ROOT / "map.html"
    out.write_text(html, encoding="utf-8")
    print("  ✓ map.html")


def card_html(skill: str, meta: dict, color_cls: str = "lv-cyan") -> str:
    tags = f'<span class="c-tag">{meta["cat"]}</span><span class="c-tag">{meta["inv"]}</span>'
    return (f'<a class="card" href="{skill}/SKILL.html">'
            f'<span class="c-name">{skill}</span>'
            f'<span class="c-zh">{meta["blurb"]}</span>'
            f'<span class="c-tags">{tags}</span>'
            f'</a>')


def learning_path_page():
    html = page_open("學習路線 · Learning Path", "")
    html += """<div class="back-link"><a href="index.html">← 首頁</a><a href="map.html">技能全景圖</a></div>
<header>
  <h1>學習路線</h1>
  <div class="subtitle">Learning Path · 從 0 練到上線</div>
  <div class="badge-line">分層分級一關一關過；support 層隨時可翻</div>
</header>
"""
    for badge, title, sub, color_cls, names in LEVELS:
        html += f'<div class="level {color_cls}"><div class="level-head"><span class="level-badge">{badge}</span><span class="level-title">{title}</span><span class="level-sub">{sub}</span></div><div class="card-grid">'
        for s in names:
            html += card_html(s, SKILLS[s], color_cls)
        html += '</div></div>\n'
    html += footer()
    html += page_close()
    out = ROOT / "learning-path.html"
    out.write_text(html, encoding="utf-8")
    print("  ✓ learning-path.html")


def install_page():
    repo = "shumingyang-opencode/superpowers-zh-tw"
    html = page_open("安裝指南 · Install Guide", "")
    html += """<div class="back-link"><a href="index.html">← 首頁</a><a href="map.html">全景圖</a><a href="learning-path.html">學習路線</a></div>
<header>
  <h1>安裝指南</h1>
  <div class="subtitle">Install Guide · Superpowers 支援的每一個平台，一步一步裝</div>
  <div class="badge-line">裝好之後，每個 session 開場就自動生效——先檢查技能，再行動</div>
</header>
<div class="guide">

<h2>這是什麼</h2>
<p>Superpowers 是一套給 coding agent 的「完整軟體開發方法論」——建構在一組可組合的技能之上，加上確保 agent 會使用它們的開場指令。它是 <a href="https://github.com/obra/superpowers" target="_blank" rel="noopener">obra/superpowers</a>（MIT License）的<strong>繁體中文翻譯學習站</strong>。<strong>本 repo 只改說明文字，指令、路徑、技能名全部照原樣，所以安裝方式跟上游完全一樣。</strong></p>
<p class="hint">Superpowers 官方建議：如果你用多個 harness，請分別為每個安裝。</p>

<h2>OpenCode（本機開發主平台）</h2>
<p>在 <code>opencode.json</code>（全域或專案層級）的 <code>plugin</code> 陣列加入：</p>
<pre>{
  "plugin": ["superpowers@git+https://github.com/obra/superpowers.git"]
}</pre>
<p>重開 OpenCode。外掛透過 plugin manager 安裝並註冊所有技能。驗證：問「Tell me about your superpowers」。想釘版本就改用分支或 tag：</p>
<pre>{
  "plugin": ["superpowers@git+https://github.com/obra/superpowers.git#v5.0.3"]
}</pre>
<p>詳見 <a href="https://raw.githubusercontent.com/obra/superpowers/main/docs/README.opencode.md" target="_blank" rel="noopener">docs/README.opencode.md</a>（OpenCode 版完整指南，含 troubleshooting）。</p>

<h2>Claude Code</h2>
<p>官方 marketplace 安裝：</p>
<pre>/plugin install superpowers@claude-plugins-official</pre>
<p>或註冊 Superpowers marketplace 再裝：</p>
<pre>/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace</pre>

<h2>Codex App / Codex CLI</h2>
<p>Codex App：側欄 Plugins → Coding 區塊找到 Superpowers → 按 <code>+</code> 安裝。</p>
<p>Codex CLI：</p>
<pre>/plugins</pre>
<p>搜尋 <code>superpowers</code> → 選擇 Install Plugin。</p>

<h2>Cursor</h2>
<p>在 Cursor Agent chat 安裝：</p>
<pre>/add-plugin superpowers</pre>
<p>或在 plugin marketplace 搜尋「superpowers」。</p>

<h2>Gemini CLI</h2>
<pre>gemini extensions install https://github.com/obra/superpowers</pre>
<p>更新：<code>gemini extensions update superpowers</code></p>

<h2>GitHub Copilot CLI</h2>
<pre>copilot plugin marketplace add obra/superpowers-marketplace
copilot plugin install superpowers@superpowers-marketplace</pre>

<h2>Kimi Code</h2>
<pre>/plugins</pre>
<p>Marketplace → Superpowers 安裝；或直接從 repo 安裝：</p>
<pre>/plugins install https://github.com/obra/superpowers</pre>

<h2>Antigravity</h2>
<pre>agy plugin install https://github.com/obra/superpowers</pre>

<h2>Factory Droid</h2>
<pre>droid plugin marketplace add https://github.com/obra/superpowers
droid plugin install superpowers@superpowers</pre>

<h2>Pi</h2>
<pre>pi install git:github.com/obra/superpowers</pre>

<h2>開始使用</h2>
<ol>
  <li>裝好後，下一個 session 開場就注入 Superpowers 的開場指令。</li>
  <li>直接說「我們來做 X」——它會先觸發 <code>brainstorming</code>，把點子敲成設計。</li>
  <li>本網站就是這套技能的閱讀版：<a href="map.html">全景圖</a>看工作流，<a href="learning-path.html">學習路線</a>照順序學，每個技能頁都是中英逐段對照。</li>
</ol>

<h2>注意</h2>
<ul>
  <li>這是<strong>翻譯學習站</strong>；想用英文原版，直接安裝上游：<code>superpowers@git+https://github.com/obra/superpowers.git</code>。</li>
  <li><strong>不要兩套都裝</strong>——每個技能會出現兩次。選擇其一。</li>
  <li>翻譯只動說明文字，若遇問題請先比對上游行為。</li>
</ul>

</div>
"""
    html += footer()
    html += page_close()
    out = ROOT / "install.html"
    out.write_text(html, encoding="utf-8")
    print("  ✓ install.html")


def sync_panel() -> str:
    status_path = ROOT / "docs" / "upstream-status.json"
    try:
        st = json.loads(status_path.read_text(encoding="utf-8"))
    except Exception:
        return ('<div class="sync-panel"><h2>待辦事項 · 上游同步</h2>'
                '<p class="sync-muted">尚未初始化（docs/upstream-status.json 不存在）。</p></div>')
    aligned = st.get("aligned", {})
    current = st.get("current", {})
    pending = st.get("pending", [])
    up_to_date = st.get("status") == "synced"

    badge = ('<span class="sync-badge ok">已同步</span>' if up_to_date
             else f'<span class="sync-badge warn">落後 {len(pending)} 項</span>')
    aligned_line = f'對齊上游 <code>{aligned.get("version", "?")}</code>（<code>{str(aligned.get("short", ""))}</code>）'
    cur = current.get("short")
    cur_line = f'上游目前 <code>{current.get("version", "?")}</code>（<code>{cur}</code>）' if cur else '上游目前 （未檢查）'

    html = ('<div class="sync-panel"><h2>待辦事項 · 上游同步</h2>'
            f'<div class="sync-meta">{aligned_line} · {cur_line} {badge}</div>')
    if pending:
        items = "".join(
            f'<li><code>{e.get("kind")}</code> {e.get("from", "")}{" → " if e.get("kind") == "rename" else ""}{e.get("path")}'
            f'<span class="sync-reason">（{e.get("reason", "")}）</span>'
            + (f'<br><span class="sync-note">{e.get("note", "")}</span>' if e.get("note") else "")
            + "</li>"
            for e in pending
        )
        html += (f'<details class="sync-list"><summary>待翻譯／整理項目（{len(pending)} 項）</summary>'
                 f'<ul>{items}</ul></details>')
    else:
        html += '<p class="sync-empty">目前沒有待辦事項。</p>'
    html += "</div>"
    return html


def about_card_html() -> str:
    return """<div class="about-card-wrap"><a class="about-card" href="about.html">
  <div class="about-row">
    <span class="ec-icon">👤</span>
    <span class="ec-title">About Jesse Vincent</span>
    <span class="ec-en">Author · 作者介紹</span>
    <span class="ec-arrow">→</span>
  </div>
  <span class="ec-desc">Superpowers 的作者，Prime Radiant 的創辦人。開源 superpowers、bugzilla、RT（Request Tracker）等專案。點進了解完整介紹。</span>
</a></div>"""


def about_page():
    html = page_open("About Jesse Vincent · 作者介紹", "")
    html += """<div class="back-link"><a href="index.html">← 首頁</a><a href="map.html">全景圖</a><a href="learning-path.html">學習路線</a></div>
<header>
  <h1>About Jesse Vincent</h1>
  <div class="subtitle">作者介紹 · 開源老兵 · Superpowers 之父</div>
  <div class="badge-line">Prime Radiant · blog.fsck.com</div>
</header>
<div class="guide">

<h2>一、快速認識</h2>
<p>Jesse Vincent 是長期的開源貢獻者與維護者，最為人知的是維護 Request Tracker（RT）——全球企業與政府機關廣用的問題追蹤系統——以及創立 Best Practical Solutions 公司。他也是 <a href="https://blog.fsck.com/2025/10/09/superpowers/" target="_blank" rel="noopener">Superpowers</a>（GitHub 269k 星）的作者，以 <a href="https://primeradiant.com" target="_blank" rel="noopener">Prime Radiant</a> 名義開發。</p>
<ul>
  <li><strong>RT（Request Tracker）</strong> — 維護者（1999 年至今）</li>
  <li><strong>bugzilla.org</strong> — 共同維護者</li>
  <li><strong>Best Practical Solutions</strong> — 創辦人</li>
  <li><strong>Superpowers</strong> — 作者（obra/superpowers，269k 星）</li>
</ul>

<h2>二、與 Superpowers 的關係</h2>
<p>Superpowers 是「可組合的技能」＋「開場指令」的套件，讓 coding agent 從「一看到要建東西就直接寫 code」，變成「先問清楚你想做什麼 → 拆成計畫 → 派子代理照計畫逐任務實作，邊做邊測」。它的哲學強調：</p>
<ul>
  <li><strong>測試驅動開發</strong> — 永遠先寫測試</li>
  <li><strong>系統化優於 ad-hoc</strong> — 流程勝於瞎猜</li>
  <li><strong>降低複雜度</strong> — 簡潔是首要目標</li>
  <li><strong>證據勝於宣稱</strong> — 宣告成功前先驗證</li>
</ul>
<p>更多方法論細節，見 <a href="docs/teaching/methodology.html">方法論總覽</a>。</p>

<h2>三、授權與聲明</h2>
<ul>
  <li>上游 <code>obra/superpowers</code> 以 <strong>MIT License</strong> 釋出（Copyright © 2025 Jesse Vincent）。</li>
  <li>本站是<strong>非官方</strong>繁體中文翻譯學習站，與 Prime Radiant 無關，不代表官方立場。</li>
  <li>本站照抄上游的 <a href="LICENSE">LICENSE</a>，並以 <a href="NOTICE">NOTICE</a> 宣告引用範圍與原創內容授權。</li>
</ul>

<h2>四、社群</h2>
<div class="link-grid">
  <a href="https://blog.fsck.com" target="_blank" rel="noopener">個人部落格 · blog.fsck.com</a>
  <a href="https://primeradiant.com" target="_blank" rel="noopener">Prime Radiant · primeradiant.com</a>
  <a href="https://github.com/obra/superpowers" target="_blank" rel="noopener">GitHub · obra/superpowers</a>
  <a href="https://discord.gg/35wsABTejz" target="_blank" rel="noopener">Discord</a>
  <a href="https://primeradiant.com/superpowers/" target="_blank" rel="noopener">Release 公告訂閱</a>
</div>

</div>
"""
    html += footer()
    html += page_close()
    out = ROOT / "about.html"
    out.write_text(html, encoding="utf-8")
    print("  ✓ about.html")


def index_page():
    html = page_open("Superpowers 技能包 · 繁中解讀", "")
    html += """<header>
  <h1>Superpowers 技能包</h1>
  <div class="subtitle">14 個給 coding agent 的開發方法論技能，中英逐段並排，口語解說</div>
</header>
<div class="entry-cards">
  <a class="entry-card" href="map.html">
    <span class="ec-icon">🗺️</span>
    <span class="ec-title">全景圖</span>
    <span class="ec-en">Skill Atlas</span>
    <span class="ec-desc">一張圖看懂 14 個技能怎麼接成「從點子到上線」的完整工作流——開場、動工前、計畫、執行、審查、收尾。</span>
  </a>
  <a class="entry-card" href="learning-path.html">
    <span class="ec-icon">🧗</span>
    <span class="ec-title">學習路線</span>
    <span class="ec-en">Learning Path</span>
    <span class="ec-desc">不想只看懂、想真的上手？從 L0 一路練到 L4，分層分級照著走。</span>
  </a>
  <a class="entry-card" href="install.html">
    <span class="ec-icon">📦</span>
    <span class="ec-title">安裝指南</span>
    <span class="ec-en">Install Guide</span>
    <span class="ec-desc">Superpowers 支援的每個平台（OpenCode / Claude Code / Codex / Cursor / Gemini…）一步一步裝。</span>
  </a>
  <a class="entry-card" href="docs/teaching/index.html">
    <span class="ec-icon">📚</span>
    <span class="ec-title">教學中心</span>
    <span class="ec-en">Teaching Hub</span>
    <span class="ec-desc">深讀解說：方法論總覽、工作流拆解、哲學四原則、SDD 深入、怎麼寫 Skill。</span>
  </a>
</div>
"""
    html += sync_panel()
    html += about_card_html()
    html += footer()
    html += page_close()
    out = ROOT / "index.html"
    out.write_text(html, encoding="utf-8")
    print("  ✓ index.html")


def footer() -> str:
    return f"""<footer>
  <div>這是 <a href="https://github.com/obra/superpowers">obra/superpowers</a> 的繁體中文翻譯學習站——翻譯只動說明文字，指令、路徑、技能名一律照原樣，安裝照常可用。</div>
  <div>內容 © <a href="https://github.com/obra">Jesse Vincent</a>（MIT License）· 本站為非官方教學站，與 Prime Radiant 無關 · 使用 OpenCode 與 deepseek-v4-flash 進行繁中翻譯與網站設計建置</div>
</footer>
"""


def write_data():
    data = {"skills": {}}
    for name, meta in SKILLS.items():
        try:
            zh_full = (ROOT / f"skills/{name}/SKILL.md").read_text(encoding="utf-8")
            zh_fm, _ = parse_frontmatter(zh_full)
            zh_desc = zh_fm.get("description", "")
        except Exception:
            zh_desc = ""
        data["skills"][name] = {**meta, "description_zh": zh_desc}
    (ROOT / "assets" / "skills-data.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("  ✓ assets/skills-data.json")


def main():
    os.chdir(ROOT)
    print("Generating bilingual site...")
    print("[skill pages]")
    for name in SKILLS:
        skill_page(name)
    print("[attached pages]")
    for name, docs in ATTACHED.items():
        for d in docs:
            attached_page(name, d)
    print("[reference pages]")
    for name, subdirs in REFERENCE_DOCS.items():
        for subdir in subdirs:
            ref_dir = ROOT / "skills" / name / subdir
            if not ref_dir.exists():
                continue
            for p in sorted(ref_dir.glob("*.md")):
                reference_page(name, subdir, p.stem)
    print("[views]")
    map_page()
    learning_path_page()
    install_page()
    about_page()
    index_page()
    write_data()
    print("Done.")


if __name__ == "__main__":
    sys.exit(main())
