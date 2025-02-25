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


var loadSurvey = async function() {
    try {
        var response = await fetch("https://www.kv.econlabs.org/" + reviewerID);
    } catch (e) {
        console.log("network is down");
        document.getElementById("completedstatus").innerHTML = "SERVER UNAVAILABLE";
        return;
    }
    if (!response.ok) {
        console.log("no stored data");
        fullData = initializeFullData(overall_data);
        build(overall_data);
    } else {
        var text = await response.text();
        fullData = JSON.parse(text);
        console.log("stored data retrieved: ", fullData);
        build(overall_data);
    }
};


(async() => {
    await loadSurvey(); 
})();

document.addEventListener("DOMContentLoaded", function() {
    loadSurvey().then(() => {
        // Automatically open the first tab and the first inner tab
        const firstTabButton = document.querySelector('.nav-tabs .nav-link');
        if (firstTabButton) {
            firstTabButton.click();
            const firstInnerTabButton = document.querySelector(`#${firstTabButton.getAttribute('aria-controls')} .nav-tabs .nav-link`);
            if (firstInnerTabButton) {
                firstInnerTabButton.click();
            }
        }
    });
});
