// Inputs: 
// - Instructions: The instructions for the evaluation (a list of strings)
// - DataMatrix: The data we need to fill in. It should be organised in such a way that it fills.
// - StructureMatrix: This gives the "structure" of the evaluation. 

overall_data = OVERALL_DATA


fullData = null;


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
    // Need to create a flag that we can then do a querySelector on to find this "parent" div.
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
        var input = document.createElement("input");
        input.type = "checkbox";
        input.className = "form-check-input";
        input.id = `${compoundID.outer}|${compoundID.inner}|${varname}|${options[i].opt_name}`; // Ensure unique ID
        
        console.log(compoundID.outer, compoundID.inner, varname, options[i].opt_name);
        // Initialize checkbox value from fullData
        var fullDataEntry = fullData.find(entry => 
            entry.compoundID.outer === compoundID.outer &&
            entry.compoundID.inner === compoundID.inner &&
            entry.compoundID.varname === varname
        );
        if (fullDataEntry && fullDataEntry.value === options[i].opt_name) {
            input.checked = true;
        }

        var label = document.createElement("label");
        label.className = "form-check-label";
        // var span = document.createElement("span");
        label.innerHTML = options[i].text;
        // label.appendChild(span);
        label.For = input.id; // Match the label's htmlFor with the input's id
        option.appendChild(input);
        option.appendChild(label);
        optionsContainer.appendChild(option);
    }
    container.appendChild(optionsContainer);
    to_append_to_pane.push(container);
    return to_append_to_pane;
}

var buildTableRowUniqueSelect = function(table_row_unique_select_dict, compoundID) {
    // This function builds a table row unique select. It returns a list of things to append to the pane in order. 
    // Here we create a table, each row has an entry for each text column, then it has a dropdown for each question. This dropdown is populated with the options. 
    // Each dropdown is, moreover, given a unique ID which is the compoundID + the varname of the question.
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
    // Create the header row, needs column names for text columns, then also each question text as a header.
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
            var select = document.createElement("select");
            select.className = "form-control";
            select.id = `${compoundID.outer}|${compoundID.inner}|${i}|${questions[j].varname}`;
            
            // Add default "Select" option
            var defaultOption = document.createElement("option");
            defaultOption.value = ""; // Corresponds to value=""
            defaultOption.innerHTML = "Select";
            select.appendChild(defaultOption);

            var options = table_row_unique_select_dict["options"][j];
            for (var k = 0; k < options.length; k++) {
                var option = document.createElement("option");
                option.value = options[k]["opt_name"];
                option.innerHTML = options[k]["text"];
                select.appendChild(option);
            }

            // Initialize select value from fullData
            console.log(`Checking fullData for ${compoundID.outer}, ${compoundID.inner}, ${i}, ${questions[j].varname}`);
            var fullDataEntry = fullData.find(entry => 
                entry.compoundID.outer === compoundID.outer &&
                entry.compoundID.inner === compoundID.inner &&
                entry.compoundID.row === i.toString() &&
                entry.compoundID.varname === questions[j].varname
            );
            console.log(fullDataEntry);
            if (fullDataEntry) {
                console.log(`Setting select value to ${fullDataEntry.value}`);
                select.value = fullDataEntry.value;
                // Need to find the dictionary in options where the opt_name is the same as the value of the fullDataEntry
                var opt = options.find(option => option.opt_name === fullDataEntry.value);
                // now set the td containing our value to have the css class of the opt_name if it exists and the css exists. It will only give "success or danger" so needs to be mapped. 
                if (opt && opt.css) {
                    td.className = "table-" + opt.css; 
                }
            }

            td.appendChild(select);
            row.appendChild(td);
        }
        tbody.appendChild(row);
    }
    tbl.appendChild(tbody);
    to_append_to_pane.push(tbl);
    return to_append_to_pane;
}

