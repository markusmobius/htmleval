//surveyID
var reviewerID = "REVIEWERID";
var saveSurvey = function() {
            //we assume that the data is stored in tabData
            fetch("https://www.kv.econlabs.org//" + reviewerID, {
                method: 'PUT',
                headers: {
                    'Content-type': 'text'
                },
                body: JSON.stringify(fullData)
            }).then((data) => {
                console.log("data saved");
            }).catch((error) => {
                console.log(error)
            });
};


//populate survey when loading
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
        build({
            "active": 0,
            "data":[]
        });    
    }
    else{
        var text= await response.text();
        var fullData=JSON.parse(text);
        console.log("stored data retrieved");
        build(fullData);
    }
};

(async() => {
    await loadSurvey(); 
})();


