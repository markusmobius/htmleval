// Inputs: 
// - Instructions: The instructions for the evaluation (a list of strings)
// - DataMatrix: The data we need to fill in. It should be organised in such a way that it fills.
// - StructureMatrix: This gives the "structure" of the evaluation. 

// Example:
// In this example we have two tabs. Each tabs contain a scrollbox. Then they contain "nested" content. This content has two tabs. The first tab contains a text block, a single question checkbox, and a table row unique select.
// The second tab contains a text block and a single question checkbox.

// overall_data = [
//     {   
//         "tab_id": "name1",
//         "content": [
//             {
//                 "type": "scrollbox",
//                 "header": {"text": "ScrollBox", "size": 2},
//                 "text": "this is a scrollbox \n and here is line 2"
//             },
//             {
//                 "type": "inner_tabs",
//                 "inner_tab_id": "name2",  
//                 "content": [
//                     {
//                         "inner_tab_id": "inner_tab11",
//                         "content":
//                         [

//                             {
//                                 "type": "text",
//                                 "header": {"text": "Text Title", "size": 2},
//                                 "text": "Here goes some text"
//                             },
//                             {
//                                 "type": "single-question-checkbox",
//                                 "varname": "favourite_colour",
//                                 "question": "What is your favourite colour?",
//                                 "options": [{"opt_name": "red", "text": "Red"}, {"opt_name": "blue", "text": "Blue"}, {"opt_name": "green", "text": "Green"}]
//                             },
//                             {
//                                 "type": "single-question-checkbox",
//                                 "varname": "favourite_animal",
//                                 "question": "What is your favourite animal?",
//                                 "options": [{"opt_name": "dog", "text": "Dog"}, {"opt_name": "cat", "text": "Cat"}, {"opt_name": "fish", "text": "Fish"}]
//                             },
//                             {
//                                 "type": "table_row_unique_select",
//                                 "col_names": ["Action", "Actor"],
//                                 "questions": [{"varname": "dog_name", "text": "What is your dogs name?"}, {"varname": "why_cat_dead", "text": "Why, if there is a god, is my cat dead?"}],
//                                 "options": [[{"opt_name": "rex", "text": "Rex"}, {"opt_name": "fido", "text": "Fido"}], [{"opt_name": "god_hates_cats", "text": "God hates cats"}, {"opt_name": "cat_hates_god", "text": "Cat hates god"}]], 
//                                 "rows": [{"text_columns": ["this is the action", "this is the actor"], "css": ["danger", "success"]}, {"text_columns": ["this is the action", "this is the actor"], "css": ["danger", "success"]}]
//                             }
//                         ]
//                     },
//                     {
//                         "inner_tab_id": "inner_tab12",
//                         "content":
//                         [
//                             {
//                                 "type": "text",
//                                 "header": {"text": "Text Title", "size": 2},
//                                 "text": "Here goes some text"
//                             },
//                             {
//                                 "type": "single-question-checkbox",
//                                 "varname": "favourite_colour",
//                                 "question": "What is your favourite colour?",
//                                 "options": [{"opt_name": "red", "text": "Red"}, {"opt_name": "turqoise", "text": "Turqoise"}, {"opt_name": "green", "text": "Green"}]
//                             }
//                         ]
//                     }
//                 ]
//             }
//         ]
//     },
//     {
//         "tab_id": "tab2",
//         "content": [
//             {
//                 "type": "scrollbox",
//                 "header": {"text": "ScrollBox", "size": 2},
//                 "text": "this is a scrollbox \n and here is line 2"
//             },
//             {
//                 "type": "inner_tabs",
//                 "inner_tab_id": "inner_tab2",
//                 "content": [
//                     {
//                         "inner_tab_id": "inner_tab21",
//                         "content":
//                         [

