var fullData = FULLDATA;
var matrix = MATRIXDATA;
var instructions = INSTRUCTIONS;

console.log(fullData);
console.log(matrix);

// Function to get all unique labels from the data
var getLabels = function() {
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

// Function to calculate the proportion of total answers that were a particular label for each reviewer
var calculateProportions = function() {
    var proportions = {};
    var totalAnswers = {};

    for (var reviewer in fullData) {
        if (reviewer !== "active") {
            proportions[reviewer] = {};
            totalAnswers[reviewer] = 0;
            fullData[reviewer].forEach(row => {
                for (var varname in row["values"]) {
                    var label = row["values"][varname];
                    if (!proportions[reviewer][label]) {
                        proportions[reviewer][label] = 0;
                    }
                    proportions[reviewer][label]++;
                    totalAnswers[reviewer]++;
                }
            });
        }
    }

    for (var reviewer in proportions) {
        for (var label in proportions[reviewer]) {
            proportions[reviewer][label] = (proportions[reviewer][label] / totalAnswers[reviewer]).toFixed(2);
        }
    }

    return proportions;
};

// Function to display the proportions table
var displayProportionsTable = function(pane) {
    var proportions = calculateProportions();
    var labels = getLabels();

    var tableDiv = document.createElement("div");
    tableDiv.className = "proportions-table";
    pane.appendChild(tableDiv);

    var title = document.createElement("h4");
    title.innerHTML = "Proportions of Total Answers by Label for Each Reviewer";
    tableDiv.appendChild(title);

    var table = document.createElement("table");
    table.className = "table table-bordered";
    tableDiv.appendChild(table);

    var thead = document.createElement("thead");
    table.appendChild(thead);
    var tr = document.createElement("tr");
    thead.appendChild(tr);
    tr.appendChild(document.createElement("th")).innerHTML = "Reviewer";
    labels.forEach(label => {
        var th = document.createElement("th");
        th.innerHTML = label;
        tr.appendChild(th);
    });

    var tbody = document.createElement("tbody");
    table.appendChild(tbody);
    for (var reviewer in proportions) {
        var tr = document.createElement("tr");
        tbody.appendChild(tr);
        tr.appendChild(document.createElement("td")).innerHTML = reviewer;
        labels.forEach(label => {
            var td = document.createElement("td");
            td.innerHTML = proportions[reviewer][label] || "0.00";
            tr.appendChild(td);
        });
    }
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
                    matrix[value1][value2]++;
                }
            } else {
                var value1 = row1["values"][question];
                var value2 = row2["values"][question];
                matrix[value1][value2]++;
            }
        }
    }

    return matrix;
};

// Function to calculate statistics from the confusion matrix
var calculateStatistics = function(matrix, labels) {
    var stats = {
        "accuracy": 0,
        "precision": {},
        "recall": {},
        "f1": {}
    };

    var total = 0;
    var correct = 0;

    labels.forEach(label => {
        stats["precision"][label] = 0;
        stats["recall"][label] = 0;
        stats["f1"][label] = 0;
    });

    labels.forEach(label1 => {
        var rowTotal = 0;
        var colTotal = 0;
        labels.forEach(label2 => {
            rowTotal += matrix[label1][label2];
            colTotal += matrix[label2][label1];
            if (label1 === label2) {
                correct += matrix[label1][label2];
            }
            total += matrix[label1][label2];
        });

        if (rowTotal > 0) {
            stats["recall"][label1] = matrix[label1][label1] / rowTotal;
        }
        if (colTotal > 0) {
            stats["precision"][label1] = matrix[label1][label1] / colTotal;
        }
        if (stats["precision"][label1] + stats["recall"][label1] > 0) {
            stats["f1"][label1] = 2 * (stats["precision"][label1] * stats["recall"][label1]) / (stats["precision"][label1] + stats["recall"][label1]);
        }
    });

    if (total > 0) {
        stats["accuracy"] = correct / total;
    }

    // Format the precision, recall, and F1 scores to 2 decimal places
    labels.forEach(label => {
        stats["precision"][label] = stats["precision"][label].toFixed(2);
        stats["recall"][label] = stats["recall"][label].toFixed(2);
        stats["f1"][label] = stats["f1"][label].toFixed(2);
    });

    stats["accuracy"] = stats["accuracy"].toFixed(2);

    return stats;
};

