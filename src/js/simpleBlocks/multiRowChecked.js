class MultiRowChecked {

    constructor(root, block, parent, blockID) {
        this.blockID = blockID;
        this.parent = parent;
        this.completed = [0, 0];

        // Use custom_colours flag if present, default to false
        const custom_colours = block["content"]["custom_colours"] === true;

        // Construct table
        var tbl = document.createElement("table");
        tbl.className = "table table-striped table-hover";
        tbl.setAttribute("border", 1);
        root.appendChild(tbl);

        // Add header
        var thead = document.createElement("thead");
        var header_row = document.createElement("tr");
        thead.appendChild(header_row);
        tbl.appendChild(thead);

        var th = document.createElement("th");
        th.innerHTML = block["content"]["rowLabel"];
        let options_length = custom_colours
            ? (block["content"]["rows"][0]?.options?.length || 0)
            : block["content"]["options"].length;
        var width = 100 - options_length * 10;
        if (width < 50) width = 50;
        th.style.width = width + "%";
        header_row.appendChild(th);

        // Header columns
        if (custom_colours) {
            let firstOptions = block["content"]["rows"][0]?.options || [];
            for (var k = 0; k < firstOptions.length; k++) {
                th = document.createElement("th");
                th.innerHTML = firstOptions[k]["label"];
                header_row.appendChild(th);
            }
        } else {
            for (var k = 0; k < block["content"]["options"].length; k++) {
                th = document.createElement("th");
                th.innerHTML = block["content"]["options"][k]["label"];
                header_row.appendChild(th);
            }
        }

        // Add rows
        var tbody = document.createElement("tbody");
        tbl.appendChild(tbody);
        for (var i = 0; i < block["content"]["rows"].length; i++) {
            var row = document.createElement("tr");
            tbody.appendChild(row);
            var td = document.createElement("td");
            if (custom_colours && block["content"]["rows"][i].highlight) {
                td.className = "table-" + block["content"]["rows"][i].highlight;
            }
            row.appendChild(td);
            td.innerHTML = block["content"]["rows"][i]["text"];

            // Build fullId
            var fullId = ["", ""];
            for (var key in block["content"]["rows"][i]["id"]) {
                fullId[key] = block["content"]["rows"][i]["id"][key];
            }
            for (var key in block["content"]["id"]) {
                fullId[key] = block["content"]["id"][key];
            }
            fullId = JSON.stringify(fullId);

            // Check for default value in three places:
            // 1. The block content (directly from Python)
            // 2. The data.variables (from JS)
            var oldValue = null;
            
            // Check if there's a default value set in the row data
            if (block["content"]["rows"][i].hasOwnProperty("default_value")) {
                oldValue = block["content"]["rows"][i]["default_value"];
                // Also set it in data.variables for consistency
                data.variables[fullId] = oldValue;
            }
            // Otherwise check the existing data variables
            else if (data.variables[fullId]) {
                oldValue = data.variables[fullId];
            }

            // Use row-specific or table-level options
            var options = custom_colours
                ? block["content"]["rows"][i]["options"]
                : block["content"]["options"];

            // Store references to the created td cells and their corresponding option colors
            let optionCells = [];
            for (var k = 0; k < options.length; k++) {
                var td = document.createElement("td");
                row.appendChild(td);
                var input = document.createElement("input");
                td.appendChild(input);
                input.setAttribute("type", "checkbox");
                input.setAttribute("fullid", fullId);
                input.setAttribute("id", fullId + "|" + options[k]["value"]);
                input.setAttribute("order", k + 1);
                input.setAttribute("varvalue", options[k]["value"]);
                if (options[k]["color"] != undefined) {
                    input.setAttribute("color", options[k]["color"]);
                }
                if (oldValue == options[k]["value"]) {
                    input.checked = true;
                    this.completed[0]++;
                    // Apply coloring immediately
                    if (options[k]["color"]) {
                        if (custom_colours) {
                            // For custom colors mode, set color on this cell
                            td.className = "table-" + options[k]["color"];
                        } else {
                            // For standard mode, set color on the whole row
                            row.className = "table-" + options[k]["color"];
                        }
                    }
                } else {
                    input.checked = false;
                }
                 optionCells.push({td, input, color: options[k]["color"]});
                input.addEventListener('change', (e) => {
                    if (!e.target.checked) {
                        // Allow unchecking - remove stored value and highlighting
                        delete data["variables"][e.target.getAttribute("fullid")];
                        var row = e.target.parentElement.parentElement;
                        
                        if (custom_colours) {
                            // Remove color from all checkbox cells in this row
                            var children = row.childNodes;
                            var array = Array.prototype.slice.call(children);
                            for (var m = 1; m < array.length; m++) {
                                array[m].className = "";
                            }
                        } else {
                            // Remove color from the whole row
                            row.className = "";
                        }
                        
                        this.completed[0]--;
                        this.completion();
                        saveSurvey();
                        return;
                    }
                    
                    if (data["variables"][e.target.getAttribute("fullid")] == undefined) {
                        this.completed[0]++;
                    }
                    data["variables"][e.target.getAttribute("fullid")] = e.target.getAttribute("varvalue");
                    var row = e.target.parentElement.parentElement;
                    var children = row.childNodes;
                    var array = Array.prototype.slice.call(children);
                    for (var m = 1; m < array.length; m++) {
                        var input = array[m].firstChild;
                        if (input.checked && input.getAttribute("order") != e.target.getAttribute("order")) {
                            input.checked = false;
                            if (custom_colours) array[m].className = "";
                        }
                    }
                    var color = e.target.getAttribute("color");
                    if (custom_colours) {
                        // Set color for ALL checkbox cells in this row
                        for (var m = 1; m < array.length; m++) {
                            if (color != undefined) {
                                array[m].className = "table-" + color;
                            } else {
                                array[m].className = "";
                            }
                        }
                    } else {
                        // Set color for the whole row
                        if (color != undefined) {
                            row.className = "table-" + color;
                        } else {
                            row.className = "";
                        }
                    }
                    this.completion();
                    saveSurvey();
                });
            }
            // After all checkboxes are created, apply highlight if any is checked (for custom_colours)
            if (custom_colours) {
                let checkedIdx = optionCells.findIndex(cell => cell.input.checked);
                if (checkedIdx !== -1 && optionCells[checkedIdx].color) {
                    for (let m = 0; m < optionCells.length; m++) {
                        optionCells[m].td.className = "table-" + optionCells[checkedIdx].color;
                    }
                }
            } else {
                // Apply row coloring for standard mode during initialization
                let checkedIdx = optionCells.findIndex(cell => cell.input.checked);
                if (checkedIdx !== -1 && optionCells[checkedIdx].color) {
                    row.className = "table-" + optionCells[checkedIdx].color;
                }
            }
            this.completed[1]++;
        }
        this.completion();
    }

    completion() {
        this.parent.completion(this.blockID, this.completed[0], this.completed[1]);
    }
}

blockLookup["multi_row_checked"] = MultiRowChecked;