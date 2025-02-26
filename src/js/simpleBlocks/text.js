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
            for(var i=0;i<block["content"]["body"]["text"].length;i++){
                var p=document.createElement("p");
                div.appendChild(p);
                p.innerHTML=block["content"]["body"]["text"][i];    
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