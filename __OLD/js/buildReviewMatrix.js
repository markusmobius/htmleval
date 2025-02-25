//tabData holds all the data across tabs
//each element in the array has a uuid and a data section
//data section consists of an array of objects with compoundID and variables with values
//example: single tab, containing one object 
//[{"active": 0,"data":[{"compoundID":{something},"values":{"varname1":"value1","varname2":"value2"}]}]

var fullData={
    "active":0, 
    "data":[]
};

var matrix=MATRIXDATA;
var instructions = INSTRUCTIONS;

var updateCompleteStatus = function() {
    var completed = 0;
    for (var i = 0; i < fullData["data"].length; i++) {
        var subcompleted = true;
        for (var key in fullData["data"][i]["values"]) {
            if (fullData["data"][i]["values"][key] == "") {
                subcompleted = false;
            }
        }
        document.getElementById("tab" + (i + 1) + "-tab").classList.remove("bg-warning-subtle");
        if (subcompleted) {
            document.getElementById("tab" + (i + 1) + "-tab").classList.add("bg-success-subtle");
            completed++;
        }
    }
    document.getElementById("completedstatus").innerHTML = Math.round(100 * completed / (fullData["data"].length + 0.0000001)) + "% completed";
    document.getElementById("tab" + fullData["active"] + "-tab").classList.remove("bg-success-subtle");
    document.getElementById("tab" + fullData["active"] + "-tab").classList.add("bg-warning-subtle");
}