//                             {
//                                 "type": "text",
//                                 "header": {"text": "Text Title", "size": 2},
//                                 "text": "Here goes some text"
//                             },
//                             {
//                                 "type": "single-question-checkbox",
//                                 "varname": "favourite_colour",
//                                 "question": "What is your favourite colour?",
//                                 "options": [{"opt_name": "red", "text": "Red"}, {"opt_name": "blue", "text": "Blue"}, {"opt_name": "green", "text": "Green"}]
//                             },
//                             {
//                                 "type": "single-question-checkbox",
//                                 "varname": "favourite_animal",
//                                 "question": "What is your favourite animal?",
//                                 "options": [{"opt_name": "dog", "text": "Dog"}, {"opt_name": "cat", "text": "Cat"}, {"opt_name": "fish", "text": "Fish"}]
//                             },
//                             {
//                                 "type": "table_row_unique_select",
//                                 "col_names": ["Action", "Actor"],
//                                 "questions": [{"varname": "dog_name", "text": "What is your dogs name?"}, {"varname": "why_cat_dead", "text": "Why, if there is a god, is my cat dead?"}],
//                                 "options": [[{"opt_name": "rex", "text": "Rex"}, {"opt_name": "fido", "text": "Fido"}], [{"opt_name": "god_hates_cats", "text": "God hates cats"}, {"opt_name": "cat_hates_god", "text": "Cat hates god"}]], 
//                                 "rows": [{"text_columns": ["this is the action", "this is the actor"], "css": ["danger", "success"]}, {"text_columns": ["this is the action", "this is the actor"], "css": ["danger", "success"]}]
//                             }
//                         ]
//                     }
//                 ]
//             }
//         ]
//     }
// ] 

overall_data = OVERALL_DATA


full_data = FULL_DATA;

// New Full Data, actually probably should have one per "series" of checkboxes, because we only want one answer per question.
// This is a list of dictionaries. Each dictionary has a compoundID and a value. The compoundID is a dictionary with the outer, inner, varname, and opt_name.
// The value is the value of the checkbox.
// full_data = {"esther" :[{"compoundID": {"outer": "tab1", "inner": "inner_tab11", "varname": "favourite_colour"}, "value": "red"},
//     {"compoundID": {"outer": "tab1", "inner": "inner_tab11", "varname": "favourite_animal"}, "value": "dog"},
//     {"compoundID": {"outer": "tab1", "inner": "inner_tab11", "row": 1, "varname": "dog_name"}, "value": "rex"},
//     {"compoundID": {"outer": "tab1", "inner": "inner_tab11", "row": 1, "varname": "why_cat_dead"}, "value": "god_hates_cats"},
//     {"compoundID": {"outer": "tab1", "inner": "inner_tab12", "varname": "favourite_colour"}, "value": "turqoise"},
//     {"compoundID": {"outer": "tab2", "inner": "inner_tab21", "varname": "favourite_colour"}, "value": "red"},
//     {"compoundID": {"outer": "tab2", "inner": "inner_tab21", "varname": "favourite_animal"}, "value": "dog"},
//     {"compoundID": {"outer": "tab2", "inner": "inner_tab21", "row": 0, "varname": "dog_name"}, "value": "rex"},
//     {"compoundID": {"outer": "tab2", "inner": "inner_tab21", "row": 0, "varname": "why_cat_dead"}, "value": "god_hates_cats"},
//     {"compoundID": {"outer": "tab2", "inner": "inner_tab21", "row": 1, "varname": "dog_name"}, "value": "rex"},
//     {"compoundID": {"outer": "tab2", "inner": "inner_tab21", "row": 1, "varname": "why_cat_dead"}, "value": "god_hates_cats"}]}

// Let's start by building the building blocks we need. 


// Add a global variable to track the mode
var mode = "viewer"; // Change this to "edit" for the editable mode

var selectedEvaluators = [];

