"""A review page answered by a language model.

``render`` turns a page's blocks and ``model`` metadata (see ``htmleval.json.model``) into the text of one prompt per
call unit; ``clients`` wraps a model behind one small protocol; ``fill`` asks the model, parses its answers back onto
the page's own answer keys and stores them exactly as a human reviewer's answers are stored.
"""
