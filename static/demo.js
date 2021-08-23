var metadata = {}; // Stores all metadata
var datasetSelected = 0; // Stores the name of currently selected dataset
var progress_complete = 0;  // Stores how much of the demo has progressed
var currentData = 0; // Stores current data from server-side
var chart_a, chart_b = 0; // Stores chart objects
var most_shifted = {"s4": {}, "global": {}, "noise-aware": {}}; // Stores most shifted words per alignment method


function openTab(evt, target)
{
    var i, x;
    var tgt_id = target.split("-")[1]-1;
    x = document.getElementsByClassName("content-page");
    for (i=0; i < x.length; ++i)
    {
        x[i].style.display = "none";
    }

    var page_nav = document.getElementById("page-nav-list");
    var tabs = page_nav.getElementsByClassName("nav-link");
    for (i=0; i < tabs.length; ++i)
    {
        tabs[i].classList.remove("active");
    }

    tabs[tgt_id].classList.add("active");
    document.getElementById(target).style.display = "block";
}


function openTabIndex(index)
{
    var i, tab_content;
    var list_items = document.getElementById("page-nav-list").getElementsByClassName("nav-link");
    if (index < 0 || index >= list_items.length)
    {
        return;
    }
    // Find current open tab
    tab_content = document.getElementsByClassName("content-page");
    for(i = 0; i < tab_content.length; ++i)
    {
        tab_content[i].style.display = "none";
    }
    // Find current tab button
    var page_nav = document.getElementById("page-nav-list");
    var tabs = page_nav.getElementsByClassName("nav-link");
    for (i = 0; i < tabs.length; ++i)
    {
        tabs[i].classList.remove("active");
    }

    // Show new content
    tabs[index].classList.add("active");
    tab_content[index].style.display = "block";
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


function setDatasetLabel(label){
    var element = document.getElementById("selected-dataset-label");

    // Define the human-readable name of each dataset.
    // TODO: Make it persistent or sent from backend. I.e., server gives list of available datasets.

    if (label in metadata)
    {
        element.innerHTML = metadata[label]["display_name"];
        element.classList.add("text-white");
    }
    else{
        element.innerHTML = label;
        element.classList.add("text-white");
    }
}


function deactivateButton(btn)
{
    btn.disabled = true;
}


function datasetClick(link, elem)
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

    // Enable the `Next` button on the dataset selection page.
    document.getElementById("btn-next-dataset").disabled = false;
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
        cell2.innerHTML = "<a class='word-item' onclick='queryWord(event,\""+data["words"][i]+"\");nextTab();'>"+data['words'][i]+"</a>";
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
    document.getElementById("tab-a").innerHTML = name_a + "&#10142" + name_b;
    document.getElementById("tab-b").innerHTML = name_b + "&#10142" + name_a;
}


function loadDataset(evt)
{
    // Requests a dataset from the server side.
    clearMostShifted();
    // TODO: add a spinner when loading dataset.
    var value = $(".dataset-item.active")[0].getAttribute("value");
    var methods = ["s4", "global", "noise-aware"];

    $.ajax({
        method: "GET",
        url: "loadDataset",
        data: {"data": value}
    }).done(function(response){
        // Once data is loaded, set the dataset label
        setDatasetLabel(value);
        // Then, get most shifted words
        for (i in methods)
        {
            var tab_index = i;
            $.ajax({
            method: "GET",
            url: "getMostShiftedWords",
            data: {"method": methods[tab_index]}
                }).done(function(response){
                    most_shifted[methods[tab_index]] = {...response};
                    setTableRows("table-"+response["method"], {...response});
                });
        }
    });

    setTabs(metadata[value]["corpus_1"], metadata[value]["corpus_2"]);
    // Set sentence table names
    document.getElementById("ex-header-1").innerHTML = metadata[value]["corpus_1"];
    document.getElementById("ex-header-2").innerHTML = metadata[value]["corpus_2"];
    datasetSelected = value;
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


function queryWord(evt, target)
{

    setTargetLabel(target);

    // Clear table bodies
    var table_a = document.getElementById("table-a");
    var table_b = document.getElementById("table-b");
    clearTableBody(table_a);
    clearTableBody(table_b);

    var table_ex_a = document.getElementById("table-ex-a");
    var table_ex_b = document.getElementById("table-ex-b");
    clearTableBody(table_ex_a);
    clearTableBody(table_ex_b);

    $.ajax({
        method: "GET",
        url: "getWordContext",
        data: {"target": target}
    }).done(function(response){
        current_data = response;
        updateWordTable("table-a", response["neighbors_ab"]);
        updateWordTable("table-b", response["neighbors_ba"]);
        chart_a = drawScatterPlot("plot-a", response["x_ab"], [target].concat(response["neighbors_ab"]));
        chart_b = drawScatterPlot("plot-b", response["x_ba"], [target].concat(response["neighbors_ba"]), true);
        $("#k-range-a").trigger("input");
        $("#k-range-b").trigger("input");
    });

    // Query sentence examples
    $.ajax({
        method: "GET",
        url: "getSentenceExamples",
        data: {"target": target}
    }).done(function(response){
        updateSentenceTable("table-ex-a", response["sents_a"]);
        // updateSentenceTable("table-ex-b", response["sents_b"]);
        document.getElementById("target-word-sent").innerHTML = target;
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


$(document).ready(function(){
    $(".dataset-item")[0].click();
    $(".btn-next").click(nextTab);
    $(".btn-prev").click(previousTab);
});