function createEvaluatorCheckboxes(full_data, selectedEvaluators) {
    var container = document.createElement("div");
    container.className = "evaluator-checkboxes";

    for (var evaluator in full_data) {
        var checkboxContainer = document.createElement("div");
        checkboxContainer.className = "form-check form-check-inline";

        var checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.className = "form-check-input";
        checkbox.id = evaluator;
        checkbox.value = evaluator;
        checkbox.checked = selectedEvaluators.includes(evaluator); // Reflect the current state of selectedEvaluators
        checkbox.addEventListener('change', function() {
            updateSelectedEvaluators();
        });

        var label = document.createElement("label");
        label.className = "form-check-label";
        label.htmlFor = evaluator;
        label.innerHTML = evaluator;

        checkboxContainer.appendChild(checkbox);
        checkboxContainer.appendChild(label);
        container.appendChild(checkboxContainer);
    }

    var root = document.getElementById("evaluator-checkboxes");
    root.innerHTML = ""; // Clear previous content
    root.appendChild(container);
}

function updateSelectedEvaluators() {
    const { activeTabId, activeInnerTabId } = getActiveTab();
    selectedEvaluators = [];
    var checkboxes = document.querySelectorAll('.evaluator-checkboxes input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        if (checkbox.checked) {
            selectedEvaluators.push(checkbox.value);
        }
    });
    build(overall_data, selectedEvaluators); // Rebuild the content with the updated selectedEvaluators
    setActiveTab(activeTabId, activeInnerTabId);
}

function initializeSelectedEvaluators(fullData) {
    selectedEvaluators = Object.keys(fullData);
}

var buildText = function(text_dict) {
    // This function builds a text block. It returns a list of things to append to the pane in order. 
    var to_append_to_pane = [];
    if (text_dict["header"] !== null) {
        var header = document.createElement("h" + text_dict["header"]["size"]);
        header.innerHTML = text_dict["header"]["text"];
        to_append_to_pane.push(header);
    }
    var text = document.createElement("p");
    text.innerHTML = text_dict["text"];
    to_append_to_pane.push(text); 
    return to_append_to_pane;
}

var buildScrollbox = function(scrollbox_dict) {
    // This function builds a scrollbox. It returns a list of things to append to the pane in order. 
    var to_append_to_pane = [];
    if (scrollbox_dict["header"] !== null) {
        var header = document.createElement("h" + scrollbox_dict["header"]["size"]);
        header.innerHTML = scrollbox_dict["header"]["text"];
        to_append_to_pane.push(header);
    }
    var scrollableContainer = document.createElement("div");
    scrollableContainer.className = "scrollable-container-one";

    var inner_div = document.createElement("div");
    inner_div.className = "scrollable-box-one";
    
    var text = scrollbox_dict['text'].split('\n');
    
    for (var j = 0; j < text.length; j++) {
        var pnws = text[j].trim();
        if (pnws != "") {
            var p = document.createElement("p");
            p.innerHTML = pnws;
            inner_div.appendChild(p);
        }
    }

    scrollableContainer.appendChild(inner_div);
    to_append_to_pane.push(scrollableContainer);

    return to_append_to_pane;
}

var buildSingleQuestionCheckbox = function(single_question_checkbox_dict, compoundID) {
    var to_append_to_pane = [];
    
    var container = document.createElement("div");
    container.className = "mb-3 row"; // Use mb-3 for margin bottom and row for flexbox
    container.id = 'single-question-checkbox';

    var question = document.createElement("label");
    question.className = "col-sm-6 col-form-label"; 
    question.innerHTML = single_question_checkbox_dict["question"];
    container.appendChild(question);

    var optionsContainer = document.createElement("div");
    optionsContainer.className = "col-sm-6 col-form-label"; // Use flexbox for inline checkboxes and center alignment

    var options = single_question_checkbox_dict["options"];
    var varname = single_question_checkbox_dict["varname"];
    
    for (var i = 0; i < options.length; i++) {
        var option = document.createElement("div");
        option.className = "form-check form-check-inline"; // Inline checkboxes

        var answers = selectedEvaluators.map(evaluator => {
            var fullDataEntry = full_data[evaluator].find(entry => 
                entry.compoundID.outer === compoundID.outer &&
                entry.compoundID.inner === compoundID.inner &&
                entry.compoundID.varname === varname
            );
            return fullDataEntry && fullDataEntry.value === options[i].opt_name ? options[i].opt_name : null;
        }).filter(answer => answer !== null);

        var label = document.createElement("label");
        label.className = "form-check-label";
        label.innerHTML = answers.join(", ");
        option.appendChild(label);
        optionsContainer.appendChild(option);
    }
    container.appendChild(optionsContainer);
    to_append_to_pane.push(container);
    return to_append_to_pane;
}

