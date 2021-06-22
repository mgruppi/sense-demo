var metadata = {}; // Stores all metadata
var progress_complete = 0;  // Stores how much of the demo has progressed
var currentData = 0; // Stores current data from server-side
var chart_a, chart_b = 0; // Stores chart objects

function openTab(evt, target)
{
    var i, x;
    var tgt_id = target.split("-")[1]-1;
    x = document.getElementsByClassName("content-page");
    for (i=0; i < x.length; ++i)
    {
        x[i].style.display = "none";
    }

    var tabs = document.getElementsByClassName("nav-link");
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
    var tabs = document.getElementsByClassName("nav-link");
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
        cell1.innerHTML = i;
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

function clearDataset()
{
    // Clears currently selected dataset (if any).
    var tables = $(".table-shifted-words");
    for (var i = 0; i < tables.length; ++i)
    {
        clearTableBody(tables[i]);
    }
}


function setTabs(name_a, name_b){
    document.getElementById("tab-a").innerHTML = name_a;
    document.getElementById("tab-b").innerHTML = name_b;
}


function loadDataset(evt)
{
    // Requests a dataset from the server side.
    clearDataset();
    // TODO: add a spinner when loading dataset.
    var value = $(".dataset-item.active")[0].getAttribute("value");

    var word_data = {"global": {}, "noise-aware": {}, "s4": {}};

    var methods = ["global", "noise-aware", "s4"];

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
                    word_data[methods[tab_index]] = response;
                    setTableRows("table-"+response["method"], response);
                });
        }
    });

    setTabs(metadata[value]["corpus_1"], metadata[value]["corpus_2"]);
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


function drawScatterPlot(target, x, labels, react=false)
{
    var x_target = {
        x: [x[0][0]],
        y: [x[0][1]],
        mode: "markers+text",
        type: "scatter",
        name: "Target",
        text: labels[0],
        textposition: "top right",
        textfont: {
            family: "Raleway, sans-serif"
        },
        marker: {
            size: 12,
            color: "#00f",
            symbol: "square"
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
        name: "Source",
        text: _labels,
        textposition: "top center",
        textfont: {
            family: "Raleway, sans-serif"
        },
        marker: {
            size : 12,
            color: "#f00",
        },
        hoverinfo: "text+name"
    };

    var data = [x_target, x_data];
    var layout = {
        "showlegend": false,
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
    }
    drawScatterPlot(plot_div, x.slice(0, element.value), [target].concat(n.slice(0, element.value)));
}


function queryWord(evt, target)
{
    setTargetLabel(target);
    $.ajax({
        method: "GET",
        url: "getWordContext",
        data: {"target": target}
    }).done(function(response){
        var table_a = document.getElementById("table-a");
        clearTableBody(table_a);
        var table_b = document.getElementById("table-b");
        clearTableBody(table_b);
        current_data = response;
        updateWordTable("table-a", response["neighbors_ab"]);
        updateWordTable("table-b", response["neighbors_ba"]);
        chart_a = drawScatterPlot("plot-a", response["x_ab"], [target].concat(response["neighbors_ab"]));
        chart_b = drawScatterPlot("plot-b", response["x_ba"], [target].concat(response["neighbors_ba"]));

        $("#k-range-a").trigger("input");
        $("#k-range-b").trigger("input");
    });
}


$(document).ready(function(){
    $(".dataset-item")[0].click();
    $(".btn-next").click(nextTab);
    $(".btn-prev").click(previousTab);
    $("#tab-a").click();

});