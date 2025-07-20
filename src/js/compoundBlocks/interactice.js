class Interactive {

  constructor(root, block, parent, blockID) {
      //generate a unique block ID
      this.blockID=blockID;
      this.parent=parent;
      //keep track of completion
      this.completed={};
      //construct container
      var container=document.createElement("div");
      container.className="container";
      root.appendChild(container);
      var row=document.createElement("div");
      row.className="row align-items-start";
      container.appendChild(row);
      //construct two columns
      this.bubbleUp=false;
      //text column
      var textColumn=document.createElement("div");
      textColumn.className="col large-scrollable-box";
      row.appendChild(textColumn);
      //context column
      var contextColumn=document.createElement("div");
      contextColumn.className="col";
      row.appendChild(contextColumn);
      this.spanAssignments={};
      this.tabAssignments={};
      for(var i=0;i<block["content"].length;i++){
        var para=document.createElement("p");
        textColumn.appendChild(para);
        for(var j=0;j<block["content"][i]["fragments"].length;j++){
          if (data["active"][this.blockID]==undefined){
            data["active"][this.blockID]=blocks.length;
          }        
          if (i==block["content"].length-1 && j==block["content"][i]["fragments"].length-1){
            this.bubbleUp=true;  
          }  
          var fragment=block["content"][i]["fragments"][j];
          var span=document.createElement("div");
          this.spanAssignments[blocks.length]=span;
          span.innerHTML=fragment["text"];
          span.setAttribute("blockid",blocks.length);
          
          // Apply light bottom border to all fragments for visual separation
          span.style.borderBottom = "1px solid #e0e0e0";
          span.style.paddingBottom = "8px";
          span.style.marginBottom = "8px";
          span.style.display = "block";
          span.style.padding = "8px";
          span.style.borderRadius = "4px";
          
          // Set color attribute from fragment data if it exists
          if (fragment["color"]) {
            span.setAttribute("color", fragment["color"]);
            span.setAttribute("original-color", fragment["color"]); // Store original color
            this.applyFragmentColor(span, fragment["color"]);
          }
          
          // Set border attribute from fragment data if it exists
          if (fragment["border"]) {
            span.setAttribute("border", fragment["border"]);
            span.style.border = fragment["border"];
            // Ensure border doesn't override the bottom separator
            span.style.borderBottom = fragment["border"].includes("border-bottom") ? fragment["border"] : span.style.borderBottom;
          }
          para.appendChild(span);
          span.addEventListener("mouseover", (e) => {
            e.target.classList.add("text-danger-emphasis");
          });
          span.addEventListener("mouseout", (e) => {
            e.target.classList.remove("text-danger-emphasis");
          });
          span.addEventListener("click", (e) => {
            //unmark old span
            var priorSpan=this.spanAssignments[data["active"][this.blockID]];
            if (priorSpan!=undefined){
              priorSpan.classList.remove("bg-warning-subtle");
              // Restore original border if it exists
              var originalBorder = priorSpan.getAttribute("border");
              if (originalBorder) {
                priorSpan.style.border = originalBorder;
              } else {
                priorSpan.style.border = ""; // Remove active border
                priorSpan.style.borderBottom = "1px solid #e0e0e0"; // Restore fragment separator
              }
              // Restore the current color
              var currentColor = priorSpan.getAttribute("color");
              if (currentColor) {
                this.applyFragmentColor(priorSpan, currentColor);
              }
              this.tabAssignments[data["active"][this.blockID]].style.display="none";
            }
            //mark new span - but preserve color and border if they exist
            var originalColor = e.target.getAttribute("original-color");
            var currentColor = e.target.getAttribute("color");
            var originalBorder = e.target.getAttribute("border");
            
            // Remove all possible background classes and inline styles
            e.target.classList.remove("bg-success-subtle", "bg-primary-subtle");
            e.target.style.backgroundColor = "";
            
            if (currentColor) {
              // For colored fragments, remove current color class
              e.target.classList.remove(currentColor);
            }
            // Always add warning background for active selection
            e.target.classList.add("bg-warning-subtle");
            
            // Add active selection border (blue border with higher specificity)
            e.target.style.border = "3px solid #0d6efd";
            
            //adjust context
            var blockID=e.target.getAttribute("blockid");
            this.tabAssignments[blockID].style.display="";
            data["active"][this.blockID]=blockID;
            saveSurvey();
          });
          var tabDiv=document.createElement("div");
          this.tabAssignments[blocks.length]=tabDiv;
          if (data["active"][this.blockID]==blocks.length){
            tabDiv.style.display="";
          }
          else{
            tabDiv.style.display="none";
          }
          contextColumn.appendChild(tabDiv);
          var currentBlockId=blocks.length;
          blocks.push(new blockLookup[fragment["block"]["type"]](tabDiv,fragment["block"],this,blocks.length));
          //if not active update the span bg attribute
          if (currentBlockId!=data["active"][this.blockID]){
            // Apply the fragment's color if it has one, otherwise default behavior
            var fragmentColor = this.spanAssignments[currentBlockId].getAttribute("color");
            if (fragmentColor) {
              this.applyFragmentColor(span, fragmentColor);
            }
          }          
          else{
            span.classList.add("bg-warning-subtle");
          }
        }
      }
  }

  // Helper function to apply fragment colors
  applyFragmentColor(span, colorClass) {
    // Clear any existing background styling
    span.classList.remove("bg-success-subtle", "bg-primary-subtle", "bg-warning-subtle");
    span.style.backgroundColor = "";
    
    // Apply the appropriate color
    if (colorClass === "bg-light-purple") {
      span.style.backgroundColor = "#f3e8ff";
    } else {
      span.classList.add(colorClass);
    }
  }

  //completion method
  completion(blockID,completed,total) {
    console.log(blockID+":"+completed+":"+total);
    this.completed[blockID]=[completed,total];
    var span = this.spanAssignments[blockID];
    
    //update the span
    if (completed==total){
      span.setAttribute("color","bg-success-subtle");
      this.applyFragmentColor(span, "bg-success-subtle");
    }
    else if (completed > 0){
      span.setAttribute("color","bg-primary-subtle");
      this.applyFragmentColor(span, "bg-primary-subtle");
    }
    else {
      // No completion - restore original color
      var originalColor = span.getAttribute("original-color");
      if (originalColor) {
        span.setAttribute("color", originalColor);
        this.applyFragmentColor(span, originalColor);
      } else {
        span.classList.remove("bg-success-subtle", "bg-primary-subtle", "bg-warning-subtle");
        span.style.backgroundColor = "";
      }
    }
    
    //bubble up completion status to parent
    if (this.bubbleUp){
        var status=[0,0];
        for(var key in this.completed){
            status[0]+=this.completed[key][0];
            status[1]+=this.completed[key][1];
        }
        this.parent.completion(this.blockID,status[0],status[1]);
    }
  }
}

  
//add class to lookup dictionary
blockLookup["interactive"]=Interactive;