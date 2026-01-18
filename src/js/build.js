var saveSurvey = function () {
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

// Signal Management
var activeSignal = null;
var signalListeners = []; // Objects { element: element, listeners: ["sig1", ...] }

var emitSignal = function (signal) {
    activeSignal = signal;
    signalListeners.forEach(function (item) {
        if (activeSignal === null) {
            item.element.classList.remove("signal-highlight");
        } else {
            if (item.listeners.includes(activeSignal)) {
                item.element.classList.add("signal-highlight");
            } else {
                item.element.classList.remove("signal-highlight");
            }
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
            listeners: blockData.listeners
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
            "variables": this.dataDefaults
        };
    }
    else {
        var text = await response.text();
        data = JSON.parse(text);
        console.log("stored data retrieved");
    }
    //now build the survey
    var root = document.getElementById("rootblock");
    blocks.push(new blockLookup[rootBlock["type"]](root, rootBlock, this, blocks.length));
};


(async () => {
    await loadSurvey();
})();
