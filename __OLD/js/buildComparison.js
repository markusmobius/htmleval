//tabData holds all the data across tabs
//each element in the array has a uuid and a data section
//data section consists of an array of objects with compoundID and variables with values
//example: single tab, containing one object 
//[{"active": 0,"data":[{"compoundID":{something},"values":{"varname1":"value1","varname2":"value2"}]}]

// var fullData = {
//     "active": 0,
//     "reviewer_1":  [{"compoundID": {"publisher": "theguardian.com", "url": "https://www.theguardian.com/us-news/2020/jul/16/pompeo-claims-private-property-and-religious-freedom-are-foremost-human-rights", "fragment": 0}, "values": {"varname1": 'yes', "varname2": 'no'}},
//                             {"compoundID": {"publisher": "theguardian.com", "url": "https://www.theguardian.com/us-news/2020/jul/16/pompeo-claims-private-property-and-religious-freedom-are-foremost-human-rights", "fragment": 1}, "values": {"varname1": 'no', "varname2": 'yes'}},
//                             {"compoundID": {"publisher": "thegraun.com", "url": "https://www.theguardian.com/us-news/2020/jul/16/pompeo-claims-private-property-and-religious-freedom-are-foremost-human-rights", "fragment": 0}, "values": {"varname1": 'no', "varname2": 'no'}}
//                         ],
//     "reviewer_2":  [{"compoundID": {"publisher": "theguardian.com", "url": "https://www.theguardian.com/us-news/2020/jul/16/pompeo-claims-private-property-and-religious-freedom-are-foremost-human-rights", "fragment": 0}, "values": {"varname1": 'yes', "varname2":"no"}},
//                             {"compoundID": {"publisher": "theguardian.com", "url": "https://www.theguardian.com/us-news/2020/jul/16/pompeo-claims-private-property-and-religious-freedom-are-foremost-human-rights", "fragment": 1}, "values": {"varname1": 'yes', "varname2": 'yes'}},
//                             {"compoundID": {"publisher": "thegraun.com", "url": "https://www.theguardian.com/us-news/2020/jul/16/pompeo-claims-private-property-and-religious-freedom-are-foremost-human-rights", "fragment": 0}, "values": {"varname1": 'yes', "varname2": 'no'}}
//     ],
//     "reviewer_3":  [{"compoundID": {"publisher": "theguardian.com", "url": "https://www.theguardian.com/us-news/2020/jul/16/pompeo-claims-private-property-and-religious-freedom-are-foremost-human-rights", "fragment": 0}, "values": {"varname1": "yes", "varname2": "no"}},
//                             {"compoundID": {"publisher": "theguardian.com", "url": "https://www.theguardian.com/us-news/2020/jul/16/pompeo-claims-private-property-and-religious-freedom-are-foremost-human-rights", "fragment": 1}, "values": {"varname1": "yes", "varname2": "no"}},
//                             {"compoundID": {"publisher": "thegraun.com", "url": "https://www.theguardian.com/us-news/2020/jul/16/pompeo-claims-private-property-and-religious-freedom-are-foremost-human-rights", "fragment": 0}, "values": {"varname1": "yes", "varname2": "no"}}
//     ]
// };

// var matrix = {
//     "questions": [
//         {"question": "Question 1", "varname": "varname1"},
//         {"question": "Question 2", "varname": "varname2"}
//     ],
//     "tabs": [
//         {
//             "header": "Header 1",
//             "text": "Text 1",
//             "rows": [
//                 {"compoundID": {"publisher": "theguardian.com", "url": "https://www.theguardian.com/us-news/2020/jul/16/pompeo-claims-private-property-and-religious-freedom-are-foremost-human-rights", "fragment": 0}, "text": "Fragment 1", "css": "success"},
//                 {"compoundID": {"publisher": "theguardian.com", "url": "https://www.theguardian.com/us-news/2020/jul/16/pompeo-claims-private-property-and-religious-freedom-are-foremost-human-rights", "fragment": 1}, "text": "Fragment 2", "css": "danger"}
//             ]
//         },
//         {
//             "header": "Header 2",
//             "text": "Text 2",
//             "rows": [
//                 {"compoundID": {"publisher": "thegraun.com", "url": "https://www.theguardian.com/us-news/2020/jul/16/pompeo-claims-private-property-and-religious-freedom-are-foremost-human-rights", "fragment": 0}, "text": "Fragment 1", "css": "success"}
//             ]
//         }
//     ]
// };

