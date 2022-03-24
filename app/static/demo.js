// application state
// data for each tab is populated when you switch to it
var state = {
    progress_complete: 0,
    dataset_selected_id: null,
    dataset_display_name: "no dataset selected",
    tabs:{
        0:null,
        1:null,
        2:null,
        3:null,
        4:null,
        5:null,
    }
}
function datasetElement(dataset_id, displayname, description, c1displayname, c2displayname){
htmlstring = 
`                                   
<div class="col mb-4">
<a href="#" class="dataset-item list-group-item-action" onclick="datasetClick(this, ${dataset_id})"
style="text-decoration: none;">
<div class="card">
<div class="card-header">
<h6>
${displayname}
</h6>
</div>
<div class="card-body">
<p>${description}</p>
<ul class="list-unstyled">
<li><b>Corpus 1: </b> ${c1displayname} 
</li>
<li><b>Corpus 2: </b> ${c2displayname} 
</li>
</ul>
</div>
</div>
</a>
</div>`
return htmlstring
}
function updateTabZeroData(){}
function updateTabOneData()
{
all_datasets = "" 
tab = 1
for (key in Object.keys(state.tabs[tab])) {
    dataset_id = state.tabs[tab][key].example_id
    displayname = state.tabs[tab][key].display_name
    description = state.tabs[tab][key].description
    c1displayname = state.tabs[tab][key].corpus_1_display_name
    c2displayname = state.tabs[tab][key].corpus_2_display_name
    all_datasets += datasetElement(dataset_id, displayname, description, c1displayname, c2displayname)
}
p = document.getElementById("dataset-parent");
p.innerHTML = all_datasets
}
function updateTabTwoData()
{}
function updateTabThreeData()
{}
function updateTabFourData()
{}
function getTabZeroData()
{
return null;
}
function getTabOneData()
{
$.ajax({
        method: "GET",
        url: "getExamplesMetadata"
    }).done(function(response){
        state.tabs[1]= response;
        updateTabOneData()
    });
}
function getTabTwoData()
{
}
function getTabThreeData()
{
// for every possible 

}
function getTabFourData()
{}
function getTabData(index)
{
    // gets data to populate the tab specified by argument index
    // updates the app's global state variable
    // propagates updates to the dom
    console.log("getting tab data for tab" + index)
    switch(index) {
        case 0:
            state.tabs[0] = getTabZeroData();
            break;
        case 1:
            state.tabs[1] = getTabOneData();
            break;
        case 2:
            state.tabs[2] = getTabTwoData();
            break;
        case 3:
            state.tabs[3] = getTabThreeData();
            break;
        case 4:
            state.tabs[4] = getTabFourData();
            break;
        default:
            console.log("unknown tab data requested")
            return 
      } 
}
function openTabIndex(index)
{
    var i, tab_content;
    var list_items = document.getElementById("page-nav-list").getElementsByClassName("nav-link");
    // error check index
    if (index < 0 || index >= list_items.length)
    {
        console.error(`Tried to open tab with invalid index: ${index}`)
        return;
    }
    // Find current tab button
    var page_nav = document.getElementById("page-nav-list");
    var tabs = page_nav.getElementsByClassName("nav-link");
    // if we are already on the requested tab, do nothing 
    if(tabs[index].id.split("-")[1] == index){
        return;
    }
    // otherwise hide all tabs but the one we want to switch to
    tab_content = document.getElementsByClassName("content-page");
    for(i = 0; i < index; ++i)
    {
        tab_content[i].style.display = "none";
        tabs[i].classList.remove("active")
    }
    for(i = index+1; i < tab_content.length; ++i)
    {
        tab_content[i].style.display = "none";
        tabs[i].classList.remove("active")
    }
    // switch the active tab in the nav
    tabs[index].classList.add("active");
    // show the content of the tab we want to switch to 
    tab_content[index].style.display = "block";
    // make ajax request to get the data for the current tab
    getTabData(index)
}

function openTab(evt, target)
{
    var tgt_id = target.split("-")[1]-1;
    openTabIndex(tgt_id)
}


function nextTab(evt){
    var nav_list = document.getElementById("page-nav-list");
    var list_items = nav_list.getElementsByClassName("nav-link");
    var i;
    for (i = 0; i < list_items.length; ++i)
    {
        if(list_items[i].classList.contains("active")) // Find active class button
        {
            break;
        }
    }
    openTabIndex(i+1);
}


