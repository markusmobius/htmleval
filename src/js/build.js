var saveSurvey = function () {
    if (readOnly) return;
    //we assume that the data is stored in tabData
    fetch("SERVERURL" + reviewerID, {
        method: 'PUT',
        headers: {
            'Content-type': 'text'
        },
        body: JSON.stringify(data)
    }).then((data) => {
        console.log("data saved");
    }).catch((error) => {
        console.log(error)
    });
};

// Per-field modification logging. For every field we record the UTC timestamp
// (ISO 8601) of when it was last modified, stored alongside the answers under
// data["timestamps"]. The timestamp key mirrors the field id but replaces the
// last id component (the answer tag) with "timestamp", e.g. an answer stored at
// ["row_1", "sentiment"] is timestamped at ["row_1", "timestamp"].
var timestampKey = function (fieldId) {
    try {
        var parsed = JSON.parse(fieldId);
        if (Array.isArray(parsed) && parsed.length > 0) {
            parsed[parsed.length - 1] = "timestamp";
            return JSON.stringify(parsed);
        }
    } catch (e) { }
    return fieldId;
};

var recordFieldTimestamp = function (fieldId) {
    if (!data["timestamps"]) data["timestamps"] = {};
    data["timestamps"][timestampKey(fieldId)] = new Date().toISOString();
};

var clearFieldTimestamp = function (fieldId) {
    if (data["timestamps"]) delete data["timestamps"][timestampKey(fieldId)];
};

// Signal Management
var activeSignal = null;
var signalListeners = []; // Objects { element: element, listeners: ["sig1", ...] }

var emitSignal = function (signal) {
    activeSignal = signal;
    signalListeners.forEach(function (item) {
        // An item matches when a signal is active and the item listens for it.
        var match = activeSignal !== null && item.listeners.includes(activeSignal);
        if (item.highlight === true) {
            // Highlight listeners: toggle the highlight class.
            item.element.classList.toggle("signal-highlight", match);
        } else {
            // Visibility listeners: show only the matching ones.
            item.element.style.display = match ? "" : "none";
        }
    });
}

var registerSignal = function (element, blockData, emitterElement = null) {
    // Handle Emitter
    if (blockData.signal) {
        var target = emitterElement || element;
        target.addEventListener('click', function (e) {
            e.stopPropagation();
            emitSignal(blockData.signal);
        });
    }

    // Handle Listener
    if (blockData.listeners && blockData.listeners.length > 0) {
        signalListeners.push({
            element: element,
            listeners: blockData.listeners,
            highlight: blockData["content"]["highlight"]
        });
    }
}

var completion = function (blockID, completed, total) {
    if (total == 0) {
        document.getElementById("completedstatus").innerHTML = "100% completed";
    }
    else {
        document.getElementById("completedstatus").innerHTML = Math.floor(100 * completed / total) + "% completed";
    }
}

// Signal-linked completion coloring. Lets an element (e.g. a thread header in one
// column) be colored green/red based on the completion of question blocks that
// share its signal (and live in another column, linked only by signal name).
// Untouched/partial questions show NO color, so nothing is highlighted by default.
var signalColorElems = {};   // signal -> [element]
var signalCompletion = {};   // signal -> { blockID: { done, total, hasNo } }

var recolorSignal = function (signal) {
    var m = signalCompletion[signal] || {};
    var done = 0, total = 0, anyNo = false;
    for (var k in m) { done += m[k].done; total += m[k].total; if (m[k].hasNo) anyNo = true; }
    (signalColorElems[signal] || []).forEach(function (el) {
        // Color the background (override .thread-content's gray background). Untouched
        // or partially-answered groups get no color, so nothing is highlighted by default.
        if (total === 0 || done < total) {
            el.style.backgroundColor = "";
            return;
        }
        el.style.backgroundColor = anyNo ? "#f8d7da" : "#d1e7dd";
    });
};

var registerSignalColor = function (signal, element) {
    if (!signal) return;
    (signalColorElems[signal] = signalColorElems[signal] || []).push(element);
    recolorSignal(signal);
};