// Function to display confusion matrices and statistics
var displayConfusionMatrices = function(pane, question, filteredData) {
    var checkedReviewers = [];
    for (var reviewer in filteredData) {
        if (reviewer !== "active") {
            checkedReviewers.push(reviewer);
        }
    }

    var labels = getLabels(filteredData);
    var confusionMatrices = {};
    var statistics = {};

    for (var i = 0; i < checkedReviewers.length; i++) {
        for (var j = i + 1; j < checkedReviewers.length; j++) {
            var reviewer1 = checkedReviewers[i];
            var reviewer2 = checkedReviewers[j];
            var matrix = calculateConfusionMatrix(reviewer1, reviewer2, labels, question, filteredData);
            confusionMatrices[reviewer1 + " vs " + reviewer2] = matrix;
            statistics[reviewer1 + " vs " + reviewer2] = calculateStatistics(matrix, labels);
        }
    }

    // Display the confusion matrices and statistics
    for (var key in confusionMatrices) {
        var matrix = confusionMatrices[key];
        var stats = statistics[key];

        var matrixDiv = document.createElement("div");
        matrixDiv.className = "confusion-matrix";
        pane.appendChild(matrixDiv);

        var title = document.createElement("h4");
        title.innerHTML = key;
        matrixDiv.appendChild(title);

        var table = document.createElement("table");
        table.className = "table table-bordered";
        matrixDiv.appendChild(table);

        var thead = document.createElement("thead");
        table.appendChild(thead);
        var tr = document.createElement("tr");
        thead.appendChild(tr);
        tr.appendChild(document.createElement("th"));
        labels.forEach(label => {
            var th = document.createElement("th");
            th.innerHTML = label;
            tr.appendChild(th);
        });

        var tbody = document.createElement("tbody");
        table.appendChild(tbody);
        labels.forEach(label1 => {
            var tr = document.createElement("tr");
            tbody.appendChild(tr);
            var th = document.createElement("th");
            th.innerHTML = label1;
            tr.appendChild(th);
            labels.forEach(label2 => {
                var td = document.createElement("td");
                td.innerHTML = matrix[label1][label2];
                tr.appendChild(td);
            });
        });

        var statsDiv = document.createElement("div");
        statsDiv.className = "statistics";
        pane.appendChild(statsDiv);

        var statsTitle = document.createElement("h4");
        statsTitle.innerHTML = "Statistics for " + key;
        statsDiv.appendChild(statsTitle);

        var statsTable = document.createElement("table");
        statsTable.className = "table table-bordered";
        statsDiv.appendChild(statsTable);

        var statsThead = document.createElement("thead");
        statsTable.appendChild(statsThead);
        var statsTr = document.createElement("tr");
        statsThead.appendChild(statsTr);
        statsTr.appendChild(document.createElement("th"));
        statsTr.appendChild(document.createElement("th")).innerHTML = "Precision";
        statsTr.appendChild(document.createElement("th")).innerHTML = "Recall";
        statsTr.appendChild(document.createElement("th")).innerHTML = "F1 Score";

        var statsTbody = document.createElement("tbody");
        statsTable.appendChild(statsTbody);
        labels.forEach(label => {
            var statsTr = document.createElement("tr");
            statsTbody.appendChild(statsTr);
            statsTr.appendChild(document.createElement("td")).innerHTML = label;
            statsTr.appendChild(document.createElement("td")).innerHTML = stats["precision"][label];
            statsTr.appendChild(document.createElement("td")).innerHTML = stats["recall"][label];
            statsTr.appendChild(document.createElement("td")).innerHTML = stats["f1"][label];
        });

        var accuracyTr = document.createElement("tr");
        statsTbody.appendChild(accuracyTr);
        accuracyTr.appendChild(document.createElement("td")).innerHTML = "Accuracy";
        accuracyTr.appendChild(document.createElement("td")).setAttribute("colspan", 3);
        accuracyTr.appendChild(document.createElement("td")).innerHTML = stats["accuracy"];
    }
};

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
                var filteredData = { "active": fullData["active"] };
                for (var rev in fullData) {
                    if (rev !== "active" && document.getElementById(rev).checked) {
                        filteredData[rev] = fullData[rev];
                    }
                }
                build(filteredData); // Rebuild the tabs and tables with filtered data
            });
            label.appendChild(checkbox);
            label.appendChild(document.createTextNode(reviewer));
            root.appendChild(label);
        }
    }
};

