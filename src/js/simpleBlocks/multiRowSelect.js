class MultiRowSelect {

    constructor(root, block, parent, blockID) {
        this.blockID=blockID;
        this.parent=parent;
        //keep track of completion
        this.completed=[0,0];
        //construct table
        var tbl = document.createElement("table");
        tbl.className = "table table-striped table-hover";
        tbl.setAttribute("border", 1);
        root.appendChild(tbl);
        //add header
        var thead = document.createElement("thead");
        var header_row = document.createElement("tr");
        thead.appendChild(header_row);
        tbl.appendChild(thead);
        var th = document.createElement("th");
        th.innerHTML = block["content"]["rowLabel"];
        th.style.width="80%";
        header_row.appendChild(th);
        th = document.createElement("th");
        th.innerHTML = block["content"]["questionLabel"];
        header_row.appendChild(th);
        //now add the rows    
        var tbody = document.createElement("tbody");
        tbl.appendChild(tbody);
        for (var i = 0; i < block["content"]["rows"].length; i++) {
            var row = document.createElement("tr");
            tbody.appendChild(row);
            var td = document.createElement("td");
            row.appendChild(td);
            td.innerHTML=block["content"]["rows"][i]["text"];
            //now create the select element
            var td = document.createElement("td");
            row.appendChild(td);
            var select = document.createElement("select");
            td.appendChild(select);
            select.className = "form-control";
            var fullId=["",""];
            for(var key in block["content"]["rows"][i]["id"]){
                fullId[key]=block["content"]["rows"][i]["id"][key];
            }
            for(var key in block["content"]["id"]){
                fullId[key]=block["content"]["id"][key];
            }
            fullId=JSON.stringify(fullId);
            select.setAttribute("id",fullId);
            var option = document.createElement("option");
            option.innerHTML = "Select";
            select.appendChild(option);
            var oldValue=data["variables"][fullId];
            for(var k=0;k<block["content"]["options"].length;k++){
                var option = document.createElement("option");
                option.innerHTML = block["content"]["options"][k]["label"];
                if (block["content"]["options"][k]["color"]!=undefined){
                    option.setAttribute("color",block["content"]["options"][k]["color"]);
                }
                option.value=block["content"]["options"][k]["value"];
                select.appendChild(option);                    
                if (oldValue==option.value){
                    select.selectedIndex=k+1;
                    this.completed[0]++;
                    if (block["content"]["options"][k]["color"]!=undefined){
                        row.className="table-"+block["content"]["options"][k]["color"];
                    }    
                }
            }
            this.completed[1]++;
            select.addEventListener('change', (e) => {
                if (e.target.selectedIndex==0){
                    delete data["variables"][e.target.id];
                    this.completed[0]--;
                }
                else{
                    if (data["variables"][e.target.id]==undefined){
                        this.completed[0]++;
                    }
                    data["variables"][e.target.id]=e.target.value;
                }
                var selectedOption = e.target.options[e.target.selectedIndex];
                var color = selectedOption.getAttribute('color');
                var row=e.target.parentElement.parentElement;
                if (color!=undefined){                    
                    row.className="table-"+color;
                }
                else{
                    row.className="";
                }
                this.completion();
                saveSurvey();
            });
        }
        this.completion();
    }
  
    //completion method
    completion() {
        this.parent.completion(this.blockID,this.completed[0],this.completed[1]);
    }
  }
  
    
//add class to lookup dictionary
blockLookup["multi_row_select"]=MultiRowSelect;