function previousTab(evt){
    var nav_list = document.getElementById("page-nav-list");
    var list_items = nav_list.getElementsByClassName("nav-link");
    var i;
    for (i = 0; i < list_items.length; ++i)
    {
        if(list_items[i].classList.contains("active")) // Find active class button
        {
            break;
        }
    }
    openTabIndex(i-1);
}

function datasetClick(link, id)
{

    // Do not register clicks on a dataset already selected
    if(link.classList.contains("active"))
    {
        return;
    }

    $(".dataset-item").removeClass("bg-primary");
    $(".dataset-item").removeClass("text-white");
    $(".dataset-item").removeClass("active");
    $(".dataset-item .card").removeClass("bg-primary");

    link.getElementsByClassName("card")[0].classList.add("bg-primary");
    link.classList.add("text-white");
    link.classList.add("active");
    state.dataset_selected_id = id 
    console.log("set dataset selected id as")
    console.log(state.dataset_selected_id)
}


function setTableRows(table_id, data)
{
    table = document.getElementById(table_id);
    tbody = table.getElementsByTagName("tbody")[0];
    for (i in data["words"])
    {
        var row = tbody.insertRow(-1);  // Insert row at last position
        var cell1 = row.insertCell(0);  // Insert cells for #, Word, Distance
        var cell2 = row.insertCell(1);
        var cell3 = row.insertCell(2);
        cell1.innerHTML = parseInt(i)+1;
        var method = table_id.split("-",2)[1];
        cell2.innerHTML = "<a class='word-item' onclick='queryWord(event,\""+data["words"][i]+"\",\""+method+"\");nextTab();'>"+data['words'][i]+"</a>";
        cell3.innerHTML = data["scores"][i];
    }
}


function clearTableBody(table)
{
    // Clears the <tbody> element of a table. Header is kept intact.
    tbody = table.getElementsByTagName("tbody")[0];
    tbody.innerHTML = "";
}


function clearMostShifted()
{
    // Clears currently selected dataset (if any).
    var tables = $(".table-shifted-words");
    for (var i = 0; i < tables.length; ++i)
    {
        clearTableBody(tables[i]);
    }
}


function setTabs(name_a, name_b){
    document.getElementById("tab-a").innerHTML = name_a + "&#10142 " + name_b;
    document.getElementById("tab-b").innerHTML = name_b + "&#10142 " + name_a;
}

function loadMetadata(data)
{
    metadata = data;
}


function setProgress(p)
{
    // Set progress bar to p in [0, 100].
    p = Math.min(Math.max(0, p), p);
    document.getElementById("progress-bar").style.width = p.toString()+"%";
}


function progressUp(amount=20)
{
    progress_complete = Math.min(100, progress_complete+amount);
    setProgress(progress_complete);
}


function updateMostShifted()
{
    var n = document.getElementById("range-most-shifted").value;
    document.getElementById("n-most-shifted").innerHTML = n; // Update label
    var methods = ["s4", "global", "noise-aware"];

    for (i in methods)
    {
        hideTableRows("table-"+methods[i], n);
    }

}

function updateWordTable(table_id, data, limit=20)
{
    table = document.getElementById(table_id);
    tbody = table.getElementsByTagName("tbody")[0];
    for (i in data.slice(0, limit))
    {
        var row = tbody.insertRow(-1);  // Insert row at last position
        var cell1 = row.insertCell(0);  // Insert cells for Word, Distance
        // var cell2 = row.insertCell(1);
        cell1.innerHTML = "<a class='word-item' onclick='queryWord(event, \""+ data[i] + "\")'>"+data[i]+"</a>";
        // cell3.innerHTML = data["scores"][i];
    }
}


function setTargetLabel(target){
    document.getElementById("target-label").innerHTML = target;
}