// var instructions = [
//     "Instructions 1",
//     "Instructions 2"
// ];

var fullData = FULLDATA;
var matrix = MULTIROWDATA;
var instructions = INSTRUCTIONS;

// Function to extract unique labels from the data
var extractUniqueLabels = function() {
    var labels = new Set();
    for (var reviewer in fullData) {
        if (reviewer !== "active") {
            fullData[reviewer].forEach(row => {
                for (var varname in row["values"]) {
                    labels.add(row["values"][varname]);
                }
            });
        }
    }
    return Array.from(labels);
};

// Function to calculate confusion matrix
var calculateConfusionMatrix = function(reviewer1, reviewer2, labels, question) {
    var matrix = {};
    labels.forEach(label1 => {
        matrix[label1] = {};
        labels.forEach(label2 => {
            matrix[label1][label2] = 0;
        });
    });

    var data1 = fullData[reviewer1];
    var data2 = fullData[reviewer2];

    for (var i = 0; i < data1.length; i++) {
        var row1 = data1[i];
        var row2 = data2.find(row => JSON.stringify(row["compoundID"]) === JSON.stringify(row1["compoundID"]));

        if (row2) {
            if (question === "all") {
                for (var varname in row1["values"]) {
                    var value1 = row1["values"][varname];
                    var value2 = row2["values"][varname];
                    matrix[value1][value2]++; // Correctly assign labels
                }
            }
        }
    }
    return matrix;
};

// Function to calculate statistics from the confusion matrix
var calculateStatistics = function(matrix, labels) {
    var stats = {
        "accuracy": 0,
        "precision": 0,
        "recall": 0,
        "fscore": 0
    };

    var total = 0;
    var correct = 0;
    var precisionSum = 0;
    var recallSum = 0;

    labels.forEach(label => {
        var tp = matrix[label][label];
        var fp = 0;
        var fn = 0;
        var tn = 0;

        labels.forEach(otherLabel => {
            if (otherLabel !== label) {
                fp += matrix[otherLabel][label];
                fn += matrix[label][otherLabel];
                tn += matrix[otherLabel][otherLabel];
            }
        });

        var precision = tp / (tp + fp);
        var recall = tp / (tp + fn);
        var fscore = 2 * (precision * recall) / (precision + recall);

        precisionSum += precision;
        recallSum += recall;

        correct += tp + tn;
        total += tp + fp + fn + tn; // Add true positives, false positives, false negatives, and true negatives for the current label

        stats["fscore"] += fscore;
    });

    stats["accuracy"] = correct / total;
    stats["precision"] = precisionSum / labels.length;
    stats["recall"] = recallSum / labels.length;
    stats["fscore"] /= labels.length;

    return stats;
};

