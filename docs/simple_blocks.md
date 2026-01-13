# Simple Blocks

Simple blocks are used for content display and data collection.

## Text
The `Text` block is the most basic block for displaying static content.
- **Usage**: Displaying instructions, articles, or context.
- **Properties**: Title, Body (list of strings/paragraphs).

## MultiRowOption
This is a helper class, not a standalone block, used to define the available choices for questions.
- **Properties**: Label (display text), Value (internal value), Color (visual hint like 'danger' or 'success').

## MultiRowChecked
A block that presents a list of "rows" (items), and for each row, a set of options that can be checked.
- **Usage**: "Check all that apply" style questions for multiple items.
- **Structure**:
  - `options`: A list of `MultiRowOption`.
  - rows are added via `.add_row()`.

## MultiRowSelect
A block that presents a list of "rows", and for each row, a set of specific questions answered via dropdowns or selections.
- **Usage**: When you need to ask multiple distinct questions (columns) for each item (row).
- **Structure**:
  - `questions`: A list of `MultiRowSelectQuestion`, each having its own `MultiRowOption` set.
