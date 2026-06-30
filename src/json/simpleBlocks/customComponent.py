class CustomComponent:
    """Generic host block: mounts author-provided HTML into the evaluation.

    The HTML may include custom elements (Web Components) such as ``<lego-tree>``.
    htmleval has no knowledge of those elements — register their JavaScript once
    with ``addCustomElement(name, js)`` and the component handles its own
    rendering and signalling (via the ``window.htmleval`` signal API).

      - ``zoomable``: optional convenience that wraps raw SVG content in a
        ``.zoomable-svg`` container (build.js's ``initZoomableSVGs`` gives it
        wheel-zoom and click-drag pan). Leave False if the content manages its own
        pan/zoom (custom elements typically do).

    The block is non-interactive on its own (reports 0/0 completion); any
    completion comes from the question blocks its components' signals are linked to.
    """

    def __init__(self, html: str, title: str = None, titleSize: int = None,
                 zoomable: bool = False, signal: str = None,
                 listeners: list = None, highlight: bool = False):
        self.type = "custom_component"
        self.signal = signal
        self.listeners = listeners if listeners is not None else []
        self.content = {
            "html": html,
            "zoomable": zoomable,
            "highlight": highlight,
        }
        if title is not None:
            self.content["title"] = {
                "text": title,
                "size": titleSize,
            }
