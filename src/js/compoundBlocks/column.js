class Column {

  constructor(root, block, parent, blockID) {
      //generate a unique block ID
      this.blockID=blockID;
      this.parent=parent;
      //keep track of completion
      this.completed={};
      //construct columns
      var container=document.createElement("div");
      container.className="container";
      root.appendChild(container);
      var row=document.createElement("div");
      row.className="row align-items-start";
      container.appendChild(row);
      this.bubbleUp=false;
      for(var i=0;i<block["content"].length;i++){
        //create column
        var column=document.createElement("div");
        column.className="col";
        if (block["styleData"]["verticalHeight"]) {
            column.style.overflowY = "auto";
            column.style.height = block["styleData"]["verticalHeight"] + "vh";
        }
        row.appendChild(column);
        for(var j=0;j<block["content"][i].length;j++){
          if (i==block["content"].length-1 && j==block["content"][i].length-1){
            this.bubbleUp=true;  
          }
          blocks.push(new blockLookup[block["content"][i][j]["type"]](column,block["content"][i][j],this,blocks.length));
        }
      }
  }

  //completion method
  completion(blockID,completed,total) {
      this.completed[blockID]=[completed,total];
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
blockLookup["column"]=Column;