var buildAnnotatedText = function(annotated_text_dict) {
    var to_append_to_pane = [];
    var paragraphs = annotated_text_dict["paragraphs"];

    var container = document.createElement("div");
    container.className = "annotated-text";

    // Create the interactive-text element
    var interactiveText = document.createElement('interactive-text');
    interactiveText.setAttribute('data', JSON.stringify({
        paragraphs: paragraphs.map(paragraph => ({
            fragments: paragraph.fragments.map(fragment => ({
                id: fragment.id,
                text: fragment.text,
                state: 'marked' // Assuming all fragments are marked
            }))
        }))
    }));

    container.appendChild(interactiveText);
    to_append_to_pane.push(container);

    return to_append_to_pane;
}
var buildMessageDisplay = function(message_display_dict) {
    var to_append_to_pane = [];
    var message_map = message_display_dict["content_map"];

    // Create the message-display element
    var messageDisplay = document.createElement('message-display');
    messageDisplay.setAttribute('content-map', JSON.stringify(message_map));

    to_append_to_pane.push(messageDisplay);

    return to_append_to_pane;
}

var buildBlock = function(block, compoundID) {
    if (block["type"] == "text") {
        console.log("text");
        return buildText(block);
    } else if (block["type"] == "scrollbox") {
        console.log("scrollbox");
        return buildScrollbox(block);
    } else if (block["type"] == "single-question-checkbox") {
        console.log("single-question-checkbox");
        return buildSingleQuestionCheckbox(block, compoundID);
    } else if (block["type"] == "table_row_unique_select") {
        console.log("table_row_unique_select");
        return buildTableRowUniqueSelect(block, compoundID);
    } else if (block["type"] == "inner_tabs") {
        console.log("inner_tabs");
        return buildTabs(block["content"], false, compoundID);
    } else if (block["type"] == "annotated_text") {
        console.log("annotated_text");
        return buildAnnotatedText(block);
    } else if (block["type"] == "message_display") {
        console.log("message_display");
        return buildMessageDisplay(block);
    }
}

var buildContent = function(content, compoundID) {
    // This function reads the json for a "content" and then calls the appropriate function to build it. 
    var to_append_to_pane = [];
    for (var i = 0; i < content.length; i++) {
        var block = content[i];
        var newCompoundID = { ...compoundID, inner: block.inner_tab_id || compoundID.inner };
        var to_append = buildBlock(block, newCompoundID);
        to_append_to_pane = to_append_to_pane.concat(to_append);
    }
    return to_append_to_pane;
}

function updateFullData(element) {
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

    // Update fullData
    const fullDataEntry = fullData.find(entry => JSON.stringify(entry.compoundID) === JSON.stringify(compoundID));
    if (fullDataEntry) {
        fullDataEntry.value = element.type === "checkbox" ? (element.checked ? opt_name : "") : element.value;
    } else {
        const newEntry = { compoundID, value: element.type === "checkbox" ? (element.checked ? opt_name : "") : element.value };
        fullData.push(newEntry);
    }

    console.log(`Updated fullData: ${JSON.stringify(compoundID)} = ${element.type === "checkbox" ? (element.checked ? opt_name : "") : element.value}`);
    console.log(fullData);
}

function checkTabCompletion(tabId) {
    const tabPane = document.getElementById(tabId);
    if (!tabPane) return; // Exit if tabPane is not found

    // Check nested tabs first
    const nestedTabs = tabPane.querySelectorAll('.tab-pane');
    nestedTabs.forEach(nestedTab => {
        console.log(`Checking nested tab ${nestedTab.id}`);
        checkTabCompletion(nestedTab.id);
    });

    var allFilled = true;
    // Start by checking checkbox groups
    const checkbox_groups = tabPane.querySelectorAll(`div#single-question-checkbox`);
    checkbox_groups.forEach(checkbox_group => {
        const checkboxes = checkbox_group.querySelectorAll('input[type="checkbox"]');
        let anyChecked = false;
        checkboxes.forEach(checkbox => {
            if (checkbox.checked) {
                anyChecked = true;
            }
        });
        if (!anyChecked) {
            allFilled = false;
            console.log(`Checkbox group ${checkbox_group.id} is not complete`);
        }
    });

    // Check select dropdowns
    const inputs = tabPane.querySelectorAll('select');
    inputs.forEach(input => {
        if (input.tagName === 'SELECT' && (input.value === '' || input.value === 'Select')) {
            allFilled = false;
        }
    });

    // Check if all nested tabs are complete
    const nestedTabButtons = tabPane.querySelectorAll('.nav-link');
    let allNestedTabsComplete = true;
    nestedTabButtons.forEach(button => {
        if (!button.classList.contains('bg-success-subtle')) {
            allNestedTabsComplete = false;
            console.log(`Tab ${button.innerHTML} is not complete`);
        }
    });

    const tabButton = document.querySelector(`button[aria-controls="${tabId}"]`);
    if (allFilled && allNestedTabsComplete) {
        tabButton.classList.add('bg-success-subtle');
        console.log(`Tab ${tabId} is complete`);
    } else {
        tabButton.classList.remove('bg-success-subtle');
        console.log(`Tab ${tabId} is not complete`);
    }
}