var buildTableRowUniqueSelect = function(table_row_unique_select_dict, compoundID) {
    var to_append_to_pane = [];
    var questions = table_row_unique_select_dict["questions"];
    var options = table_row_unique_select_dict["options"];
    var rows = table_row_unique_select_dict["rows"];
    var header = table_row_unique_select_dict["header"];
    
    var header_banner = document.createElement("h" + header["size"]);
    header_banner.innerHTML = header["text"];
    to_append_to_pane.push(header_banner);

    var tbl = document.createElement("table");
    tbl.className = "table table-striped table-hover";
    tbl.setAttribute("border", 1);

    var thead = document.createElement("thead");
    var header_row = document.createElement("tr");
    var col_names = table_row_unique_select_dict["col_names"];
    for (var i = 0; i < col_names.length; i++) {
        var th = document.createElement("th");
        th.innerHTML = col_names[i];
        header_row.appendChild(th);
    }
    for (var i = 0; i < questions.length; i++) {
        var th = document.createElement("th");
        th.innerHTML = questions[i]["text"];
        header_row.appendChild(th);
    }
    thead.appendChild(header_row);
    tbl.appendChild(thead);

    var tbody = document.createElement("tbody");
    for (var i = 0; i < rows.length; i++) {
        var row = document.createElement("tr");
        var text_columns = rows[i]["text_columns"];
        for (var j = 0; j < text_columns.length; j++) {
            var td = document.createElement("td");
            td.innerHTML = text_columns[j];
            row.appendChild(td);
        }
        for (var j = 0; j < questions.length; j++) {
            var td = document.createElement("td");

            var answers = selectedEvaluators.map(evaluator => {
                var fullDataEntry = full_data[evaluator].find(entry => 
                    entry.compoundID.outer === compoundID.outer &&
                    entry.compoundID.inner === compoundID.inner &&
                    entry.compoundID.row === i.toString() &&
                    entry.compoundID.varname === questions[j].varname
                );
                return fullDataEntry ? fullDataEntry.value : null;
            }).filter(answer => answer !== null);

            td.innerHTML = answers.join(", ");
            // Check if an answer corresponds to a danger option. Can look to options list for that.
            var danger = false;
            for (var k = 0; k < answers.length; k++) {
                for (var l = 0; l < options[j].length; l++) {
                    if (answers[k] === options[j][l].opt_name && options[j][l].css === "danger") {
                        danger = true;
                        break;
                    }
                }
            }
            // Add the css class to the td if danger is true
            if (danger) {
                td.className = "table-danger";
            }
            else {
                td.className = "table-success";
            }

            row.appendChild(td);
        }
        tbody.appendChild(row);
    }
    tbl.appendChild(tbody);
    to_append_to_pane.push(tbl);
    return to_append_to_pane;
}