var buildTab = function(pane, i, tabData, is_active) {
    // Add text on top
    var h3 = document.createElement("h3");
    h3.innerHTML = matrix["tabs"][i]["header"];
    pane.appendChild(h3);

    // Create a container for the scrollable boxes
    var scrollableContainer = document.createElement("div");
    pane.appendChild(scrollableContainer);

    // Create the first scrollable box for "text"
    var scrollable1 = document.createElement("div");
    var articleHeader = document.createElement("h4");
    articleHeader.innerHTML = "Article";
    if (matrix["tabs"][i]["articles"]) {
        articleHeader.innerHTML = "Cluster Description";
    }
    scrollable1.appendChild(articleHeader);
    var paras = matrix["tabs"][i]["text"].split('\n');
    for (var j = 0; j < paras.length; j++) {
        var pnws = paras[j].trim();
        if (pnws != "") {
            var p = document.createElement("p");
            p.innerHTML = pnws;
            scrollable1.appendChild(p);
        }
    }

    // Check if "summary_text" exists and create the second scrollable box if it does
    if (matrix["tabs"][i]["summary_text"]) {
        scrollableContainer.className = "scrollable-container-two";
        scrollable1.className = "scrollable-box-two";
        scrollableContainer.appendChild(scrollable1);

        var scrollable2 = document.createElement("div");
        scrollable2.className = "scrollable-box-two";
        scrollableContainer.appendChild(scrollable2);
        var summaryHeader = document.createElement("h4");
        summaryHeader.innerHTML = "Summary";
        scrollable2.appendChild(summaryHeader);
        var summaryParas = matrix["tabs"][i]["summary_text"].split('\n');
        for (var j = 0; j < summaryParas.length; j++) {
            var pnws = summaryParas[j].trim();
            if (pnws != "") {
                var p = document.createElement("p");
                p.innerHTML = pnws;
                scrollable2.appendChild(p);
            }
        }
    } else if (matrix["tabs"][i]["articles"]) {
        scrollableContainer.className = "scrollable-container-two";
        scrollable1.className = "scrollable-box-two";
        scrollableContainer.appendChild(scrollable1);
    
        var tableContainer = document.createElement("div");
        tableContainer.className = "scrollable-box-two";
        scrollableContainer.appendChild(tableContainer);
        var tableHeader = document.createElement("h4");
        tableHeader.innerHTML = "Article Titles";
        tableContainer.appendChild(tableHeader);
    
        var table = document.createElement("table");
        table.className = "table table-bordered table-striped table-hover";
        tableContainer.appendChild(table);
    
        var thead = document.createElement("thead");
        table.appendChild(thead);
        var tr = document.createElement("tr");
        thead.appendChild(tr);
    
        var tbody = document.createElement("tbody");
        table.appendChild(tbody);
    
        var articleTitles = matrix["tabs"][i]["articles"];
        articleTitles.forEach(title => {
            var tr = document.createElement("tr");
            tbody.appendChild(tr);
            var td = document.createElement("td");
            td.innerHTML = title;
            tr.appendChild(td);
        });
    } else {
        scrollableContainer.className = "scrollable-container-one";
        scrollable1.className = "scrollable-box-one";
        scrollableContainer.appendChild(scrollable1);
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
    tr.appendChild(th);
    th.innerHTML = "Question";
    for (var j = 0; j < matrix["options"].length; j++) {
        th = document.createElement("th");
        tr.appendChild(th);
        th.innerHTML = matrix["options"][j]["text"];
    }
    var tbody = document.createElement("tbody");
    tbl.appendChild(tbody);
    for (var q = 0; q < matrix["questions"].length; q++) {
        var tr = document.createElement("tr");
        tbody.appendChild(tr);
        // Add the question
        var varname = matrix["questions"][q]["varname"];
        var td = document.createElement("td");
        tr.appendChild(td);
        td.innerHTML = matrix["questions"][q]["question"];
        // Now add the checkboxes
        var checkboxes = [];
        for (var j = 0; j < matrix["options"].length; j++) {
            td = document.createElement("td");
            tr.appendChild(td);
            var checkbox = document.createElement("input");
            td.appendChild(checkbox);
            if (matrix["options"][j]["value"] == tabData["values"][varname]) {
                checkbox.checked = true;
                tr.className = "table-" + matrix["options"][j]["css"];
            }
            checkbox.setAttribute("type", "checkbox");
            checkbox.setAttribute("css-selected", matrix["options"][j]["css"]);
            checkbox.setAttribute("value-selected", i + "|" + varname + "|" + matrix["options"][j]["value"]);
            // Now add the event listener
            checkbox.addEventListener("click", (e) => {
                var row = e.target.parentNode.parentNode;
                var columns = row.children;
                // Uncheck everything in that row
                for (var c = 0; c < columns.length; c++) {
                    var col = columns[c];
                    if (col.children.length > 0 && e.target.getAttribute("value-selected") != col.children[0].getAttribute("value-selected")) {
                        col.children[0].checked = false;
                    }
                }
                var valselected = e.target.getAttribute("value-selected").split('|');
                if (e.target.checked) {
                    fullData["data"][valselected[0]]["values"][valselected[1]] = valselected[2];
                    row.className = "table-" + e.target.getAttribute("css-selected");
                } else {
                    fullData["data"][valselected[0]]["values"][valselected[1]] = ""; // Set to empty string or default value
                    // Check if any checkbox in the row is still checked
                    var anyChecked = false;
                    for (var c = 0; c < columns.length; c++) {
                        var col = columns[c];
                        if (col.children.length > 0 && col.children[0].checked) {
                            anyChecked = true;
                            break;
                        }
                    }
                    if (!anyChecked) {
                        row.className = ""; // Remove the highlight if no checkboxes are checked
                    }
                }
                updateCompleteStatus();
                saveSurvey();
            });
            checkboxes.push(checkbox);
        }
    }
}

var build = function(savedData) {
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
        document.querySelector(".nav-link.active").classList.remove("active");
        e.target.classList.add("active");
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
        button.innerHTML = i + 1; // Adjust tab numbering to start from 1
        button.addEventListener("click", (e) => {
            document.querySelector(".nav-link.active").classList.remove("active");
            e.target.classList.add("active");
            fullData["active"] = parseInt(e.target.getAttribute("tabid"));
            saveSurvey();
            updateCompleteStatus();
        });
    }

    // Add the content for the other tabs
    for (var i = 0; i < matrix["tabs"].length; i++) {
        var pane = document.createElement("div");
        tabcontent.appendChild(pane);
        pane.className = fullData["active"] === i + 1 ? "tab-pane active" : "tab-pane";
        pane.setAttribute("id", "tab" + (i + 1));
        pane.setAttribute("role", "tabpanel");
        pane.setAttribute("aria-labelledby", "tab" + (i + 1) + "-tab");

        if (savedData["data"][i] != undefined) {
            var tabData = savedData["data"][i];
        } else {
            var tabData = {
                "compoundID": matrix["tabs"][i]["compoundID"],
                "values": {}
            };
            // Add default value for all variables
            for (var q = 0; q < matrix["questions"].length; q++) {
                tabData["values"][matrix["questions"][q]["varname"]] = "";
            }
        }
        fullData["data"].push(tabData);
        console.log(fullData);
        buildTab(pane, i, tabData, i + 1 == savedData["active"]);
    }

    // Set active tab based on savedData
    document.getElementById("tab" + fullData["active"] + "-tab").click();
}