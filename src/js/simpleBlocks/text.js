class SimpleText {

    constructor(root, block, parent, blockID) {
        this.blockID = blockID;
        this.parent = parent;
        //keep track of completion
        this.completed = [0, 0];

        // Create wrapper for the whole block
        var container = document.createElement("div");
        container.className = "text-content";
        root.appendChild(container);

        var div = document.createElement("div");
        container.appendChild(div);
        if (block["content"]["verticalHeight"]) {
            div.style.overflowY = "auto";
            div.style.height = block["content"]["verticalHeight"] + "vh";
        }
        //write title (if exists)
        if (block["content"]["title"] != undefined) {
            var h = document.createElement("h" + block["content"]["title"]["size"]);
            div.appendChild(h);
            h.innerHTML = block["content"]["title"]["text"];
        }
        //write body (if exists)
        if (block["content"]["body"] != undefined) {
            if (block["content"]["body"]["is_table"] == true) {
                var tbl = document.createElement("table");
                tbl.className = "table table-striped table-hover";
                container.appendChild(tbl);
                var tbody = document.createElement("tbody");
                tbl.appendChild(tbody);
                for (var i = 0; i < block["content"]["body"]["text"].length; i++) {
                    var row = document.createElement("tr");
                    tbody.appendChild(row);
                    var rowData = block["content"]["body"]["text"][i];
                    // If rowData is an array, create a cell for each item
                    if (Array.isArray(rowData)) {
                        for (var j = 0; j < rowData.length; j++) {
                            var td = document.createElement("td");
                            row.appendChild(td);
                            td.innerHTML = rowData[j];
                        }
                    } else {
                        // Fallback: treat as single column
                        var td = document.createElement("td");
                        row.appendChild(td);
                        td.innerHTML = rowData;
                    }
                }
            }
            else {
                for (var i = 0; i < block["content"]["body"]["text"].length; i++) {
                    var p = document.createElement("p");
                    div.appendChild(p);
                    p.innerHTML = block["content"]["body"]["text"][i];
                }
            }
        }

        // Register Signal
        registerSignal(container, block);

        this.completion();
    }

    //completion method
    completion() {
        this.parent.completion(this.blockID, this.completed[0], this.completed[1]);
    }
}


//add class to lookup dictionary
blockLookup["text"] = SimpleText;