var buildStats = function(stats_dict, selectedEvaluators) {
    var to_append_to_pane = [];
    var header = document.createElement("h" + stats_dict["header"]["size"]);
    header.innerHTML = stats_dict["header"]["text"];
    to_append_to_pane.push(header);

    for (var i = 0; i < selectedEvaluators.length; i++) {
        var evaluator = selectedEvaluators[i];

        // Add evaluator's name as a header
        var evaluatorHeader = document.createElement("h3");
        evaluatorHeader.innerHTML = "Evaluator " + i;
        to_append_to_pane.push(evaluatorHeader);

        var tbl = document.createElement("table");
        tbl.className = "table table-striped table-hover";
        tbl.setAttribute("border", 1);

        var thead = document.createElement("thead");
        var header_row = document.createElement("tr");
        var th = document.createElement("th");
        th.innerHTML = "Question";
        header_row.appendChild(th);
        th = document.createElement("th");
        th.innerHTML = "n";
        header_row.appendChild(th);
        th = document.createElement("th");
        th.innerHTML = "Mean";
        header_row.appendChild(th);
        th = document.createElement("th");
        th.innerHTML = "Variance of Agreement";
        header_row.appendChild(th);
        thead.appendChild(header_row);
        tbl.appendChild(thead);

        var tbody = document.createElement("tbody");
        for (var j = 0; j < stats_dict["varnames"].length; j++) {
            var varname = stats_dict["varnames"][j].varname;
            var question = stats_dict["varnames"][j].question;
            var row = document.createElement("tr");

            var td = document.createElement("td");
            td.innerHTML = question;
            row.appendChild(td);

            td = document.createElement("td");
            var n = calculateSampleSize(varname, evaluator);
            td.innerHTML = n;
            row.appendChild(td);

            td = document.createElement("td");
            var mean = calculateMean(varname, evaluator);
            td.innerHTML = mean.toFixed(2);
            row.appendChild(td);

            td = document.createElement("td");
            var variance = calculateVarianceOfAgreement(varname, evaluator);
            td.innerHTML = variance.toFixed(2);
            row.appendChild(td);

            tbody.appendChild(row);
        }
        tbl.appendChild(tbody);
        to_append_to_pane.push(tbl);
    }
    console.log(to_append_to_pane);
    return to_append_to_pane;
}

function calculateSampleSize(varname, evaluator) {
    var values = full_data[evaluator].filter(entry => entry.compoundID.varname === varname);
    return values.length;
}

function calculateMean(varname, evaluator) {
    var values = full_data[evaluator].filter(entry => entry.compoundID.varname === varname).map(entry => entry.value === "yes" ? 1 : 0);
    if (values.length === 0) return 0;
    var mean = values.reduce((a, b) => a + b, 0) / values.length;
    return mean;
}

function calculateVarianceOfAgreement(varname, evaluator) {
    var values = full_data[evaluator].filter(entry => entry.compoundID.varname === varname).map(entry => entry.value === "yes" ? 1 : 0);
    if (values.length === 0) return 0;
    var mean = values.reduce((a, b) => a + b, 0) / values.length;
    var variance = values.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / values.length;
    return variance;
}

// Update buildBlock function to pass compoundID
var buildBlock = function(block, compoundID, selectedEvaluators) {
    // This function reads the json for a "block" and then calls the appropriate function to build it. 
    if (block["type"] == "text") {
        console.log("text");
        return buildText(block);
    } else if (block["type"] == "scrollbox") {
        console.log("scrollbox");
        return buildScrollbox(block);
    } else if (block["type"] == "single-question-checkbox") {
        console.log("single-question-checkbox");
        return buildSingleQuestionCheckbox(block, compoundID, selectedEvaluators);
    } else if (block["type"] == "table_row_unique_select") {
        console.log("table_row_unique_select");
        return buildTableRowUniqueSelect(block, compoundID, selectedEvaluators);
    } else if (block["type"] == "inner_tabs") {
        console.log("inner_tabs");
        return buildTabs(block["content"], false, selectedEvaluators, compoundID);
    } else if (block["type"] == "stats") {
        console.log("stats");
        return buildStats(block, selectedEvaluators);
    }
}

var buildContent = function(content, compoundID, selectedEvaluators) {
    // This function reads the json for a "content" and then calls the appropriate function to build it. 
    var to_append_to_pane = [];
    for (var i = 0; i < content.length; i++) {
        var block = content[i];
        var newCompoundID = { ...compoundID, inner: block.inner_tab_id || compoundID.inner };
        var to_append = buildBlock(block, newCompoundID, selectedEvaluators);
        to_append_to_pane = to_append_to_pane.concat(to_append);
    }
    return to_append_to_pane;
}