function addInputEventListeners() {
    const inputs = document.querySelectorAll('input[type="checkbox"], select');
    inputs.forEach(input => {
        input.addEventListener('change', () => {
            updateFullData(input);
            const tabPane = input.closest('.tab-pane');
            if (tabPane) {
                const outermostTabPane = tabPane.closest('.tab-content').closest('.tab-pane');
                const outermostTabId = outermostTabPane ? outermostTabPane.id : tabPane.id;
                checkTabCompletion(outermostTabId);
            }
            saveSurvey(); // Save survey data whenever a change is made

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

var initializeFullData = function(overall_data) {
    var fullData = [];
    var traverseContent = function(content, compoundID) {
        for (var i = 0; i < content.length; i++) {
            var block = content[i];
            var newCompoundID = { ...compoundID, inner: block.inner_tab_id || compoundID.inner };
            if (block.type === "single-question-checkbox") {
                fullData.push({ compoundID: { ...newCompoundID, varname: block.varname }, value: "" });
            } else if (block.type === "table_row_unique_select") {
                for (var j = 0; j < block.questions.length; j++) {
                    for (var k = 0; k < block.rows.length; k++) {
                        fullData.push({ compoundID: { ...newCompoundID, row: k, varname: block.questions[j].varname }, value: "" });
                    }
                }
            } else if (block.type === "inner_tabs") {
                traverseContent(block.content, newCompoundID);
            }
        }
    };

    for (var i = 0; i < overall_data.length; i++) {
        var compoundID = { outer: overall_data[i].tab_id, inner: "" };
        traverseContent(overall_data[i].content, compoundID);
    }

    return fullData;
};

// Update build function to call addInputEventListeners
var build = function(overall_data) {
    if (!fullData || fullData.length === 0) {
        fullData = initializeFullData(overall_data);
    }
    // This function attaches the whole to the root
    var root = document.getElementById("tabs");
    root.innerHTML = ""; // Clear previous content
    var content = buildTabs(overall_data, true);
    for (var i = 0; i < content.length; i++) {
        root.appendChild(content[i]);
    }
    addInputEventListeners();
    // Initial check for tab completion
    const tabPanes = document.querySelectorAll('.tab-pane');
    tabPanes.forEach(tabPane => {
        const outermostTabPane = tabPane.closest('.tab-content').closest('.tab-pane');
        const outermostTabId = outermostTabPane ? outermostTabPane.id : tabPane.id;
        checkTabCompletion(outermostTabId);
    });
    saveSurvey();
}

// Update buildTabs function to pass compoundID
var buildTabs = function(tabs, first = false, compoundID = { outer: "", inner: "" }) {
    // This function builds the tabs. It returns a list of things to append to the root in order.
    var to_append_to_root = [];
    // Add tabs_nav_bar
    var ul = document.createElement("ul");
    ul.className = "nav nav-tabs";
    ul.setAttribute("role", "tablist");

    // Add buttons for each tab. 
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
            button.innerHTML = tabs[i].header ? tabs[i].header.text : (i); // Set to appropriate name

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
        var content = buildContent(tabs[i]["content"], newCompoundID);
        for (var j = 0; j < content.length; j++) {
            pane.appendChild(content[j]);
        }
    }
    to_append_to_root.push(tabcontent);

    return to_append_to_root;
}




