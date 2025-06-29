# 🏨 Lunch-Check  freedreams Hotel Matcher 🇨🇭

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![DVC](https://img.shields.io/badge/DVC-enabled-success)](https://dvc.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Find hotels in Switzerland where you can **stay using your Lunch-Check credit** — by combining [Freedreams](https://www.freedreams.ch/) hotel deals with [Lunch-Check](https://www.lunch-check.ch/) participating restaurants.

## 💡 Project Overview

This tool scrapes:

- 🔸 **[Freedreams](https://www.freedreams.ch/):** Hotel voucher provider – book stays of 2+ nights where you only pay for breakfast and dinner, not the room.
- 🔸 **[Lunch-Check]([https://www.lunch-check.ch/](https://www.lunch-card.ch/public/LunchCheck/LC_Directory.aspx)):** A Swiss employee benefit allowing payment at restaurants using credits.

It then:

- ✅ Matches hotels that **have a restaurant** and **accept Lunch-Check**.
- 🔍 Uses **Levenshtein distance** for fuzzy matching between hotel and restaurant names.
- 🖼 Generates an **HTML page** with hotel images and basic info.

> ⚡ Now you can use your Lunch-Check credit to cover meals — and get hotel stays in Switzerland almost for free!

---

## 📦 Installation

This project uses [`uv`](https://github.com/astral-sh/uv) for fast and reliable dependency management.
If you don't have it yet, you can install it with curl:

```bash
curl -sSfL https://astral.sh/uv.sh | sh
```

Then, use uv sync to install the dependencies:

```bash
uv sync
```

You need to activate the virtual environment created by uv:

```bash
source .venv/bin/activate
```

Then, initialize DVC to be able to use the pipeline:

```bash
dvc init
```

## 🚀 Usage
Use dvc repro to run the pipeline and generate the HTML page with matched hotels:

```bash
dvc repro
```

## 📄 Output
The output will be generated HTML files under results/ directory.