function drawScatterPlot(target, x, labels, flip=false, react=false)
{
    var symbols = ["square", "circle"];
    var colors = ["#84b000", "#764e80"];
    var src_labels = [metadata[datasetSelected]["corpus_1"], metadata[datasetSelected]["corpus_2"]];
    if (flip)
    {
        symbols = symbols.reverse();
        colors = colors.reverse();
        src_labels = src_labels.reverse();
    }

    var x_target = {
        x: [x[0][0]],
        y: [x[0][1]],
        mode: "markers+text",
        type: "scatter",
        name: src_labels[0],
        text: labels[0],
        textposition: "top right",
        textfont: {
            family: "Raleway, sans-serif"
        },
        marker: {
            size: 12,
            color: colors[0],
            symbol: symbols[0]
        },
        hoverinfo: "text+name"
    };

    var _x = [];
    var _y = [];
    var _labels = [];
    for (var i = 1; i < x.length; ++i)
    {
        _x.push(x[i][0]);
        _y.push(x[i][1]);
        _labels.push(labels[i]);
    }
    var x_data = {
        x: _x,
        y: _y,
        mode: "markers+text",
        type: "scatter",
        name: src_labels[1],
        text: _labels,
        textposition: "top center",
        textfont: {
            family: "Raleway, sans-serif"
        },
        marker: {
            size : 12,
            color: colors[1],
            symbol: symbols[1]
        },
        hoverinfo: "text+name"
    };

    var data = [x_target, x_data];
    var layout = {
        // "showlegend": false,
        "paper_bgcolor": "#FAFAFA",
        "plot_bgcolor": "DDDDDD",
        "dragmode": "pan",
        font: {
            family: "Courier New, monospace",
            size: 18
        },
        margin: {
            l: 60,
            r: 40,
            b: 40,
            t: 40,
            pad: 4
        },
        xaxis: {
            "showgrid": true,
            "zeroline": false,
            "visible": true
        },
        yaxis: {
            "showgrid": true,
            "zeroline": false,
            "visible": true
        },
        legend: {
        },
        title: {
        }
    };

    var chart_configs = {
        "displaylogo": false,
        "scrollZoom": true,
        "responsive": true,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"]
    }
    var plot_div = document.getElementById(target);

    if (!react){ // If not react, then draw a new chart.
        var chart = Plotly.newPlot(target, data, layout, chart_configs);
        dragLayer = document.getElementsByClassName("nsewdrag")[0];
        // Add event handlers
        plot_div.on("plotly_hover", function(data){
            dragLayer.style.cursor = "pointer";
        });

        plot_div.on("plotly_unhover", function(data){
            dragLayer.style.cursor = "";
        });

        plot_div.on("plotly_click", function(data){
            console.log(data);
        });
    }
    else{  // Update existing chart
        var chart = Plotly.react(target, data, layout, chart_configs);
        dragLayer = document.getElementsByClassName("nsewdrag")[0];
    }

    return chart;
}


function updateNeighbors(element)
{
    // Updates number of neighbors shown in the plot according to value selected in the controls.
    target = document.getElementById("target-label").innerHTML;
    element.parentNode.getElementsByClassName("label-neighbors")[0].innerHTML = element.value;
    var flip=false;
    if(element.id == "k-range-a")
    {
        x = current_data["x_ab"];
        n = current_data["neighbors_ab"];
        plot_div = "plot-a";
    }
    else{
        x = current_data["x_ba"];
        n = current_data["neighbors_ba"];
        plot_div = "plot-b";
        flip=true;
    }
    drawScatterPlot(plot_div, x.slice(0, element.value), [target].concat(n.slice(0, element.value)), flip);
}


function updateSentenceTable(table_id, data, limit=1)
{
    table = document.getElementById(table_id);
    tbody = table.getElementsByTagName("tbody")[0];
    for (i in data.slice(0, limit))
    {
        var row = tbody.insertRow(-1);  // Insert row at last position
        var cell1 = row.insertCell(0);  // Insert cells for Word, Distance
        // var cell2 = row.insertCell(1);
        // cell1.innerHTML = "<a class='word-item' onclick='queryWord(event, \""+ data[i] + "\")'>"+data[i]+"</a>";
        // cell3.innerHTML = data["scores"][i];
        cell1.innerHTML = data[i];
    }
}


function updateSentences(s_src, s_tgt)
{
    $("#sent-src").html(s_src);

    $("#sent-tgt").html("");

    for (var i=0; i < s_tgt.length; ++i)
    {
        var div = document.createElement("div");
        div.classList.add("p-3");
        div.classList.add("bg-light");
        div.classList.add("border");
        div.classList.add("border-1");
        div.innerHTML = s_tgt[i];
        $("#sent-tgt").append(div);
    }
}


function swap_corpora()
{
    if(current_source == "a")
    {
        current_source = "b";
        document.getElementById("ex-header-1").innerHTML = metadata[datasetSelected]["corpus_2"];
        document.getElementById("ex-header-2").innerHTML = metadata[datasetSelected]["corpus_1"];
    }
    else{
        current_source = "a";
        document.getElementById("ex-header-1").innerHTML = metadata[datasetSelected]["corpus_1"];
        document.getElementById("ex-header-2").innerHTML = metadata[datasetSelected]["corpus_2"];
    }

    current_sent = 0;
    getNextSentence();
}