var checkAgreement = function(values) {
    var firstValue = values[0];
    for (var i = 1; i < values.length; i++) {
        if (values[i] !== firstValue) {
            return false;
        }
    }
    return true;
}

// Function to build the tab content
var buildTab = function(pane, i, tabData, is_active, filteredData) {
    var h3 = document.createElement("h3");
    h3.innerHTML = matrix["tabs"][i]["header"];
    pane.appendChild(h3);

    // Create a container for the scrollable boxes
    var scrollableContainer = document.createElement("div");
    pane.appendChild(scrollableContainer);

    // Create the first scrollable box for "text"
    var scrollable1 = document.createElement("div");
    var articleHeader = document.createElement("h4");
    articleHeader.innerHTML = "Article";
    if (matrix["tabs"][i]["articles"]) {
        articleHeader.innerHTML = "Cluster Description";
    }
    scrollable1.appendChild(articleHeader);
    var paras = matrix["tabs"][i]["text"].split('\n');
    for (var j = 0; j < paras.length; j++) {
        var pnws = paras[j].trim();
        if (pnws != "") {
            var p = document.createElement("p");
            p.innerHTML = pnws;
            scrollable1.appendChild(p);
        }
    }

    // Check if "summary_text" exists and create the second scrollable box if it does
    if (matrix["tabs"][i]["summary_text"]) {
        scrollableContainer.className = "scrollable-container-two";
        scrollable1.className = "scrollable-box-two";
        scrollableContainer.appendChild(scrollable1);

        var scrollable2 = document.createElement("div");
        scrollable2.className = "scrollable-box-two";
        scrollableContainer.appendChild(scrollable2);
        var summaryHeader = document.createElement("h4");
        summaryHeader.innerHTML = "Summary";
        scrollable2.appendChild(summaryHeader);
        var summaryParas = matrix["tabs"][i]["summary_text"].split('\n');
        for (var j = 0; j < summaryParas.length; j++) {
            var pnws = summaryParas[j].trim();
            if (pnws != "") {
                var p = document.createElement("p");
                p.innerHTML = pnws;
                scrollable2.appendChild(p);
            }
        }
    } else if (matrix["tabs"][i]["articles"]) {
        scrollableContainer.className = "scrollable-container-two";
        scrollable1.className = "scrollable-box-two";
        scrollableContainer.appendChild(scrollable1);
    
        var tableContainer = document.createElement("div");
        tableContainer.className = "scrollable-box-two";
        scrollableContainer.appendChild(tableContainer);
        var tableHeader = document.createElement("h4");
        tableHeader.innerHTML = "Article Titles";
        tableContainer.appendChild(tableHeader);
    
        var table = document.createElement("table");
        table.className = "table table-bordered table-striped table-hover";
        tableContainer.appendChild(table);
    
        var thead = document.createElement("thead");
        table.appendChild(thead);
        var tr = document.createElement("tr");
        thead.appendChild(tr);
    
        var tbody = document.createElement("tbody");
        table.appendChild(tbody);
    
        var articleTitles = matrix["tabs"][i]["articles"];
        articleTitles.forEach(title => {
            var tr = document.createElement("tr");
            tbody.appendChild(tr);
            var td = document.createElement("td");
            td.innerHTML = title;
            tr.appendChild(td);
        });
    } else {
        scrollableContainer.className = "scrollable-container-one";
        scrollable1.className = "scrollable-box-one";
        scrollableContainer.appendChild(scrollable1);
    }

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
    th.innerHTML = "Question";
    tr.appendChild(th);

    matrix["options"].forEach(option => {
        th = document.createElement("th");
        th.innerHTML = option["text"];
        tr.appendChild(th);
    });

    var tbody = document.createElement("tbody");
    tbl.appendChild(tbody);

    matrix["questions"].forEach(question => {
        var tr = document.createElement("tr");
        tbody.appendChild(tr);

        var td = document.createElement("td");
        td.innerHTML = question["question"];
        tr.appendChild(td);

        var values = [];
        matrix["options"].forEach(option => {
            td = document.createElement("td");
            var reviewers = [];

            for (var reviewer in filteredData) {
                if (reviewer !== "active") {
                    filteredData[reviewer].forEach(row => {
                        if (JSON.stringify(row["compoundID"]) === JSON.stringify(matrix["tabs"][i]["compoundID"]) &&
                            row["values"][question["varname"]] === option["value"]) {
                            reviewers.push(reviewer);
                            values.push(option["value"]);
                        }
                    });
                }
            }

            td.innerHTML = reviewers.join(", ");
            tr.appendChild(td);
        });

        // Highlight the row based on agreement
        if (checkAgreement(values)) {
            tr.classList.add("table-success");
        } else {
            tr.classList.add("table-danger");
        }
    });
}