// Function to display confusion matrices and statistics
var displayConfusionMatrices = function(pane, question) {
    var checkedReviewers = [];
    for (var reviewer in fullData) {
        if (reviewer !== "active" && document.getElementById(reviewer).checked) {
            checkedReviewers.push(reviewer);
        }
    }

    var labels = extractUniqueLabels();

    for (var i = 0; i < checkedReviewers.length; i++) {
        for (var j = i + 1; j < checkedReviewers.length; j++) {
            var reviewer1 = checkedReviewers[i];
            var reviewer2 = checkedReviewers[j];
            var matrix = calculateConfusionMatrix(reviewer1, reviewer2, labels, question);
            var stats = calculateStatistics(matrix, labels);

            var div = document.createElement("div");
            div.className = "confusion-matrix";
            div.innerHTML = `<h4>${reviewer1} vs ${reviewer2}</h4>`;
            
            var table = document.createElement("table");
            table.className = "table table-bordered";
            var thead = document.createElement("thead");
            var tr = document.createElement("tr");
            tr.appendChild(document.createElement("th")); // Empty corner cell
            labels.forEach(label => {
                var th = document.createElement("th");
                th.innerHTML = label;
                tr.appendChild(th);
            });
            thead.appendChild(tr);
            table.appendChild(thead);

            var tbody = document.createElement("tbody");
            labels.forEach(label1 => {
                var tr = document.createElement("tr");
                var th = document.createElement("th");
                th.innerHTML = label1;
                tr.appendChild(th);
                labels.forEach(label2 => {
                    var td = document.createElement("td");
                    td.innerHTML = matrix[label1][label2];
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });
            table.appendChild(tbody);

            div.appendChild(table);

            // Add statistics
            var statsDiv = document.createElement("div");
            statsDiv.className = "statistics";
            statsDiv.innerHTML = `<p>Accuracy: ${stats["accuracy"].toFixed(2)}</p>
                                  <p>Precision: ${stats["precision"].toFixed(2)}</p>
                                  <p>Recall: ${stats["recall"].toFixed(2)}</p>
                                  <p>F-Score: ${stats["fscore"].toFixed(2)}</p>`;
            div.appendChild(statsDiv);

            pane.appendChild(div);
        }
    }
};

var calculateDisagreements = function(tabIndex) {
    var disagreements = 0;

    matrix["tabs"][tabIndex]["rows"].forEach(row => {
        matrix["questions"].forEach(question => {
            var answers = new Set();

            for (var reviewer in fullData) {
                if (reviewer !== "active") {
                    fullData[reviewer].forEach(reviewerRow => {
                        if (JSON.stringify(reviewerRow["compoundID"]) === JSON.stringify(row["compoundID"])) {
                            answers.add(reviewerRow["values"][question["varname"]]);
                        }
                    });
                }
            }

            // Check for disagreements
            if (answers.size > 1) {
                disagreements++;
            }
        });
    });

    return disagreements;
};

// Add checkboxes for each reviewer
var addReviewerCheckboxes = function() {
    var root = document.getElementById("reviewer-checkboxes");
    var checkboxStates = {};

    // Save the state of existing checkboxes
    for (var reviewer in fullData) {
        if (reviewer !== "active") {
            var checkbox = document.getElementById(reviewer);
            if (checkbox) {
                checkboxStates[reviewer] = checkbox.checked;
            }
        }
    }

    root.innerHTML = ""; // Clear previous checkboxes

    // Recreate checkboxes and restore their state
    for (var reviewer in fullData) {
        if (reviewer !== "active") {
            var label = document.createElement("label");
            var checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.id = reviewer;
            checkbox.checked = checkboxStates[reviewer] !== undefined ? checkboxStates[reviewer] : true; // Restore state or default to checked
            checkbox.addEventListener("change", () => {
                build(fullData); // Rebuild the tabs and tables when a checkbox is changed
            });
            label.appendChild(checkbox);
            label.appendChild(document.createTextNode(reviewer));
            root.appendChild(label);
        }
    }
};

// Modify the buildTab function to include answers from selected reviewers in the same cell
var buildTab = function(pane, i, tabData, is_active) {
    var tbl = document.createElement("table");
    pane.appendChild(tbl);
    tbl.className = "table table-striped table-hover";
    tbl.setAttribute("border", 1);

    var thead = document.createElement("thead");
    tbl.appendChild(thead);
    var tr = document.createElement("tr");
    thead.appendChild(tr);
    tr.style.textAlign = "left";

    var th = document.createElement("th");
    th.style.width = (100 - matrix['questions'].length * 20) + "%";
    tr.appendChild(th);
    th.innerHTML = "Fragment";

    // Add the questions titles as headers
    for (var j = 0; j < matrix["questions"].length; j++) {
        th = document.createElement("th");
        tr.appendChild(th);
        th.innerHTML = matrix["questions"][j]["question"];
    }

    var tbody = document.createElement("tbody");
    tbl.appendChild(tbody);

    // Create Body of Table
    for (var q = 0; q < matrix["tabs"][i]["rows"].length; q++) {
        var tr = document.createElement("tr");
        tbody.appendChild(tr);

        // Add the fragment
        var compoundID = matrix["tabs"][i]["rows"][q]["compoundID"];
        var compoundID_str = JSON.stringify(compoundID);
        var td = document.createElement("td");
        tr.appendChild(td);
        td.innerHTML = matrix["tabs"][i]["rows"][q]["text"];
        td.className = "table-" + matrix["tabs"][i]["rows"][q]["css"];

        // Initialize cells for each question
        var cells = {};
        for (var j = 0; j < matrix["questions"].length; j++) {
            cells[matrix["questions"][j]["varname"]] = document.createElement("td");
            tr.appendChild(cells[matrix["questions"][j]["varname"]]);
        }

        // Find answers from selected reviewers and fill the table
        for (var reviewer in fullData) {
            if (reviewer !== "active" && document.getElementById(reviewer).checked) {
                var rowData = fullData[reviewer].find(row => JSON.stringify(row["compoundID"]) === compoundID_str);
                if (rowData) {
                    for (var j = 0; j < matrix["questions"].length; j++) {
                        var varname = matrix["questions"][j]["varname"];
                        cells[varname].innerHTML += rowData["values"][varname] + "<br>";
                    }
                }
            }
        }

        // Check for disagreements and highlight cells
        for (var j = 0; j < matrix["questions"].length; j++) {
            var varname = matrix["questions"][j]["varname"];
            var answers = cells[varname].innerHTML.trim().split("<br>").map(answer => answer.trim()).filter(answer => answer !== "");
            var allAgree = answers.every(answer => answer === answers[0]);
            if (!allAgree) {
                cells[varname].classList.add("table-danger");
            }
        }
    }
};

// Modify the build function to include checkboxes and the new "Statistics" tab
var build = function(fullData) {
    var root = document.getElementById("tabs");
    root.innerHTML = ""; // Clear previous content

    // Add reviewer checkboxes
    addReviewerCheckboxes();

    // Add tabs
    var ul = document.createElement("ul");
    root.appendChild(ul);
    ul.className = "nav nav-tabs";
    ul.setAttribute("role", "tablist");

    // Add instructions tab
    var li = document.createElement("li");
    ul.appendChild(li);
    li.className = "nav-item";
    li.setAttribute("role", "presentation");
    var button = document.createElement("button");
    li.appendChild(button);
    button.setAttribute("data-bs-toggle", "tab");
    button.setAttribute("id", "tab0-tab");
    button.setAttribute("tabid", 0);
    button.setAttribute("data-bs-target", "#tab0");
    button.setAttribute("type", "button");
    button.setAttribute("role", "tab");
    button.setAttribute("aria-controls", "instructions");
    button.setAttribute("aria-selected", fullData["active"] === 0);
    button.className = fullData["active"] === 0 ? "nav-link active" : "nav-link";
    button.innerHTML = "Instructions";
    button.addEventListener("click", (e) => {
        fullData["active"] = 0;
    });

    // Add the content for the instructions tab
    var tabcontent = document.createElement("div");
    root.appendChild(tabcontent);
    tabcontent.className = "tab-content bg-light";
    var pane = document.createElement("div");
    tabcontent.appendChild(pane);
    pane.className = fullData["active"] === 0 ? "tab-pane active" : "tab-pane";
    pane.setAttribute("id", "tab0");
    pane.setAttribute("role", "tabpanel");
    pane.setAttribute("aria-labelledby", "tab0-tab");

    var instructionsContent = document.createElement("div");
    instructionsContent.className = "instructions-content";
    pane.appendChild(instructionsContent);
    for (var j = 0; j < instructions.length; j++) {
        var p = document.createElement("p");
        p.innerHTML = instructions[j];
        instructionsContent.appendChild(p);
    }

    // Add statistics tab
    var li = document.createElement("li");
    ul.appendChild(li);
    li.className = "nav-item";
    li.setAttribute("role", "presentation");
    var button = document.createElement("button");
    li.appendChild(button);
    button.setAttribute("data-bs-toggle", "tab");
    button.setAttribute("id", "tab1-tab");
    button.setAttribute("tabid", 1);
    button.setAttribute("data-bs-target", "#tab1");
    button.setAttribute("type", "button");
    button.setAttribute("role", "tab");
    button.setAttribute("aria-controls", "statistics");
    button.setAttribute("aria-selected", fullData["active"] === 1);
    button.className = fullData["active"] === 1 ? "nav-link active" : "nav-link";
    button.innerHTML = "Statistics";
    button.addEventListener("click", (e) => {
        fullData["active"] = 1;
    });

    // Add the content for the statistics tab
    var statsPane = document.createElement("div");
    tabcontent.appendChild(statsPane);
    statsPane.className = fullData["active"] === 1 ? "tab-pane active" : "tab-pane";
    statsPane.setAttribute("id", "tab1");
    statsPane.setAttribute("role", "tabpanel");
    statsPane.setAttribute("aria-labelledby", "tab1-tab");

    // Create a dropdown for selecting the question
    var dropdownContainer = document.createElement("div");
    dropdownContainer.className = "dropdown-container";
    statsPane.appendChild(dropdownContainer);

    var dropdown = document.createElement("select");
    dropdown.id = "question-dropdown";
    dropdown.className = "form-select";
    dropdown.addEventListener("change", () => {
        var selectedQuestion = dropdown.value;
        statsPane.innerHTML = ""; // Clear previous content
        statsPane.appendChild(dropdownContainer); // Re-add the dropdown
        displayConfusionMatrices(statsPane, selectedQuestion);
    });

    // Add options to the dropdown
    var option = document.createElement("option");
    option.value = "all";
    option.text = "All";
    dropdown.appendChild(option);
    matrix["questions"].forEach(question => {
        var option = document.createElement("option");
        option.value = question["varname"];
        option.text = question["question"];
        dropdown.appendChild(option);
    });

    dropdownContainer.appendChild(dropdown);

    // Display confusion matrices for all questions by default
    displayConfusionMatrices(statsPane, "all");

    // Add the other tabs
    for (var i = 0; i < matrix["tabs"].length; i++) {
        var li = document.createElement("li");
        ul.appendChild(li);
        li.className = "nav-item";
        li.setAttribute("role", "presentation");
        var button = document.createElement("button");
        li.appendChild(button);
        button.setAttribute("data-bs-toggle", "tab");
        button.setAttribute("id", "tab" + (i + 2) + "-tab");
        button.setAttribute("tabid", i + 2);
        button.setAttribute("data-bs-target", "#tab" + (i + 2));
        button.setAttribute("type", "button");
        button.setAttribute("role", "tab");
        button.setAttribute("aria-controls", i + 2);
        button.setAttribute("aria-selected", fullData["active"] === i + 2);
        button.className = fullData["active"] === i + 2 ? "nav-link active" : "nav-link";
        button.innerHTML = i + 1; // Adjust tab numbering to start from 1
        button.addEventListener("click", (e) => {
            fullData["active"] = parseInt(e.target.getAttribute("tabid"));
        });

        // Highlight nav-tab items based on disagreements
        var disagreements = calculateDisagreements(i);
        console.log(disagreements);
        var colorIntensity = Math.min(255, disagreements * 10); // Adjust the multiplier as needed
        button.style.backgroundColor = `rgb(255, ${255 - colorIntensity}, ${255 - colorIntensity})`;
    }

    // Add the content for the other tabs
    for (var i = 0; i < matrix["tabs"].length; i++) {
        var pane = document.createElement("div");
        tabcontent.appendChild(pane);
        pane.className = fullData["active"] === i + 2 ? "tab-pane active" : "tab-pane";
        pane.setAttribute("id", "tab" + (i + 2));
        pane.setAttribute("role", "tabpanel");
        pane.setAttribute("aria-labelledby", "tab" + (i + 2) + "-tab");

        // Add tab data
        var tabData = {
            "compoundID": matrix["tabs"][i]["compoundID"],
            "values": {}
        };
        // Add default value for all variables
        for (var q = 0; q < matrix["questions"].length; q++) {
            tabData["values"][matrix["questions"][q]["varname"]] = "";
        }

        buildTab(pane, i, tabData);
    }

    // Set active tab based on savedData
    document.getElementById("tab" + fullData["active"] + "-tab").click();
}

// Add a container for the checkboxes
var checkboxContainer = document.createElement("div");
checkboxContainer.id = "reviewer-checkboxes";
document.body.insertBefore(checkboxContainer, document.getElementById("tabs"));

// Run build function
build(fullData);

// Add a container for the checkboxes
var checkboxContainer = document.createElement("div");
checkboxContainer.id = "reviewer-checkboxes";
document.body.insertBefore(checkboxContainer, document.getElementById("tabs"));

// Run build function
build(fullData);