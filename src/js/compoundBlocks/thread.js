class Thread {

    constructor(root, block, parent, blockID) {
        //generate a unique block ID
        this.blockID = blockID;
        this.parent = parent;
        //keep track of completion
        this.completed = {};

        // Render Text Content (Title + Body)
        var textDiv = document.createElement("div");
        textDiv.className = "thread-content";
        root.appendChild(textDiv);

        // Title
        if (block["content"] && block["content"]["title"] != undefined) {
            var h = document.createElement("h" + block["content"]["title"]["size"]);
            textDiv.appendChild(h);
            h.innerHTML = block["content"]["title"]["text"];
        }

        // Body
        if (block["content"] && block["content"]["body"] != undefined) {
            for (var i = 0; i < block["content"]["body"]["text"].length; i++) {
                var p = document.createElement("p");
                textDiv.appendChild(p);
                p.innerHTML = block["content"]["body"]["text"][i];
            }
        }

        // Render Child Threads Container
        var container = document.createElement("div");
        container.className = "thread-container";
        root.appendChild(container);

        this.bubbleUp = false;
        // Loop over child threads
        if (block["threads"]) {
            for (var i = 0; i < block["threads"].length; i++) {
                // Check if this is the last block to handle bubbleUp logic
                if (i == block["threads"].length - 1) {
                    this.bubbleUp = true;
                }
                // Instantiate the child block
                blocks.push(new blockLookup[block["threads"][i]["type"]](container, block["threads"][i], this, blocks.length));
            }
        }
    }

    //completion method
    completion(blockID, completed, total) {
        this.completed[blockID] = [completed, total];
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
blockLookup["thread"] = Thread;
