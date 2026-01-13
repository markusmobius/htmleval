class Interactive {

  constructor(root, block, parent, blockID) {
    //generate a unique block ID
    this.blockID = blockID;
    this.parent = parent;
    //keep track of completion
    this.completed = {};
    //construct container
    var container = document.createElement("div");
    container.className = "container";
    root.appendChild(container);
    var row = document.createElement("div");
    row.className = "row align-items-start";
    container.appendChild(row);
    //construct two columns
    this.bubbleUp = false;
    //text column
    var textColumn = document.createElement("div");
    textColumn.className = "col large-scrollable-box";
    row.appendChild(textColumn);
    //context column
    var contextColumn = document.createElement("div");
    contextColumn.className = "col";
    row.appendChild(contextColumn);
    this.spanAssignments = {};
    this.tabAssignments = {};
    for (var i = 0; i < block["content"].length; i++) {
      var para = document.createElement("p");
      textColumn.appendChild(para);
      for (var j = 0; j < block["content"][i]["fragments"].length; j++) {
        if (data["active"][this.blockID] == undefined) {
          data["active"][this.blockID] = blocks.length;
        }
        if (i == block["content"].length - 1 && j == block["content"][i]["fragments"].length - 1) {
          this.bubbleUp = true;
        }
        var fragment = block["content"][i]["fragments"][j];
        var span = document.createElement("div");
        this.spanAssignments[blocks.length] = span;
        span.innerHTML = fragment["text"];
        span.setAttribute("blockid", blocks.length);

        // Apply light bottom border to all fragments for visual separation
        span.style.borderBottom = "1px solid #e0e0e0";
        span.style.paddingBottom = "8px";
        span.style.marginBottom = "8px";
        span.style.display = "block";
        span.style.padding = "8px";
        span.style.borderRadius = "4px";

        // Set border attribute from fragment data if it exists
        if (fragment["border"]) {
          span.setAttribute("border", fragment["border"]);
          span.setAttribute("original-border", fragment["border"]); // Store original border
          span.style.border = fragment["border"];
          // Override the bottom separator with the main border
          span.style.borderBottom = fragment["border"];
        }

        para.appendChild(span);
        span.addEventListener("mouseover", (e) => {
          e.currentTarget.classList.add("text-danger-emphasis");
        });
        span.addEventListener("mouseout", (e) => {
          e.currentTarget.classList.remove("text-danger-emphasis");
        });
        span.addEventListener("click", (e) => {
          // Determine new and previous block IDs as numbers
          var newBlockID = parseInt(e.currentTarget.getAttribute("blockid"), 10);
          var priorBlockID = data["active"][this.blockID] !== undefined ? parseInt(data["active"][this.blockID], 10) : undefined;

          // If clicking the same active block, ensure tab is visible and keep highlight
          if (priorBlockID === newBlockID) {
            if (this.tabAssignments[newBlockID]) this.tabAssignments[newBlockID].style.display = "";
            e.currentTarget.classList.add("bg-warning-subtle");
            saveSurvey();
            return;
          }

          // Unmark old span if it exists
          var priorSpan = this.spanAssignments[priorBlockID];
          if (priorSpan != undefined) {
            priorSpan.classList.remove("bg-warning-subtle");
            // Restore original border if it exists
            var originalBorder = priorSpan.getAttribute("original-border");
            if (originalBorder) {
              priorSpan.style.border = originalBorder;
            } else {
              priorSpan.style.border = ""; // Remove any border
              priorSpan.style.borderBottom = "1px solid #e0e0e0"; // Restore fragment separator
            }
            if (this.tabAssignments[priorBlockID]) this.tabAssignments[priorBlockID].style.display = "none";
          }

          //adjust context - set new active and show its tab
          if (this.tabAssignments[newBlockID]) this.tabAssignments[newBlockID].style.display = "";
          data["active"][this.blockID] = newBlockID;

          //mark new span - add yellow background but preserve border
          e.currentTarget.classList.add("bg-warning-subtle");

          // Update the previous span to show its completion status now that it's not active
          if (priorSpan != undefined && this.completed[priorBlockID]) {
            this.completion(priorBlockID, this.completed[priorBlockID][0], this.completed[priorBlockID][1]);
          }

          saveSurvey();
        });
        var tabDiv = document.createElement("div");
        this.tabAssignments[blocks.length] = tabDiv;
        if (data["active"][this.blockID] == blocks.length) {
          tabDiv.style.display = "";
        }
        else {
          tabDiv.style.display = "none";
        }
        contextColumn.appendChild(tabDiv);
        var currentBlockId = blocks.length;
        blocks.push(new blockLookup[fragment["block"]["type"]](tabDiv, fragment["block"], this, blocks.length));
        //if not active, apply normal styling
        if (currentBlockId != data["active"][this.blockID]) {
          // Fragment gets its default styling from border attribute
        }
        else {
          span.classList.add("bg-warning-subtle");
        }
      }
    }

    // Register Signal
    registerSignal(container, block);
  }

  //completion method
  completion(blockID, completed, total) {
    console.log(blockID + ":" + completed + ":" + total);
    this.completed[blockID] = [completed, total];
    var span = this.spanAssignments[blockID];

    //update the span - just change background, preserve border
    // Check if any answers for this specific block are "no"
    // TODO make this more generic - this only works for yes/no questions
    if (completed == total) {
      var hasNoAnswers = false;
      // Get the specific block and check its data variables directly
      if (blocks[blockID]) {
        // Look for the table element in the tab that corresponds to this blockID
        var tabDiv = this.tabAssignments[blockID];
        if (tabDiv) {
          // Find all checked inputs in this specific tab div (for MultiRowChecked)
          var checkedInputs = tabDiv.querySelectorAll('input[type="checkbox"]:checked');
          for (var i = 0; i < checkedInputs.length; i++) {
            var input = checkedInputs[i];
            var fullId = input.getAttribute("fullid") || input.getAttribute("name");
            var value = fullId ? data["variables"][fullId] : null;
            var varValue = input.getAttribute("varvalue");
            console.log("[completion] checkbox", i, "fullId:", fullId, "stored value:", value, "varvalue:", varValue);
            if (value === "no" || varValue === "no" || input.value === "no") {
              hasNoAnswers = true;
              break;
            }
          }

          // Support MultiRowSelect: radio inputs or select elements
          if (!hasNoAnswers) {
            // Radios
            var radioInputs = tabDiv.querySelectorAll('input[type="radio"]:checked');
            console.log('[completion] found radios:', radioInputs.length);
            for (var r = 0; r < radioInputs.length; r++) {
              var rInput = radioInputs[r];
              var rFullId = rInput.getAttribute("fullid") || rInput.getAttribute("name");
              var rValue = rFullId ? data["variables"][rFullId] : null;
              var rVarValue = rInput.getAttribute("varvalue");
              console.log("[completion] radio", r, "fullId:", rFullId, "stored value:", rValue, "varvalue:", rVarValue, "input.value:", rInput.value);
              if (rValue === "no" || rVarValue === "no" || rInput.value === "no") {
                hasNoAnswers = true;
                break;
              }
            }
          }

          if (!hasNoAnswers) {
            // Select elements (dropdowns)
            var selects = tabDiv.querySelectorAll('select');
            console.log('[completion] found selects:', selects.length);
            for (var s = 0; s < selects.length; s++) {
              var sel = selects[s];
              var selFullId = sel.getAttribute('fullid') || sel.getAttribute('name');
              var selValue = selFullId ? data['variables'][selFullId] : null;
              var selSelected = sel.options[sel.selectedIndex] ? sel.options[sel.selectedIndex].value : null;
              console.log('[completion] select', s, 'fullId:', selFullId, 'stored value:', selValue, 'selected:', selSelected);
              if (selValue === 'no' || selSelected === 'no') {
                hasNoAnswers = true;
                break;
              }
            }
          }
        } else {
          console.log("Could not find tabDiv for blockID:", blockID);
        }
      } else {
        console.log("Could not find block for blockID:", blockID);
      }

      span.classList.remove("bg-primary-subtle", "bg-warning-subtle", "bg-danger-subtle", "bg-success-subtle");

      // Check if this block is currently active/selected - if so, don't change it
      var isActive = data["active"][this.blockID] == blockID;

      if (!isActive) {
        // Only apply completion colors if the block is NOT currently active
        if (hasNoAnswers) {
          span.classList.add("bg-danger-subtle");
        } else {
          span.classList.add("bg-success-subtle");
        }
      } else {
        // If active, keep the yellow highlight
        span.classList.add("bg-warning-subtle");
      }
    }
    else if (completed > 0) {
      // Check if this block is currently active/selected
      var isActive = data["active"][this.blockID] == blockID;

      span.classList.remove("bg-success-subtle", "bg-warning-subtle", "bg-danger-subtle");

      if (isActive) {
        // If active, show yellow highlight
        span.classList.add("bg-warning-subtle");
      } else {
        // If not active, show partial completion (blue)
        span.classList.add("bg-primary-subtle");
      }
    }
    else {
      // No completion - remove completion styling
      span.classList.remove("bg-success-subtle", "bg-primary-subtle", "bg-danger-subtle");
      // Keep warning if currently active
      if (data["active"][this.blockID] == blockID) {
        span.classList.add("bg-warning-subtle");
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
blockLookup["interactive"] = Interactive;