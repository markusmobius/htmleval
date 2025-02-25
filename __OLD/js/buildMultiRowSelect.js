//tabData holds all the data across tabs
//each element in the array has a uuid and a data section
//data section consists of an array of objects with compoundID and variables with values
//example: single tab, containing one object 
//[{"active": 0,"data":[{"compoundID":{something},"values":{"varname1":"value1","varname2":"value2"}]}]

var fullData={
    "active" : 0,
    "data":[]
};


var matrix=MULTIROWDATA;
var instructions = INSTRUCTIONS;
console.log(matrix);

var compareCompoundID = function(id1, id2) {
    if (id1 === id2) return true;
    if (typeof id1 !== 'object' || typeof id2 !== 'object') return false;
    var keys1 = Object.keys(id1);
    var keys2 = Object.keys(id2);
    if (keys1.length !== keys2.length) return false;
    for (var key of keys1) {
        if (id1[key] !== id2[key]) return false;
    }
    return true;
};

var updateCompleteStatus = function() {
    var completed = 0;
    var totalRows = 0;

    for (var i = 0; i < matrix["tabs"].length; i++) {
        var tabCompleted = true;
        var tabRows = matrix["tabs"][i]["rows"];
        totalRows += tabRows.length;

        for (var j = 0; j < tabRows.length; j++) {
            var compoundID = tabRows[j]["compoundID"];
            var rowData = fullData["data"].find(row => compareCompoundID(row["compoundID"], compoundID));

            if (rowData) {
                for (var key in rowData["values"]) {
                    if (rowData["values"][key] === "") {
                        tabCompleted = false;
                        break;
                    }
                }
            } else {
                tabCompleted = false;
                break;
            }
        }

        var tabButton = document.getElementById("tab" + i + "-tab");
        if (tabButton) {
            tabButton.classList.remove("bg-warning-subtle");
            if (tabCompleted) {
                tabButton.classList.add("bg-success-subtle");
                completed += tabRows.length;
            } else {
                tabButton.classList.remove("bg-success-subtle");
            }
        }
    }

    var percentageCompleted = Math.round(100 * completed / (totalRows + 0.0000001));
    document.getElementById("completedstatus").innerHTML = percentageCompleted + "% completed";
    var activeTabButton = document.getElementById("tab" + fullData["active"] + "-tab");
    if (activeTabButton) {
        activeTabButton.classList.remove("bg-success-subtle");
        activeTabButton.classList.add("bg-warning-subtle");
    }
}