function updateFullData(element) {
    if (mode === "viewer") return; // Skip updating data in viewer mode

    const idParts = element.id.split('|');
    if (element.type === "checkbox") {
        var outer = idParts[0];
        var inner = idParts[1];
        var varname = idParts[2];
        var opt_name = idParts[3];
        var compoundID = { outer, inner, varname, opt_name };
    } else if (element.tagName === "SELECT") {
        var outer = idParts[0];
        var inner = idParts[1];
        var row = idParts[2];
        var varname = idParts[3];
        var compoundID = { outer, inner, row, varname };
    }

    if (element.type === "checkbox") {
        // Uncheck other checkboxes for the same question using the parent element
        const parent = element.closest('div#single-question-checkbox');
        const checkboxes = parent.querySelectorAll(`input[type="checkbox"][id^="${outer}|${inner}|${varname}"]`);
        checkboxes.forEach(checkbox => {
            if (checkbox !== element) {
                checkbox.checked = false;
            }
        });
    }

}

function checkTabCompletion(tabId) {
    const tabPane = document.getElementById(tabId);
    if (!tabPane) return 0; // Exit if tabPane is not found

    let dangerCount = 0;

    // Check nested tabs first
    const nestedTabs = tabPane.querySelectorAll('.tab-pane');
    nestedTabs.forEach(nestedTab => {
        console.log(`Checking nested tab ${nestedTab.id}`);
        dangerCount += checkTabCompletion(nestedTab.id);
    });

    // Check the current tab
    // Recall we no longer have checkboxes and selects. We now just print the actual reviewer answers. So what we need to do is: 

    // Maybe as a quick fix we can just check how many times "no" appears in the tables on that tab.
    // Although it should be no on its own, so maybe we can just check if it includes no and nothing else in a cell. 
    const tableCells = tabPane.querySelectorAll('td');
    tableCells.forEach(cell => {
        const cellText = cell.innerText.trim();
        if (/^no$/.test(cellText) && !/yes/.test(cellText)) {
            dangerCount++;
        }
    });

    // Update tab color based on dangerCount
    const tabButton = document.querySelector(`button[aria-controls="${tabId}"]`);
    if (tabButton) {
        const redIntensity = Math.min(255, dangerCount * 10); // Adjust the multiplier as needed
        tabButton.style.backgroundColor = `rgb(255, ${255 - redIntensity}, ${255 - redIntensity})`;
    }
    

    return dangerCount;
}

function addInputEventListeners() {
    const inputs = document.querySelectorAll('input[type="checkbox"], select');
    inputs.forEach(input => {
        input.addEventListener('change', () => {
            if (mode === "viewer") return; // Skip event handling in viewer mode

            updateFullData(input);
            const tabPane = input.closest('.tab-pane');
            if (tabPane) {
                const outermostTabPane = tabPane.closest('.tab-content').closest('.tab-pane');
                const outermostTabId = outermostTabPane ? outermostTabPane.id : tabPane.id;
                checkTabCompletion(outermostTabId);
            }

            // If we're dealing with select, we'll want to update the background of the td.
            // Need to use the id to find in overall_data the css class. Recall that the id is outer|inner|row|varname.
            // Index of varname will give what options list we should be looking at. Then use the value to find the css class.
            if (input.tagName === "SELECT") {
                const idParts = input.id.split('|');
                const outer = idParts[0];
                const inner = idParts[1];
                const row = idParts[2];
                const varname = idParts[3];

                let block = overall_data.find(block => block.tab_id === outer);
                if (!block) {
                    console.error(`No block found with tab_id: ${outer}`);
                    return;
                }

                let innerBlock = block.content.find(block => block.inner_tab_id === inner);
                if (!innerBlock) {
                    // If not found directly, search recursively in nested inner_tabs
                    const findInnerBlock = (content) => {
                        for (let item of content) {
                            if (item.type === "inner_tabs") {
                                let found = item.content.find(innerItem => innerItem.inner_tab_id === inner);
                                if (found) return found;
                                found = findInnerBlock(item.content);
                                if (found) return found;
                            }
                        }
                        return null;
                    };
                    innerBlock = findInnerBlock(block.content);
                    if (!innerBlock) {
                        console.error(`No inner block found with inner_tab_id: ${inner} in tab_id: ${outer}`);
                        return;
                    }
                }

                let finalBlock = innerBlock.content.find(block => block.varname === varname);
                if (!finalBlock) {
                    // go through items in innerBlock one by one. Each time, try to identify "question", if no question, continue.
                    // Then when you find question, (this is a list of dictionaries) look for the one with the varname.
                    // Keep number, go back one step and find the options list with that number.
                    // Then find the css class.
                    // Step 1 enumerate
                    for (var i = 0; i < innerBlock.content.length; i++) {
                        var finalestblock = innerBlock.content[i];
                        if (finalestblock.type === "table_row_unique_select") {
                            for (var j = 0; j < finalestblock.questions.length; j++) {
                                if (finalestblock.questions[j].varname === varname) {
                                    var options = finalestblock.options[j];
                                    var opt = options.find(option => option.opt_name === input.value);
                                    if (opt && opt.css) {
                                        input.closest('td').className = "table-" + opt.css;
                                    }
                                    else {
                                        input.closest('td').className = "";
                                    }
                                }
                            }
                        }
                    }
                }
            }
        });
    });
}