var reportSignalCompletion = function (signal, blockID, done, total, hasNo) {
    if (!signal) return;
    var m = signalCompletion[signal] = (signalCompletion[signal] || {});
    m[blockID] = { done: done, total: total, hasNo: hasNo };
    recolorSignal(signal);
};

//populate survey when loading
var blocks = [];
var loadSurvey = async function () {
    try {
        var response = await fetch(this.serverURL + reviewerID);
    }
    catch (e) {
        console.log("network is down");
        document.getElementById("completedstatus").innerHTML = "SERVER UNAVAILABLE";
        return;
    }
    if (!response.ok) {
        console.log("no stored data");
        data = {
            "active": {},
            "variables": this.dataDefaults,
            "timestamps": {}
        };
    }
    else {
        var text = await response.text();
        data = JSON.parse(text);
        console.log("stored data retrieved");
    }
    //ensure the per-field timestamp log exists (backward compatibility)
    if (!data["timestamps"]) data["timestamps"] = {};
    //now build the survey
    var root = document.getElementById("rootblock");
    var rootID = blocks.length;
    blocks.push(null);
    blocks[rootID] = new blockLookup[rootBlock["type"]](root, rootBlock, this, rootID);
};

// Make any element with class "zoomable-svg" pan/zoomable. The element should
// contain a single <svg> and optional buttons carrying data-zoom="in|out|reset".
var initZoomableSVGs = function () {
    document.querySelectorAll(".zoomable-svg").forEach(function (container) {
        if (container.dataset.zoomInit === "1") return;
        container.dataset.zoomInit = "1";
        var svg = container.querySelector("svg");
        if (!svg) return;
        var state = { scale: 1, tx: 0, ty: 0 };
        var apply = function () {
            svg.style.transformOrigin = "0 0";
            svg.style.transform = "translate(" + state.tx + "px," + state.ty + "px) scale(" + state.scale + ")";
        };
        // Scale around a point (cx,cy) in container coordinates so it stays put.
        var zoomAt = function (factor, cx, cy) {
            var newScale = Math.min(8, Math.max(0.2, state.scale * factor));
            var ratio = newScale / state.scale;
            state.tx = cx - ratio * (cx - state.tx);
            state.ty = cy - ratio * (cy - state.ty);
            state.scale = newScale;
            apply();
        };
        container.querySelectorAll("[data-zoom]").forEach(function (btn) {
            btn.addEventListener("click", function (e) {
                e.preventDefault();
                e.stopPropagation();
                var dir = btn.getAttribute("data-zoom");
                if (dir === "reset") { state.scale = 1; state.tx = 0; state.ty = 0; apply(); return; }
                var rect = container.getBoundingClientRect();
                zoomAt(dir === "in" ? 1.2 : 1 / 1.2, rect.width / 2, rect.height / 2);
            });
        });
        container.addEventListener("wheel", function (e) {
            e.preventDefault();
            var rect = container.getBoundingClientRect();
            zoomAt(e.deltaY < 0 ? 1.1 : 1 / 1.1, e.clientX - rect.left, e.clientY - rect.top);
        }, { passive: false });
        // Click-drag to pan.
        var dragging = false, sx = 0, sy = 0;
        container.addEventListener("mousedown", function (e) {
            dragging = true; sx = e.clientX; sy = e.clientY;
            container.style.cursor = "grabbing";
            e.preventDefault();
        });
        window.addEventListener("mousemove", function (e) {
            if (!dragging) return;
            state.tx += e.clientX - sx;
            state.ty += e.clientY - sy;
            sx = e.clientX; sy = e.clientY;
            apply();
        });
        window.addEventListener("mouseup", function () {
            dragging = false;
            container.style.cursor = "grab";
        });
        container.style.cursor = "grab";
        apply();
    });
};


(async () => {
    await loadSurvey();
    if (readOnly) {
        document.querySelectorAll('select').forEach(function(el) { el.disabled = true; });
        document.querySelectorAll('input[type="checkbox"]').forEach(function(el) { el.disabled = true; });
    }
    initZoomableSVGs();
})();
