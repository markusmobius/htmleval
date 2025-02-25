var saveSurvey = function() {
            //we assume that the data is stored in tabData
            fetch("https://www.kv.econlabs.org//" + reviewerID, {
                method: 'PUT',
                headers: {
                    'Content-type': 'text'
                },
                body: JSON.stringify(data)
            }).then((data) => {
                console.log("data saved");
            }).catch((error) => {
                console.log(error)
            });
};

var completion = function(blockID,completed,total){
    if (total==0){
        document.getElementById("completedstatus").innerHTML="100% completed";
    }
    else{
        document.getElementById("completedstatus").innerHTML=Math.floor(100*completed/total)+ "% completed";
    }
}

//populate survey when loading
var blocks=[];
var loadSurvey = async function(){
    try{
        var response = await fetch("https://www.kv.econlabs.org/" + reviewerID);
    }
    catch(e){
        console.log("network is down");
        document.getElementById("completedstatus").innerHTML="SERVER UNAVAILABLE";
        return;
    }
    if (!response.ok){
        console.log("no stored data");
        data={
            "active": {},
            "variables":{}
        };
    }
    else{
        var text= await response.text();
        data=JSON.parse(text);
        console.log("stored data retrieved");
    }
    //now build the survey
    var root=document.getElementById("rootblock");
    blocks.push(new blockLookup[rootBlock["type"]](root,rootBlock,this,blocks.length));
};


(async() => {
    await loadSurvey(); 
 })();
