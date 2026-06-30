class CustomComponent:
    """Generic host block for a custom web component.

    Mounts author-provided, pre-rendered HTML/SVG into the evaluation and opts in
    to shared htmleval behaviors instead of re-implementing them per component:

      - ``zoomable``: wrap the mounted content in a ``.zoomable-svg`` container so
        build.js's ``initZoomableSVGs`` gives it wheel-zoom and click-drag pan.
        (If the supplied ``html`` already contains its own ``.zoomable-svg``
        wrapper, leave this False to avoid double-wrapping.)
      - ``svg_signals``: natively wire any descendant element that carries
        ``data-listeners`` and/or ``data-questions`` into htmleval's signal system
        and answer store:
            * ``data-listeners="sigA sigB"`` -> element gains class ``svg-sel``
              while a matching signal is the active signal.
            * ``data-questions='[["row","q"], ...]'`` -> a descendant ``.svg-tick``
              element is shown once every listed answer key is filled.
        These conventions match the legacy SVG bootstrap exactly, so existing
        renderers (e.g. the action graph) keep their signal/listener/completion
        wiring unchanged.

    The block is non-interactive on its own (it reports 0/0 completion); any
    completion comes from the question blocks its signals are linked to.
    """

    def __init__(self, html: str, title: str = None, titleSize: int = None,
                 zoomable: bool = False, svg_signals: bool = False,
                 signal: str = None, listeners: list = None,
                 highlight: bool = False):
        self.type = "custom_component"
        self.signal = signal
        self.listeners = listeners if listeners is not None else []
        self.content = {
            "html": html,
            "zoomable": zoomable,
            "svg_signals": svg_signals,
            "highlight": highlight,
        }
        if title is not None:
            self.content["title"] = {
                "text": title,
                "size": titleSize,
            }