var build = function(overall_data, selectedEvaluators) {
    createEvaluatorCheckboxes(full_data, selectedEvaluators);
    var root = document.getElementById("tabs");
    root.innerHTML = ""; // Clear previous content
    var content = buildTabs(overall_data, true, selectedEvaluators);
    for (var i = 0; i < content.length; i++) {
        root.appendChild(content[i]);
    }
    addInputEventListeners();
    const tabPanes = document.querySelectorAll('.tab-pane');
    tabPanes.forEach(tabPane => {
        const outermostTabPane = tabPane.closest('.tab-content').closest('.tab-pane');
        const outermostTabId = outermostTabPane ? outermostTabPane.id : tabPane.id;
        checkTabCompletion(outermostTabId);
    });
}
// Update buildTabs function to pass compoundID
var buildTabs = function(tabs, first = false, selectedEvaluators, compoundID = { outer: "", inner: "" }) {
    // This function builds the tabs. It returns a list of things to append to the root in order.
    var to_append_to_root = [];
    var dangerCounts = []; // Initialize an array to store danger counts for each tab

    // Add tabs_nav_bar
    var ul = document.createElement("ul");
    ul.className = "nav nav-tabs";
    ul.setAttribute("role", "tablist");

    // Add buttons for each tab. 
    var j = 1; // Initialize the variable j to 1
    for (var i = 0; i < tabs.length; i++) {
        (function(i) {
            var li = document.createElement("li");
            ul.appendChild(li);
            li.className = "nav-item";
            li.setAttribute("role", "presentation");
            var button = document.createElement("button");
            li.appendChild(button);
            let tabId; // Use let to create a block-scoped variable
            if (first == true) {
                tabId = tabs[i]['tab_id'];
            } else {
                tabId = tabs[i]['inner_tab_id'];
            }
            button.setAttribute("data-bs-toggle", "tab");
            button.setAttribute("id", tabId + "-tab");
            button.setAttribute("tabid", i);
            button.setAttribute("data-bs-target", "#" + tabId);
            button.setAttribute("type", "button");
            button.setAttribute("role", "tab");
            button.setAttribute("aria-controls", tabId);
            button.className = "nav-link";
            if (tabs[i].header) {
                button.innerHTML = tabs[i].header.text;
            } else {
                button.innerHTML = j; // Use the variable j for numbering
                j++; // Increment j only when the tab does not have a header
            }

            // Add event listener to open the first inner tab when an outermost tab is clicked
            button.addEventListener('click', function() {
                console.log(`Opening first inner tab for ${tabId}`);
                const innerTabPane = document.querySelector(`#${tabId} .tab-content`);
                console.log(innerTabPane);
                if (innerTabPane) {
                    const activeInnerTab = innerTabPane.querySelector('.tab-pane.active');
                    if (!activeInnerTab) {
                        const firstInnerTabButton = document.querySelector(`#${tabId} .nav-tabs .nav-link`);
                        if (firstInnerTabButton) {
                            firstInnerTabButton.click();
                        }
                    }
                }
            });
        })(i);
    }

    to_append_to_root.push(ul);

    var tabcontent = document.createElement("div");
    tabcontent.className = "tab-content bg-light";

    for (var i = 0; i < tabs.length; i++) {
        var pane = document.createElement("div");
        tabcontent.appendChild(pane);
        if (first == true) {
            tabId = tabs[i]['tab_id'];
            newCompoundID = { outer: tabId, inner: "" };
        } else {
            tabId = tabs[i]['inner_tab_id'];
            newCompoundID = { outer: compoundID.outer, inner: tabId };
        }
        pane.className = "tab-pane";
        pane.setAttribute("id", tabId);
        pane.setAttribute("role", "tabpanel");
        pane.setAttribute("aria-labelledby", tabId + "-tab");
        pane.innerHTML = "";
        var content = buildContent(tabs[i]["content"], newCompoundID, selectedEvaluators);
        console.log("Content to append:", content); // Debugging log
        for (var j = 0; j < content.length; j++) {
            if (content[j] instanceof Node) {
                pane.appendChild(content[j]);
            } else {
                console.error("Invalid node:", content[j]); // Debugging log
            }
        }

        // Calculate danger count for the current tab
        var dangerCount = calculateDangerCount(newCompoundID);
        dangerCounts.push(dangerCount); // Add to the danger counts array

        // Update tab color based on dangerCount
        const tabButton = document.querySelector(`button[aria-controls="${tabId}"]`);
        if (tabButton) {
            const redIntensity = Math.min(255, dangerCount * 20); // Adjust the multiplier as needed
            tabButton.style.backgroundColor = `rgb(255, ${255 - redIntensity}, ${255 - redIntensity})`;
        }
    }
    to_append_to_root.push(tabcontent);

    // Update outer tab color based on totalDangerCount
    if (first) {
        const totalDangerCount = dangerCounts.reduce((a, b) => a + b, 0); // Sum of all inner tab danger counts
        const outerTabButton = document.querySelector(`button[aria-controls="${compoundID.outer}"]`);
        if (outerTabButton) {
            const redIntensity = Math.min(255, totalDangerCount * 20); // Adjust the multiplier as needed
            outerTabButton.style.backgroundColor = `rgb(255, ${255 - redIntensity}, ${255 - redIntensity})`;
        }
    }

    return to_append_to_root;
}