function getNextSentence()
{

    if (current_source == "a")
    {
        src = "sents_a";
        samples = "samples_a";
        tgt = "sents_b";
    }
    else{
        src = "sents_b";
        samples = "samples_b";
        tgt = "sents_a";
    }
    s_src = sent_data[src][current_sent];
    s_tgt = [];
    for (var i=0; i < sent_data[samples][current_sent].length; ++i)
    {
        s_tgt.push(sent_data[tgt][parseInt(sent_data[samples][current_sent][i])]);
    }
    updateSentences(s_src, s_tgt);
    current_sent += 1;
    if (current_sent >= sent_data[src].length)
    {
        current_sent = 0;
    }
}


function searchAutocomplete(element)
{
    var query = element.value;

    if(query.length < 2)
    {
        return;
    }
    var search_results = [];
    for(var i = 0; i < current_words.length; ++i)
    {
        if(current_words[i].toLowerCase().startsWith(query.toLowerCase()))
        {
            search_results.push(current_words[i]);
        }
    }

    var ul = document.getElementById("autocomplete-dropdown");
    ul.style.display = "block";
    ul.innerHTML = "";

    for(var i=0; i < Math.min(search_results.length, 3); ++i)
    {
        var item = document.createElement("button");
        item.innerHTML = search_results[i];
        item.type="button";
        item.classList.add("list-group-item");
        item.classList.add("list-group-item-action");
        item.onclick = function(evt){
            queryWord(element, evt.target.innerHTML);
            ul.style.display = "none";
        }

        ul.appendChild(item);
    }

}

function searchWord(evt)
{
    var target = document.getElementById("input-word-search").value;
    var method = document.querySelector('input[name="btnAlign"]:checked').value;
    queryWord(evt, target, method);
}


function switch_alignment_method(evt)
{
    var method = document.querySelector('input[name="btnAlign"]:checked').value;
    var target = document.getElementById("target-label").innerHTML;
    queryWord(evt, target);
}

function queryWord(evt, target, method=null)
{

    setTargetLabel(target);

    if(method == null)
    {
        method = document.querySelector('input[name="btnAlign"]:checked').value;
    }

    var radioBtnId = "#btn-align-"+method;
    console.log(method);
    console.log(radioBtnId);

    $(radioBtnId).prop("checked", true);

    // Clear table bodies
    var table_a = document.getElementById("table-a");
    var table_b = document.getElementById("table-b");
    clearTableBody(table_a);
    clearTableBody(table_b);

//    var table_ex_a = document.getElementById("table-ex-a");
//    var table_ex_b = document.getElementById("table-ex-b");
//    clearTableBody(table_ex_a);
//    clearTableBody(table_ex_b);

    $("#spinner-closest").removeClass("d-none");
    $("#spinner-examples").removeClass("d-none");

    $.ajax({
        method: "GET",
        url: "getWordContext",
        data: {"target": target, "method": method, "dataset": datasetSelected}
    }).done(function(response){
        if ("error" in response)
        {
            alert("An error occurred: " + response["error"]);
            return;
        }
        current_data = response;
        updateWordTable("table-a", response["neighbors_ab"]);
        updateWordTable("table-b", response["neighbors_ba"]);
        chart_a = drawScatterPlot("plot-a", response["x_ab"], [target].concat(response["neighbors_ab"]));
        chart_b = drawScatterPlot("plot-b", response["x_ba"], [target].concat(response["neighbors_ba"]), true);
        $("#k-range-a").trigger("input");
        $("#k-range-b").trigger("input");
        $("#spinner-closest").addClass("d-none");
    });

    // Query sentence examples
    $.ajax({
        method: "GET",
        url: "getSentenceExamples",
        data: {"target": target, "method": method, "dataset": datasetSelected}
    }).done(function(response){
        // updateSentenceTable("table-ex-a", response["sents_a"]);
        // updateSentenceTable("table-ex-b", response["sents_b"]);
        if("error" in response)
        {
            alert("An error occurred: " + response["error"]);
            return;
        }
        sent_data = response;
        document.getElementById("target-word-sent").innerHTML = target;
        getNextSentence();  // Select first sentence
        $("#spinner-examples").addClass("d-none");
    });
}


