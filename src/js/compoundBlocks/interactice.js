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
            priorSpan.classList.remove("bg-warning-subtle");
            priorSpan.classList.add(priorSpan.getAttribute("color"));
            this.tabAssignments[data["active"][this.blockID]].style.display="none";
            //mark new span
            e.target.classList.remove("bg-success-subtle");
            e.target.classList.remove("bg-primary-subtle");
            e.target.classList.add("bg-warning-subtle");
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
            span.classList.add(this.spanAssignments[currentBlockId].getAttribute("color"));            
          }          
          else{
            span.classList.add("bg-warning-subtle");
          }
        }
      }
  }

  //completion method
  completion(blockID,completed,total) {
    console.log(blockID+":"+completed+":"+total);
    this.completed[blockID]=[completed,total];
    //update the span
    if (completed==total){
      this.spanAssignments[blockID].setAttribute("color","bg-success-subtle");
    }
    else{
      this.spanAssignments[blockID].setAttribute("color","bg-primary-subtle");
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