function calculateDangerCount(compoundID) {
    let dangerCount = 0;

    selectedEvaluators.forEach(evaluator => {
        full_data[evaluator].forEach(entry => {
            if (entry.compoundID.outer === compoundID.outer && entry.compoundID.inner === compoundID.inner) {
                const block = overall_data.find(block => block.tab_id === compoundID.outer);
                if (block) {
                    const innerBlock = block.content.find(block => block.inner_tab_id === compoundID.inner);
                    if (innerBlock) {
                        const finalBlock = innerBlock.content.find(block => block.varname === entry.compoundID.varname);
                        if (finalBlock) {
                            const options = finalBlock.options.find(option => option.opt_name === entry.value);
                            if (options && options.css === "danger") {
                                dangerCount++;
                            }
                        }
                    }
                }
            }
        });
    });

    return dangerCount;
}

function getActiveTab() {
    const activeTab = document.querySelector('.nav-tabs .nav-link.active');
    const activeInnerTab = document.querySelector('.tab-pane.active .nav-tabs .nav-link.active');
    return {
        activeTabId: activeTab ? activeTab.getAttribute('id') : null,
        activeInnerTabId: activeInnerTab ? activeInnerTab.getAttribute('id') : null
    };
}

function setActiveTab(activeTabId, activeInnerTabId) {
    if (activeTabId) {
        const activeTab = document.getElementById(activeTabId);
        if (activeTab) {
            activeTab.click();
        }
    }
    if (activeInnerTabId) {
        const activeInnerTab = document.getElementById(activeInnerTabId);
        if (activeInnerTab) {
            activeInnerTab.click();
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    initializeSelectedEvaluators(full_data);
    build(overall_data, selectedEvaluators);
    setActiveTab('statistics-tab', null); // Set the default active tab to the 0th tab
});