function addCommonFilter()
{
    var tables = document.getElementsByClassName("table-shifted-words");

    var commonWords = new Set();  // Stores words that are common across all tables.
    var tableWords = [];
    for (var i = 0; i < tables.length; ++i)
    {
        tbody = tables[i].getElementsByTagName("tbody")[0];
        // Create a set to store every word in each table.
        tableSet = new Set();
        for(var j = 0; j < tbody.rows.length; ++j)
        {
            var item = tbody.rows[j].getElementsByClassName("word-item")[0];
            tableSet.add(item.innerHTML);
        }
        tableWords.push(tableSet);
    }
    // Take the intersection of the 3 sets of words.
    commonWords = new Set([...tableWords[0]].filter(x => tableWords[1].has(x)));
    commonWords = new Set([...commonWords].filter(x => tableWords[2].has(x)));

    // Now highlight common words
    for (var i = 0; i < tables.length; ++i)
    {
        tbody = tables[i].getElementsByTagName("tbody")[0];
        for (var j = 0; j < tbody.rows.length; ++j)
        {
            var item = tbody.rows[j].getElementsByClassName("word-item")[0];
            if (commonWords.has(item.innerHTML) && tbody.rows[j].style.display != 'none')
            {
                tbody.rows[j].classList.add("highlight-common");
            }
            else{
                tbody.rows[j].style.display = 'none';
            }
        }
    }
}


function addUniqueFilter()
{
    var tables = document.getElementsByClassName("table-shifted-words");
    var tableWords = [];
    for (var i = 0; i < tables.length; ++i)
    {
        tbody = tables[i].getElementsByTagName("tbody")[0];
        // Create a set to store every word in each table.
        tableSet = new Set();
        for(var j = 0; j < tbody.rows.length; ++j)
        {
            var item = tbody.rows[j].getElementsByClassName("word-item")[0];
            tableSet.add(item.innerHTML);
        }
        tableWords.push(tableSet);
    }

    // Now highlight common words
    for (var i = 0; i < tables.length; ++i)
    {
        // Get words unique to current table
        const uniqueWords = new Set([...tableWords[i]].filter(x => !tableWords[(i+1)%tables.length].has(x) && !tableWords[(i+2)%tables.length].has(x)));
        tbody = tables[i].getElementsByTagName("tbody")[0];
        for (var j = 0; j < tbody.rows.length; ++j)
        {
            var item = tbody.rows[j].getElementsByClassName("word-item")[0];
            if (uniqueWords.has(item.innerHTML) && tbody.rows[j].style.display != 'none')
            {
                // item.classList.add("text-danger");
                tbody.rows[j].classList.add("highlight-unique");
            }
            else
            {
                tbody.rows[j].style.display = 'none';
            }
        }
    }
}


// Given a table id, shows the first `to_show` rows and hide the rest
function hideTableRows(table_id, to_show)
{
    table = document.getElementById(table_id);
    tbody = table.getElementsByTagName("tbody")[0];

    for (var j = 0; j < tbody.rows.length; ++j)
    {
        if (j < to_show)
        {
            tbody.rows[j].style.display = '';
        }
        else{
            tbody.rows[j].style.display = 'none';
        }
    }

}


function clearFilters()
{
    // Clear all word filters
    var tables = document.getElementsByClassName("table-shifted-words");
    // Now highlight common words
    for (var i = 0; i < tables.length; ++i)
    {
        // Get words unique to current table
        tbody = tables[i].getElementsByTagName("tbody")[0];
        for (var j = 0; j < tbody.rows.length; ++j)
        {
            tbody.rows[j].classList.remove("highlight-common");
            tbody.rows[j].classList.remove("highlight-unique");
            tbody.rows[j].style.display = '';
        }
    }
}

function loadDataset(is_initial_load)
{
    // make a call to the server's loadDataset endpoint to tell it to read a dataset from disk to memory
    // this makes sure that subsequent calls to a given dataset won't cause the server to re-read the dataset from disk
    // initial_load tells the server if it should expect to get an id to load
    // on the initial load we just tell the server to give us an id to load
    console.log("Here")
    $.ajax({
        method: "GET",
        url: "loadDataset",
        data: {initial_load: is_initial_load, id: state.dataset_selected_id}
    }).done(function(response){
        
    }).fail(function(response){
        console.log("there")
        if ("error" in response)
        {
            alert("An error occurred: " + response.responseText);
            return;
        }
    });
}
$(document).ready(function(){
    // tell server to load the first dataset in the background for us
    // todo get the id of a dataset to load when the app first loads somehow
    loadDataset(true)
});