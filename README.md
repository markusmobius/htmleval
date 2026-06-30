# HTMLEval documentation

**HtmlEval** is a framework for constructing **evaluation surveys** with reusable, structured **blocks**.

It enables the creation of **simple and complex survey layouts**, allowing users to:
- **Evaluate text**
- **Categorize content**
- **Interact with structured data**

## Features

- **Simple & compound blocks** for building structured survey layouts.
- **Threaded conversations** via the `Thread` block, with nested indentation.
- **Signals & listeners** that let blocks highlight or reveal each other at runtime.
- **Custom components** for mounting bespoke HTML/SVG visualizations.
- **Review aggregation & summarization** — close reviews, compute majority votes
  and error rates, and generate a read-only summary reviewer.

## Installation

```bash
pip install git+https://github.com/markusmobius/htmleval
```

## Documentation

- **[Core Concepts](docs/concepts.md)**: Understand the difference between Simple and Compound blocks.
- **[Usage Guide](docs/usage.md)**: How to use the Python API to generate surveys, close reviews, and build summaries.
- **[Simple Blocks](docs/simple_blocks.md)**: Documentation for Text, Questions, CustomComponent, and other content blocks.
- **[Compound Blocks](docs/compound_blocks.md)**: Documentation for Layouts, Tabs, Threads, and Interactive blocks.
- **[Signals & Listeners](docs/signals.md)**: How blocks emit and react to signals at runtime.

## Getting Started

To see a running example, generating the survey from the repository:

```bash
python createDemo.py
```

Additional demos showcase specific features:

- `createDemo3.py` — nested **threads**.
- `createDemo4.py` — **signals & listeners** (linked menu).
- `createDemo5.py` + `createDemo5_summary.py` — the full **summarization**
  workflow: creating evaluations, closing them, aggregating reviewer answers, and
  generating a summary reviewer.
- `createDemo6.py` — **custom components**: mounting HTML/SVG, zoomable SVGs, and
  signal-wired SVG highlighting and completion ticks.

