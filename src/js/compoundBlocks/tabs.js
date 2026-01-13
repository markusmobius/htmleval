class Tabs {

    constructor(root, block, parent, blockID) {
        //generate a unique tab ID
        this.blockID = blockID;
        this.parent = parent;
        this.tabBlockAssignment = {};
        //keep track of completion
        this.completed = {};
        //construct table

        var container = document.createElement("div");
        root.appendChild(container);

        var ul = document.createElement("ul");
        container.appendChild(ul);
        ul.className = "nav nav-tabs";
        ul.setAttribute("role", "tablist");
        if (data["active"][this.blockID] == undefined) {
            data["active"][this.blockID] = 0;
        }
        for (var i = 0; i < block["content"].length; i++) {
            var li = document.createElement("li");
            ul.appendChild(li);
            li.className = "nav-item";
            li.setAttribute("role", "presentation");
            var button = document.createElement("button");
            li.appendChild(button);
            button.setAttribute("data-bs-toggle", "tab");
            button.setAttribute("id", this.blockID + ":" + i);
            button.setAttribute("taborder", i);
            button.setAttribute("data-bs-target", "#" + this.blockID + ":" + i + "-tab");
            button.setAttribute("type", "button");
            button.setAttribute("role", "tab");
            button.setAttribute("aria-controls", i);
            if (data["active"][this.blockID] == i) {
                button.setAttribute("aria-selected", "true");
                button.className = "nav-link active bg-warning-subtle";
            }
            else {
                button.setAttribute("aria-selected", "false");
                button.className = "nav-link";
            }
            button.innerHTML = block["content"][i]["tabName"];
            button.addEventListener("click", (e) => {
                //remove active class from currently active tab
                var oldButton = document.getElementById(this.blockID + ":" + data["active"][this.blockID]);
                oldButton.classList.remove("bg-warning-subtle");
                var oldStatus = [0, 0];
                for (var key in this.tabBlockAssignment) {
                    if (this.tabBlockAssignment[key] == data["active"][this.blockID]) {
                        if (this.completed[key] !== undefined) {
                            oldStatus = this.completed[key];
                        }
                    }
                }
                if (oldStatus[1] > 0 && oldStatus[0] == oldStatus[1]) {
                    oldButton.classList.remove("bg-primary-subtle");
                    oldButton.classList.add("bg-success-subtle");
                }
                if (oldStatus[1] > 0 && oldStatus[0] < oldStatus[1]) {
                    oldButton.classList.remove("bg-success-subtle");
                    oldButton.classList.add("bg-primary-subtle");
                }
                data["active"][this.blockID] = parseInt(e.target.getAttribute("taborder"));
                var newButton = document.getElementById(this.blockID + ":" + data["active"][this.blockID]);
                newButton.classList.remove("bg-success-subtle");
                newButton.classList.remove("bg-primary-subtle");
                newButton.classList.add("bg-warning-subtle");
                saveSurvey();
            });
        }
        //now add the content
        var tabcontent = document.createElement("div");
        container.appendChild(tabcontent);
        tabcontent.className = "tab-content bg-light";
        this.bubbleUp = false;
        for (var i = 0; i < block["content"].length; i++) {
            var pane = document.createElement("div");
            tabcontent.appendChild(pane);
            if (data["active"][this.blockID] == i) {
                pane.className = "tab-pane active";
            }
            else {
                pane.className = "tab-pane";
            }
            pane.setAttribute("id", this.blockID + ":" + i + "-tab");
            pane.setAttribute("role", "tabpanel");
            pane.setAttribute("aria-labelledby", this.blockID + ":" + i + "-tab");
            if (i == block["content"].length - 1) {
                this.bubbleUp = true;
            }
            this.tabBlockAssignment[blocks.length] = i;
            var newBlock = new blockLookup[block["content"][i]["block"]["type"]](pane, block["content"][i]["block"], this, blocks.length);
            blocks.push(newBlock);
        }

        // Register Signal
        registerSignal(container, block);
    }

    //completion method
    completion(blockID, completed, total) {
        this.completed[blockID] = [completed, total];
        //if not active update the button background
        if (this.tabBlockAssignment[blockID] != data["active"][this.blockID]) {
            var newButton = document.getElementById(this.blockID + ":" + this.tabBlockAssignment[blockID]);
            newButton.classList.remove("bg-success-subtle");
            newButton.classList.remove("bg-primary-subtle");
            if (total > 0 && completed == total) {
                newButton.classList.add("bg-success-subtle");
            }
            if (total > 0 && completed < total) {
                newButton.classList.add("bg-primary-subtle");
            }
        }
        //bubble up completion status to parent
        if (this.bubbleUp) {
            var status = [0, 0];
            for (var key in this.completed) {
                status[0] += this.completed[key][0];
                status[1] += this.completed[key][1];
            }
            this.parent.completion(this.blockID, status[0], status[1]);
        }
    }
}

//add class to lookup dictionary
blockLookup["tabs"] = Tabs;