var buildTab = function(pane, i, tabData, is_active) {
    // if there is text to add, at it here, just regular font
    if (matrix["tabs"][i]["header"]) {
        var header = document.createElement("h3");
        header.innerHTML = matrix["tabs"][i]["header"];
        pane.appendChild(header);
    }
    // if there is text, add it
    if (matrix["tabs"][i]["text"]) {
        var text = document.createElement("p");
        text.innerHTML = matrix["tabs"][i]["text"];
        pane.appendChild(text);
    }

    var tbl = document.createElement("table");
    pane.appendChild(tbl);
    tbl.className = "table table-striped table-hover";
    tbl.setAttribute("border", 1);

    var thead = document.createElement("thead");
    tbl.appendChild(thead);
    var tr = document.createElement("tr");
    thead.appendChild(tr);
    tr.style.textAlign = "left";

    var th = document.createElement("th");
    th.style.width = (100-matrix['questions'].length*20) + "%";
    tr.appendChild(th);
    th.innerHTML = matrix["tabs"][i]["table_header"];

    // Add the new column header if it exists
    if (matrix["tabs"][i]["column_header"]) {
        th = document.createElement("th");
        tr.appendChild(th);
        th.innerHTML = matrix["tabs"][i]["column_header"];
    }

    // Add the questions titles as headers
    for (var j = 0; j < matrix["questions"].length; j++) {
        th = document.createElement("th");
        tr.appendChild(th);
        th.innerHTML = matrix["questions"][j]["question"];
    }

    var tbody = document.createElement("tbody");
    tbl.appendChild(tbody);

    // Create Body of Table
    for (var q = 0; q < matrix["tabs"][i]["rows"].length; q++) {
        var tr = document.createElement("tr");
        tbody.appendChild(tr);

        // Add the fragment
        var compoundID = matrix["tabs"][i]["rows"][q]["compoundID"];
        var compoundID_str = JSON.stringify(compoundID);
        var td = document.createElement("td");
        tr.appendChild(td);
        td.innerHTML = matrix["tabs"][i]["rows"][q]["text"];
        td.className = "table-" + matrix["tabs"][i]["rows"][q]["css"];

        // Add the new column data if it exists
        if (matrix["tabs"][i]["column"]) {
            td = document.createElement("td");
            tr.appendChild(td);
            td.innerHTML = matrix["tabs"][i]["column"][q];
        }

        // Add the select boxes
        for (var j = 0; j < matrix["questions"].length; j++) {
            var td = document.createElement("td");
            tr.appendChild(td);
            var select = document.createElement("select");
            td.appendChild(select);
            select.className = "form-select";
            var varname = matrix["questions"][j]["varname"];
            select.setAttribute("varname", varname);
            select.setAttribute("compoundID", compoundID_str + '|' + varname);
            select.addEventListener("change", (e) => {
                var targetCompoundID_str = e.target.getAttribute("compoundID").split('|')[0];
                var targetCompoundID = JSON.parse(targetCompoundID_str);
                var rowIndex = fullData["data"].findIndex(row => JSON.stringify(row["compoundID"]) === targetCompoundID_str);
                if (rowIndex !== -1) {
                    fullData["data"][rowIndex]["values"][e.target.getAttribute("varname")] = e.target.value;
                    saveSurvey();
                    updateCompleteStatus();
                }

                // Highlight the cell based on the selected value
                var selectedOption = matrix["questions"][j]["options"].find(option => option["value"] === e.target.value);
                if (selectedOption) {
                    e.target.parentElement.className = selectedOption["css"];
                } else {
                    e.target.parentElement.classList.remove("table-success", "table-danger");
                }
            });

            var option = document.createElement("option");
            select.appendChild(option);
            option.value = "";
            option.innerHTML = "Select";
            for (var k = 0; k < matrix["questions"][j]["options"].length; k++) {
                var option = document.createElement("option");
                select.appendChild(option);
                option.value = matrix["questions"][j]["options"][k]["value"];
                option.innerHTML = matrix["questions"][j]["options"][k]["text"];
            }

            // For each question, check if the value is already saved in tabData. If so, set the value.
            var rowData = tabData.find(row => JSON.stringify(row["compoundID"]) === compoundID_str);
            if (rowData && rowData["values"][varname] !== undefined) {
                select.value = rowData["values"][varname];

                // Highlight the cell based on the saved value
                var savedOption = matrix["questions"][j]["options"].find(option => option["value"] === select.value);
                if (savedOption) {
                    td.className = savedOption["css"];
                } else {
                    td.classList.remove("table-success", "table-danger");
                }
            }
        }
    }
}

