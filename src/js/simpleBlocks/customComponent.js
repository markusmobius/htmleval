// Generic host for a custom web component.
//
// Mounts pre-rendered HTML/SVG provided by the Python `CustomComponent` block and
// opts in to shared htmleval behaviors (signal highlighting, completion ticks,
// pan/zoom) rather than each component re-implementing them. This is the
// supported extension point for adding bespoke visualizations (e.g. the action
// graph) to an evaluation while staying inside the standard block pipeline.
class CustomComponent {
    constructor(root, block, parent, blockID) {
        this.blockID = blockID;
        this.parent = parent;
        // Non-interactive container: completion is driven by linked question blocks.
        this.completed = [0, 0];

        var container = document.createElement("div");
        container.className = "text-content";
        root.appendChild(container);

        // Optional title.
        if (block["content"]["title"] != undefined) {
            var h = document.createElement("h" + block["content"]["title"]["size"]);
            h.innerHTML = block["content"]["title"]["text"];
            container.appendChild(h);
        }

        // Mount the author-provided markup.
        var mount = document.createElement("div");
        mount.innerHTML = block["content"]["html"] || "";
        container.appendChild(mount);

        // Optional pan/zoom: wrap raw content so build.js's initZoomableSVGs (which
        // runs after every block is built) wires it up. Skipped when the html
        // already provides its own .zoomable-svg wrapper.
        if (block["content"]["zoomable"] && !mount.querySelector(".zoomable-svg")) {
            mount.classList.add("zoomable-svg");
            mount.style.position = "relative";
            mount.style.overflow = "hidden";
        }

        // Register this block as a signal emitter/listener (block-level), reusing
        // the standard helper.
        registerSignal(container, block);

        // Opt in to descendant-level SVG signal/completion wiring.
        if (block["content"]["svg_signals"]) {
            initSvgSignalWiring();
        }
    }

    completion() {
        this.parent.completion(this.blockID, this.completed[0], this.completed[1]);
    }
}

// One-time global hook that wires elements inside custom components into
// htmleval's signal system and answer store. Elements opt in declaratively:
//   data-listeners="sigA sigB"          -> class "svg-sel" while a matching
//                                           signal is active (style it via CSS).
//   data-questions='[["row","q"], ...]' -> show a descendant ".svg-tick" element
//                                           once every listed answer key is filled.
// Wrapping emitSignal/saveSurvey (rather than editing the template) keeps this
// behavior identical to the legacy inline bootstrap it replaces.
var __htmlevalSvgSignalsInit = false;
function initSvgSignalWiring() {
    if (__htmlevalSvgSignalsInit) return;
    __htmlevalSvgSignalsInit = true;

    var _emit = window.emitSignal;
    window.emitSignal = function (sig) {
        if (_emit) _emit(sig);
        var els = document.querySelectorAll("[data-listeners]");
        for (var i = 0; i < els.length; i++) {
            var el = els[i];
            var listeners = (el.getAttribute("data-listeners") || "").split(" ");
            var on = sig && listeners.indexOf(sig) !== -1;
            el.classList.toggle("svg-sel", !!on);
        }
    };

    window.__htmlevalSvgTicks = function () {
        if (typeof data === "undefined" || !data || !data.variables) return;
        var els = document.querySelectorAll("[data-questions]");
        for (var i = 0; i < els.length; i++) {
            var el = els[i];
            var keys = [];
            try { keys = JSON.parse(el.getAttribute("data-questions")); } catch (e) { keys = []; }
            var done = keys.length > 0;
            for (var j = 0; j < keys.length; j++) {
                var v = data.variables[keys[j]];
                if (v === undefined || v === null || v === "") done = false;
            }
            var tick = el.querySelector(".svg-tick");
            if (tick) tick.style.display = done ? "" : "none";
        }
    };

    var _save = window.saveSurvey;
    window.saveSurvey = function () {
        if (_save) _save.apply(this, arguments);
        window.__htmlevalSvgTicks();
    };

    // Catch answers made outside saveSurvey and the initial restored state.
    setInterval(window.__htmlevalSvgTicks, 800);
    window.__htmlevalSvgTicks();
}

blockLookup["custom_component"] = CustomComponent;