// Function to calculate the number of disagreements for a given tab
var calculateDisagreements = function(tabIndex) {
    var disagreements = 0;

    matrix["questions"].forEach(question => {
        var answers = {};

        for (var reviewer in fullData) {
            if (reviewer !== "active") {
                fullData[reviewer].forEach(row => {
                    if (JSON.stringify(row["compoundID"]) === JSON.stringify(matrix["tabs"][tabIndex]["compoundID"])) {
                        if (!answers[question["varname"]]) {
                            answers[question["varname"]] = new Set();
                        }
                        answers[question["varname"]].add(row["values"][question["varname"]]);
                    }
                });
            }
        }

        for (var answer in answers) {
            if (answers[answer].size > 1) {
                disagreements++;
            }
        }
    });

    return disagreements;
};

// Function to build the entire interface
var build = function(filteredData) {
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
    button.setAttribute("aria-selected", filteredData["active"] === 0);
    button.className = filteredData["active"] === 0 ? "nav-link active" : "nav-link";
    button.innerHTML = "Instructions";
    button.addEventListener("click", (e) => {
        filteredData["active"] = 0;
    });

    // Add the content for the instructions tab
    var tabcontent = document.createElement("div");
    root.appendChild(tabcontent);
    tabcontent.className = "tab-content bg-light";
    var pane = document.createElement("div");
    tabcontent.appendChild(pane);
    pane.className = filteredData["active"] === 0 ? "tab-pane active" : "tab-pane";
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
    button.setAttribute("aria-selected", filteredData["active"] === 1);
    button.className = filteredData["active"] === 1 ? "nav-link active" : "nav-link";
    button.innerHTML = "Statistics";
    button.addEventListener("click", (e) => {
        filteredData["active"] = 1;
    });

    // Add the content for the statistics tab
    var statsPane = document.createElement("div");
    tabcontent.appendChild(statsPane);
    statsPane.className = filteredData["active"] === 1 ? "tab-pane active" : "tab-pane";
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
        displayConfusionMatrices(statsPane, selectedQuestion, filteredData);
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
    displayConfusionMatrices(statsPane, "all", filteredData);

    // Display proportions table if matrix['single'] is present
    if (matrix['single']) {
        displayProportionsTable(statsPane);
    }

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
        button.setAttribute("aria-selected", filteredData["active"] === i + 2);
        button.className = filteredData["active"] === i + 2 ? "nav-link active" : "nav-link";
        tab_title = "Article " + (i + 1);
        button.innerHTML = tab_title; 
        // Calculate disagreements and set button color
        var disagreements = calculateDisagreements(i);
        var colorIntensity = Math.min(255, disagreements * 10); // Adjust the multiplier as needed
        button.style.backgroundColor = `rgb(255, ${255 - colorIntensity}, ${255 - colorIntensity})`;

        button.addEventListener("click", (e) => {
            filteredData["active"] = parseInt(e.target.getAttribute("tabid"));
        });
    }

    // Add the content for the other tabs
    for (var i = 0; i < matrix["tabs"].length; i++) {
        var pane = document.createElement("div");
        tabcontent.appendChild(pane);
        pane.className = filteredData["active"] === i + 2 ? "tab-pane active" : "tab-pane";
        pane.setAttribute("id", "tab" + (i + 2));
        pane.setAttribute("role", "tabpanel");
        pane.setAttribute("aria-labelledby", "tab" + (i + 2) + "-tab");

        var tabData = {
            "compoundID": matrix["tabs"][i]["compoundID"],
            "values": {}
        };
        // Add default value for all variables
        for (var q = 0; q < matrix["questions"].length; q++) {
            tabData["values"][matrix["questions"][q]["varname"]] = "";
        }

        buildTab(pane, i, tabData, i + 2 == filteredData["active"], filteredData);
    }

    // Set active tab based on savedData
    document.getElementById("tab" + filteredData["active"] + "-tab").click();
}

// Add a container for the checkboxes
var checkboxContainer = document.createElement("div");
checkboxContainer.id = "reviewer-checkboxes";
document.body.insertBefore(checkboxContainer, document.getElementById("tabs"));

// Run build function
build(fullData);
