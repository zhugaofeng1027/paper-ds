import argparse
import glob
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple

import requests
from bs4 import BeautifulSoup


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "towards",
    "with",
    "via",
    "using",
    "based",
    "through",
    "toward",
    "be",
    "can",
    "do",
    "does",
    "from",
    "learning",
    "models",
    "model",
}


THEME_KEYWORDS = {
    "agent_systems": [
        "agent",
        "agents",
        "autonomous",
        "tool",
        "tools",
        "workflow",
        "assistant",
    ],
    "llm_and_reasoning": [
        "llm",
        "language model",
        "reasoning",
        "chain",
        "deliberation",
        "inference",
    ],
    "multi_agent": [
        "multi-agent",
        "multi agent",
        "coordination",
        "collaboration",
        "society",
        "swarm",
    ],
    "planning_and_decision": [
        "planning",
        "plan",
        "decision",
        "policy",
        "search",
        "tree",
    ],
    "retrieval_and_memory": [
        "retrieval",
        "memory",
        "rag",
        "database",
        "knowledge",
    ],
    "safety_and_alignment": [
        "safety",
        "alignment",
        "robust",
        "secure",
        "risk",
        "hallucination",
        "trust",
    ],
    "vision_and_multimodal": [
        "vision",
        "visual",
        "image",
        "video",
        "multimodal",
    ],
    "robotics_and_control": [
        "robot",
        "robotics",
        "control",
        "navigation",
        "manipulation",
    ],
    "code_and_software": [
        "code",
        "program",
        "software",
        "debug",
        "compiler",
    ],
}


@dataclass
class VenueTask:
    venue: str
    year: int
    url: str
    selectors: List[str]


def build_tasks(keyword: str, years: List[int], venues: List[str]) -> List[VenueTask]:
    k = keyword
    all_tasks: List[VenueTask] = []
    for year in years:
        if "acl" in venues:
            all_tasks.append(
                VenueTask(
                    "acl",
                    year,
                    f"https://aclanthology.org/events/acl-{year}/",
                    ["p.d-sm-flex strong a", "strong a", "a[href*='acl-']"],
                )
            )
        if "cvpr" in venues:
            all_tasks.append(
                VenueTask("cvpr", year, f"https://openaccess.thecvf.com/CVPR{year}?day=all", ["dt.ptitle > a"])
            )
        if "iccv" in venues and year in {2023, 2025}:
            all_tasks.append(
                VenueTask("iccv", year, f"https://openaccess.thecvf.com/ICCV{year}?day=all", ["dt.ptitle > a"])
            )
        if "eccv" in venues and year in {2024}:
            all_tasks.append(
                VenueTask("eccv", year, f"https://eccv.ecva.net/virtual/{year}/papers.html?search={k}", ["li a"])
            )
        if "neurips" in venues:
            all_tasks.append(
                VenueTask(
                    "neurips",
                    year,
                    f"https://neurips.cc/virtual/{year}/papers.html?search={k}",
                    ["li a"],
                )
            )
        if "icml" in venues:
            all_tasks.append(VenueTask("icml", year, f"https://icml.cc/virtual/{year}/papers.html?search={k}", ["li a"]))
        if "iclr" in venues:
            all_tasks.append(
                VenueTask(
                    "iclr",
                    year,
                    f"https://iclr.cc/virtual/{year}/papers.html?filter=titles&search={k}",
                    ["li a"],
                )
            )
    return all_tasks


def is_noise_title(title: str) -> bool:
    t = title.strip().lower()
    bad_exact = {
        "pdf",
        "bib",
        "bib (full)",
        "bib (urls)",
        "copy bibtex",
    }
    if t in bad_exact:
        return True
    if len(t) < 12:
        return True
    if t.startswith("http"):
        return True
    return False


