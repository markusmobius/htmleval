class MultiRowChecked {

    constructor(root, block, parent, blockID) {
        this.blockID = blockID;
        this.parent = parent;
        //keep track of completion
        this.completed = [0, 0];
        //construct table
        var tbl = document.createElement("table");
        tbl.className = "table table-striped table-hover";
        tbl.setAttribute("border", 1);
        root.appendChild(tbl);
        //add header
        var thead = document.createElement("thead");
        var header_row = document.createElement("tr");
        thead.appendChild(header_row);
        tbl.appendChild(thead);
        var th = document.createElement("th");
        th.innerHTML = block["content"]["rowLabel"];
        var width = 100 - block["content"]["options"].length * 10;
        if (width < 50) {
            width = 50;
        }
        th.style.width = width + "%";
        header_row.appendChild(th);
        for (var k = 0; k < block["content"]["options"].length; k++) {
            th = document.createElement("th");
            th.innerHTML = block["content"]["options"][k]["label"];
            header_row.appendChild(th);
        }
        //now add the rows    
        var tbody = document.createElement("tbody");
        tbl.appendChild(tbody);
        for (var i = 0; i < block["content"]["rows"].length; i++) {
            var row = document.createElement("tr");
            tbody.appendChild(row);
            var td = document.createElement("td");
            row.appendChild(td);
            td.innerHTML = block["content"]["rows"][i]["text"];
            //now create the check boxes element
            var fullId = ["", ""];
            for (var key in block["content"]["rows"][i]["id"]) {
                fullId[key] = block["content"]["rows"][i]["id"][key];
            }
            for (var key in block["content"]["id"]) {
                fullId[key] = block["content"]["id"][key];
            }
            fullId = JSON.stringify(fullId);
            var oldValue = data["variables"][fullId];
            for (var k = 0; k < block["content"]["options"].length; k++) {
                var td = document.createElement("td");
                row.appendChild(td);
                var input = document.createElement("input");
                td.appendChild(input);
                input.setAttribute("type", "checkbox");
                input.setAttribute("fullid", fullId);
                input.setAttribute("id", fullId + "|" + block["content"]["options"][k]["value"])
                input.setAttribute("order", k + 1);
                input.setAttribute("varvalue", block["content"]["options"][k]["value"]);
                if (block["content"]["options"][k]["color"] != undefined) {
                    input.setAttribute("color", block["content"]["options"][k]["color"]);
                }
                if (oldValue == block["content"]["options"][k]["value"]) {
                    input.checked = true;
                    this.completed[0]++;
                    if (block["content"]["options"][k]["color"] != undefined) {
                        row.className = "table-" + block["content"]["options"][k]["color"];
                    }
                }
                else {
                    input.checked = false;
                }
                input.addEventListener('change', (e) => {
                    if (!e.target.checked) {
                        e.target.checked = true;
                        return;
                    }
                    if (data["variables"][e.target.getAttribute("fullid")] == undefined) {
                        this.completed[0]++;
                    }
                    data["variables"][e.target.getAttribute("fullid")] = e.target.getAttribute("varvalue");
                    var row = e.target.parentElement.parentElement;
                    //uncheck everything
                    var children = row.childNodes;
                    var array = Array.prototype.slice.call(children);
                    for (k = 1; k < array.length; k++) {
                        var input = array[k].firstChild;
                        if (input.checked && input.getAttribute("order") != e.target.getAttribute("order")) {
                            input.checked = false;
                        }
                    }
                    var color = e.target.getAttribute("color");
                    if (color != undefined) {
                        row.className = "table-" + color;
                    }
                    else {
                        row.className = "";
                    }
                    this.completion();
                    saveSurvey();
                });
            }
            this.completed[1]++;
        }
        // Register Signal
        registerSignal(tbl, block);

        this.completion();
    }

    //completion method
    completion() {
        this.parent.completion(this.blockID, this.completed[0], this.completed[1]);
    }
}


//add class to lookup dictionary
blockLookup["multi_row_checked"] = MultiRowChecked;