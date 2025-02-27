class SimpleText {

    constructor(root, block, parent, blockID) {
        this.blockID=blockID;
        this.parent=parent;
        //keep track of completion
        this.completed=[0,0];
        var div=document.createElement("div");
        root.appendChild(div);
        if (block["content"]["scrollable"]===true){
            div.className="scrollable-box";
        }
        //write title (if exists)
        if (block["content"]["title"]!=undefined){
            var h=document.createElement("h"+block["content"]["title"]["size"]);
            div.appendChild(h);
            h.innerHTML=block["content"]["title"]["text"];
        }
        //write body (if exists)
        if (block["content"]["body"]!=undefined){
            if (block["content"]["body"]["is_table"]==true){
                var tbl = document.createElement("table");
                tbl.className = "table table-striped table-hover";
                root.appendChild(tbl);
                var tbody = document.createElement("tbody");
                tbl.appendChild(tbody);
                for(var i=0;i<block["content"]["body"]["text"].length;i++){
                    var row = document.createElement("tr");
                    tbody.appendChild(row);
                    var td = document.createElement("td");
                    row.appendChild(td);
                    td.innerHTML=block["content"]["body"]["text"][i];
                }
            }
            else{
                for(var i=0;i<block["content"]["body"]["text"].length;i++){
                    var p=document.createElement("p");
                    div.appendChild(p);
                    p.innerHTML=block["content"]["body"]["text"][i];    
                }    
            }
        }
        this.completion();
    }
  
    //completion method
    completion() {
        this.parent.completion(this.blockID,this.completed[0],this.completed[1]);
    }
  }
  
    
//add class to lookup dictionary
blockLookup["text"]=SimpleText;