var build = function(savedData) {
    console.log(savedData);

    // Set active tab to 0 (instructions) if it's the first time opening
    if (savedData["active"] === undefined || savedData["active"] === null) {
        fullData["active"] = 0;
    } else {
        fullData["active"] = savedData["active"];
    }

    var root = document.getElementById("tabs");

    // Add tabs
    var ul = document.createElement("ul");
    root.appendChild(ul);
    ul.className = "nav nav-tabs";
    ul.setAttribute("role", "tablist");

    // Add instructions tab
    var li = document.createElement("li");
    ul.appendChild(li);
    li.className = "nav-item";
    li.setAttribute("role", "presentation");
    var button = document.createElement("button");
    li.appendChild(button);
    button.setAttribute("data-bs-toggle", "tab");
    button.setAttribute("id", "tab0-tab");
    button.setAttribute("tabid", 0);
    button.setAttribute("data-bs-target", "#tab0");
    button.setAttribute("type", "button");
    button.setAttribute("role", "tab");
    button.setAttribute("aria-controls", "instructions");
    button.setAttribute("aria-selected", fullData["active"] === 0);
    button.className = fullData["active"] === 0 ? "nav-link active" : "nav-link";
    button.innerHTML = "Instructions";
    button.addEventListener("click", (e) => {
        fullData["active"] = 0;
        saveSurvey();
        updateCompleteStatus();
    });

    // Add the content for the instructions tab
    var tabcontent = document.createElement("div");
    root.appendChild(tabcontent);
    tabcontent.className = "tab-content bg-light";
    var pane = document.createElement("div");
    tabcontent.appendChild(pane);
    pane.className = fullData["active"] === 0 ? "tab-pane active" : "tab-pane";
    pane.setAttribute("id", "tab0");
    pane.setAttribute("role", "tabpanel");
    pane.setAttribute("aria-labelledby", "tab0-tab");

    var instructionsContent = document.createElement("div");
    instructionsContent.className = "instructions-content";
    pane.appendChild(instructionsContent);
    for (var j = 0; j < instructions.length; j++) {
        var p = document.createElement("p");
        p.innerHTML = instructions[j];
        instructionsContent.appendChild(p);
    }

    // Add the other tabs
    for (var i = 0; i < matrix["tabs"].length; i++) {
        var li = document.createElement("li");
        ul.appendChild(li);
        li.className = "nav-item";
        li.setAttribute("role", "presentation");
        var button = document.createElement("button");
        li.appendChild(button);
        button.setAttribute("data-bs-toggle", "tab");
        button.setAttribute("id", "tab" + (i + 1) + "-tab");
        button.setAttribute("tabid", i + 1);
        button.setAttribute("data-bs-target", "#tab" + (i + 1));
        button.setAttribute("type", "button");
        button.setAttribute("role", "tab");
        button.setAttribute("aria-controls", i + 1);
        button.setAttribute("aria-selected", fullData["active"] === i + 1);
        button.className = fullData["active"] === i + 1 ? "nav-link active" : "nav-link";
        button.innerHTML = matrix["tabs"][i]["name"]; // Set to appropriate name
        button.addEventListener("click", (e) => {
            fullData["active"] = parseInt(e.target.getAttribute("tabid"));
            saveSurvey();
            updateCompleteStatus();
        });
    }

    // Now add the content
    for (var i = 0; i < matrix["tabs"].length; i++) {
        var pane = document.createElement("div");
        tabcontent.appendChild(pane);
        pane.className = fullData["active"] === i + 1 ? "tab-pane active" : "tab-pane";
        pane.setAttribute("id", "tab" + (i + 1));
        pane.setAttribute("role", "tabpanel");
        pane.setAttribute("aria-labelledby", "tab" + (i + 1) + "-tab");

        var tabData = [];

        for (var j = 0; j < matrix["tabs"][i]["rows"].length; j++) {
            var row = matrix["tabs"][i]["rows"][j];
            var isSaved = false;

            // Check if data for the current row is already saved
            for (var k = 0; k < savedData["data"].length; k++) {
                if (compareCompoundID(savedData["data"][k]["compoundID"], row["compoundID"])) {
                    isSaved = true;
                    tabData.push(savedData["data"][k]);
                    break;
                }
            }

            if (!isSaved) {
                var rowData = {
                    "compoundID": row["compoundID"],
                    "values": {}
                };

                // Add default value for all variables
                for (var q = 0; q < matrix["questions"].length; q++) {
                    rowData["values"][matrix["questions"][q]["varname"]] = "";
                }

                tabData.push(rowData);
            }
        }

        // Add the tab data to fullData
        fullData["data"] = fullData["data"].concat(tabData);

        console.log(fullData);
        buildTab(pane, i, tabData, i + 1 == savedData["active"]);
    }

    // Set active tab based on savedData
    document.getElementById("tab" + fullData["active"] + "-tab").click();
}
