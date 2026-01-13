# Core Concepts

HtmlEval is built around the concept of **Blocks**. A generic evaluation or survey is essentially a tree of blocks.

## Simple vs. Compound Blocks

There are two main types of blocks in the framework:

### 1. Simple Blocks (Content & Interaction)
**Simple Blocks** are the fundamental units of content and user interaction. They are primarily used to:
- Display information (e.g., `Text`).
- Collect user input (e.g., `MultiRowChecked`, `MultiRowSelect`).

Think of Simple Blocks as the "leaves" of your survey tree. They do not contain other blocks; proper content flows within them.

**Examples:**
- **Text**: Displays a title and paragraphs.
- **MultiRowChecked**: A list of items where one or more can be selected (checkbox style).
- **MultiRowSelect**: A list of items with dropdown selections.

### 2. Compound Blocks (Layout & Structure)
**Compound Blocks** are container blocks used to organize the layout and structure of your survey. Their primary purpose is to hold other blocks (children).

Compound Blocks allow you to build complex interfaces by nesting blocks. A Compound Block can contain Simple Blocks or other Compound Blocks.

**Examples:**
- **Tabs**: Organizes content into clickable tabs. The root of a survey is often a Tabs block.
- **Column**: Arranges child blocks vertically or horizontally (e.g., for side-by-side comparisons).
- **Interactive**: A specialized block for fine-grained text interaction (highlighting, specific sentence feedback).
