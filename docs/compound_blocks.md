# Compound Blocks

Compound blocks provide the layout structure for the evaluation.

## Tabs
The `Tabs` block acts as a container where child blocks are separated into distinct tabs.
- **Usage**: Almost always the root of the survey. Used to separate distinct tasks or sections.
- **Method**: `add_tab(tabName="Name", block=ChildBlock)`

## Column
The `Column` block arranges its children in a layout.
- **Usage**: Creating the main body of a tab, or creating side-by-side layouts.
- **Method**: `add_column([list_of_blocks])`.
  - Adding multiple columns via repeated calls to `add_column` creates a side-by-side layout (e.g., text on left, questions on right).

## Interactive
The `Interactive` block is a highly specialized compound block designed for granular text evaluation.
- **Usage**: When you need users to interact with specific sentences or fragments within a paragraph (e.g., "Click on the sentence that makes a claim").
- **Components**:
  - `InteractiveParagraph`: Represents a paragraph.
  - `InteractiveFragment`: Represents a piece of text within a paragraph that opens a pop-up or interaction when clicked.

## Thread
The `Thread` block is used to represent threaded conversations. It acts as a text block that can have other threads attached to it.
- **Properties**:
  - `title`: Optional title text.
  - `titleSize`: Size of header (e.g., 3 for h3).
  - `body`: List of paragraph strings.
- **Visuals**: Displays the text content, then adds a vertical line and indentation for any attached child threads.
- **Method**: `addThread(block)`
  - Adds a child `Thread` block (or other block) to the thread, indented below the current text.