def fetch_titles(task: VenueTask, keyword: str) -> List[str]:
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(task.url, headers=headers, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    elements = []
    for selector in task.selectors:
        elements = soup.select(selector)
        if elements:
            break

    titles: List[str] = []
    for element in elements:
        text = element.get_text(strip=True)
        if not text:
            continue
        if is_noise_title(text):
            continue
        if keyword.lower() not in text.lower():
            continue
        titles.append(text)

    # Keep order, remove duplicates
    return list(dict.fromkeys(titles))


def save_titles(keyword: str, venue: str, year: int, titles: List[str], out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    safe_kw = re.sub(r"[^a-zA-Z0-9_-]+", "_", keyword.lower())
    file_name = f"{safe_kw}_papers_{venue}{year}_{len(titles)}.txt"
    out_path = os.path.join(out_dir, file_name)
    with open(out_path, "w", encoding="utf-8") as f:
        for title in titles:
            f.write(title + "\n")
    return out_path


def crawl(keyword: str, years: List[int], venues: List[str], out_dir: str) -> Tuple[List[str], Dict[str, int]]:
    tasks = build_tasks(keyword, years, venues)
    saved_files: List[str] = []
    counts: Dict[str, int] = {}
    all_titles: List[str] = []

    for task in tasks:
        key = f"{task.venue}{task.year}"
        try:
            titles = fetch_titles(task, keyword)
            out = save_titles(keyword, task.venue, task.year, titles, out_dir)
            saved_files.append(out)
            counts[key] = len(titles)
            all_titles.extend(titles)
            print(f"[OK] {key}: {len(titles)}")
        except Exception as exc:
            counts[key] = 0
            print(f"[ERR] {key}: {exc}")

    # Aggregate file for analysis
    dedup_all = list(dict.fromkeys(all_titles))
    aggregate = os.path.join(out_dir, f"{keyword.lower()}_all_titles.txt")
    with open(aggregate, "w", encoding="utf-8") as f:
        f.write("\n".join(dedup_all))
    saved_files.append(aggregate)
    print(f"[OK] aggregate: {len(dedup_all)} -> {aggregate}")

    return saved_files, counts


def load_titles_from_txt(path: str) -> List[str]:
    titles: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                titles.append(line)
    return titles


def tokenize(text: str, banned_tokens: set[str]) -> List[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9-]+", text.lower())
    return [w for w in words if len(w) > 2 and w not in STOPWORDS and w not in banned_tokens]


def count_phrases(tokens_per_title: List[List[str]]) -> Counter:
    phrase_counter: Counter = Counter()
    for tokens in tokens_per_title:
        for i in range(len(tokens) - 1):
            bg = f"{tokens[i]} {tokens[i + 1]}"
            if tokens[i] in STOPWORDS or tokens[i + 1] in STOPWORDS:
                continue
            phrase_counter[bg] += 1
    return phrase_counter


def infer_theme(title: str) -> List[str]:
    t = title.lower()
    matched: List[str] = []
    for theme, words in THEME_KEYWORDS.items():
        if any(w in t for w in words):
            matched.append(theme)
    return matched


def analyze_titles(titles: List[str], keyword: str) -> Dict[str, object]:
    kw = keyword.lower()
    banned_tokens = {kw, f"{kw}s", "agent", "agents", "agentic"}
    tokens_per_title = [tokenize(t, banned_tokens) for t in titles]
    word_counter: Counter = Counter()
    for tokens in tokens_per_title:
        word_counter.update(tokens)

    phrase_counter = count_phrases(tokens_per_title)
    theme_counter: Counter = Counter()
    theme_examples: Dict[str, List[str]] = defaultdict(list)

    for title in titles:
        themes = infer_theme(title)
        if themes:
            for th in themes:
                theme_counter[th] += 1
                if len(theme_examples[th]) < 3:
                    theme_examples[th].append(title)
        else:
            theme_counter["other"] += 1

    return {
        "total_titles": len(titles),
        "top_words": word_counter.most_common(20),
        "top_phrases": phrase_counter.most_common(15),
        "theme_counter": theme_counter,
        "theme_examples": theme_examples,
    }


def parse_venue_counts_from_filenames(paths: List[str]) -> Dict[str, int]:
    result: Dict[str, int] = {}
    for p in paths:
        name = os.path.basename(p)
        m = re.search(r"_papers_([a-z]+)(\d{4})_(\d+)\.txt$", name)
        if m:
            result[f"{m.group(1)}{m.group(2)}"] = int(m.group(3))
    return dict(sorted(result.items(), key=lambda x: x[0]))


def write_report(
    keyword: str,
    input_files: List[str],
    result: Dict[str, object],
    venue_counts: Dict[str, int],
    report_dir: str,
) -> str:
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"{keyword.lower()}_analysis_report.md")

    theme_counter: Counter = result["theme_counter"]  # type: ignore[assignment]
    theme_examples: Dict[str, List[str]] = result["theme_examples"]  # type: ignore[assignment]
    top_words = result["top_words"]  # type: ignore[assignment]
    top_phrases = result["top_phrases"]  # type: ignore[assignment]

    sorted_themes = theme_counter.most_common()
    non_generic = [x for x in sorted_themes if x[0] != "agent_systems"]
    total = result["total_titles"]

    lines = [
        f"# Keyword Analysis Report: {keyword}",
        "",
        "## 1) Data Overview",
        f"- Total titles: **{total}**",
        f"- Input files: **{len(input_files)}**",
        "",
        "### Counts by venue-year",
    ]
    for k, v in venue_counts.items():
        lines.append(f"- {k}: {v}")

    lines += [
        "",
        "## 2) High-Frequency Words",
    ]
    for w, c in top_words:
        lines.append(f"- {w}: {c}")

    lines += [
        "",
        "## 3) High-Frequency Phrases",
    ]
    for p, c in top_phrases:
        lines.append(f"- {p}: {c}")

    lines += [
        "",
        "## 4) Theme Distribution (for research direction)",
    ]
    for theme, c in sorted_themes:
        ratio = (c / total * 100) if total else 0.0
        lines.append(f"- {theme}: {c} ({ratio:.1f}%)")
        examples = theme_examples.get(theme, [])
        if examples:
            lines.append(f"  Example: {examples[0]}")

    # Conclusions
    lines += [
        "",
        "## 5) Practical Conclusions",
    ]
    if non_generic:
        top_theme = non_generic[0][0]
        lines.append(f"- Current hotspot signal: **{top_theme}** appears most frequently among non-generic subfields.")
    elif sorted_themes:
        top_theme = sorted_themes[0][0]
        lines.append(f"- Current hotspot signal: **{top_theme}** appears most frequently.")
    if top_phrases:
        lines.append(f"- Common phrase trend: **{top_phrases[0][0]}** is the most repeated phrase.")
    lines.append("- Actionable suggestion: prioritize papers in top 2-3 themes and build a focused reading list.")
    lines.append("- Actionable suggestion: track growth by venue-year to find fast-rising subtopics.")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return report_path


def maybe_plot_themes(theme_counter: Counter, keyword: str, out_dir: str) -> str:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return ""

    os.makedirs(out_dir, exist_ok=True)
    pairs = theme_counter.most_common(8)
    if not pairs:
        return ""

    labels = [k for k, _ in pairs]
    values = [v for _, v in pairs]

    plt.figure(figsize=(10, 5))
    plt.bar(labels, values, color="#5B8FF9")
    plt.xticks(rotation=30, ha="right")
    plt.title(f"Theme Distribution for '{keyword}'")
    plt.xlabel("Theme")
    plt.ylabel("Count")
    plt.tight_layout()

    out_path = os.path.join(out_dir, f"{keyword.lower()}_theme_distribution.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path


def collect_keyword_files(keyword: str, txt_dir: str) -> List[str]:
    safe_kw = re.sub(r"[^a-zA-Z0-9_-]+", "_", keyword.lower())
    pattern = os.path.join(txt_dir, f"{safe_kw}_papers_*.txt")
    return sorted(glob.glob(pattern))


def parse_years(raw: str) -> List[int]:
    years = []
    for x in raw.split(","):
        x = x.strip()
        if not x:
            continue
        years.append(int(x))
    return years


def parse_venues(raw: str) -> List[str]:
    return [x.strip().lower() for x in raw.split(",") if x.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Top-conference paper spider + title analysis pipeline")
    sub = parser.add_subparsers(dest="command", required=True)

    crawl_cmd = sub.add_parser("crawl", help="Crawl paper titles by keyword and save to txt")
    crawl_cmd.add_argument("-k", "--keyword", required=True, help="Keyword, case-insensitive, e.g. Agent")
    crawl_cmd.add_argument("--years", default="2023,2024,2025", help="Comma-separated years")
    crawl_cmd.add_argument(
        "--venues",
        default="acl,cvpr,iccv,eccv,neurips,icml,iclr",
        help="Comma-separated venue list",
    )
    crawl_cmd.add_argument("--txt-dir", default="txt", help="Directory to save txt files")

    ana_cmd = sub.add_parser("analyze", help="Analyze saved txt files and output a report")
    ana_cmd.add_argument("-k", "--keyword", required=True, help="Keyword used in filenames")
    ana_cmd.add_argument("--txt-dir", default="txt", help="Directory containing txt files")
    ana_cmd.add_argument("--report-dir", default="report", help="Directory to save report")
    ana_cmd.add_argument("--plot-dir", default="plot", help="Directory to save figures")
    ana_cmd.add_argument("--from-file", default="", help="Analyze this one txt file directly")

    all_cmd = sub.add_parser("all", help="Run crawl + analyze in one command")
    all_cmd.add_argument("-k", "--keyword", required=True, help="Keyword, case-insensitive")
    all_cmd.add_argument("--years", default="2023,2024,2025", help="Comma-separated years")
    all_cmd.add_argument(
        "--venues",
        default="acl,cvpr,iccv,eccv,neurips,icml,iclr",
        help="Comma-separated venue list",
    )
    all_cmd.add_argument("--txt-dir", default="txt", help="Directory to save txt files")
    all_cmd.add_argument("--report-dir", default="report", help="Directory to save report")
    all_cmd.add_argument("--plot-dir", default="plot", help="Directory to save figures")

    args = parser.parse_args()

    if args.command == "crawl":
        _, counts = crawl(args.keyword, parse_years(args.years), parse_venues(args.venues), args.txt_dir)
        print("Crawl finished. Counts:", counts)
        return

    if args.command == "analyze":
        if args.from_file:
            files = [args.from_file]
        else:
            files = collect_keyword_files(args.keyword, args.txt_dir)
        if not files:
            raise FileNotFoundError("No keyword txt files found. Run crawl first.")

        all_titles: List[str] = []
        for f in files:
            all_titles.extend(load_titles_from_txt(f))
        all_titles = list(dict.fromkeys(all_titles))

        result = analyze_titles(all_titles, args.keyword)
        venue_counts = parse_venue_counts_from_filenames(files)
        report_path = write_report(args.keyword, files, result, venue_counts, args.report_dir)
        fig = maybe_plot_themes(result["theme_counter"], args.keyword, args.plot_dir)
        print("Analyze finished.")
        print("Report:", report_path)
        if fig:
            print("Plot:", fig)
        return

    if args.command == "all":
        files, _ = crawl(args.keyword, parse_years(args.years), parse_venues(args.venues), args.txt_dir)
        crawl_files = [f for f in files if f.endswith(".txt") and "_papers_" in os.path.basename(f)]
        all_titles: List[str] = []
        for f in crawl_files:
            all_titles.extend(load_titles_from_txt(f))
        all_titles = list(dict.fromkeys(all_titles))

        result = analyze_titles(all_titles, args.keyword)
        venue_counts = parse_venue_counts_from_filenames(crawl_files)
        report_path = write_report(args.keyword, crawl_files, result, venue_counts, args.report_dir)
        fig = maybe_plot_themes(result["theme_counter"], args.keyword, args.plot_dir)
        print("All finished.")
        print("Report:", report_path)
        if fig:
            print("Plot:", fig)
        return


if __name__ == "__main__":
    main()
