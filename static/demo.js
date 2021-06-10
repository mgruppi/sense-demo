var metadata = {}; // Stores all metadata
var progress_complete = 0;  // Stores how much of the demo has progressed

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

function datasetClick(link, elem)
{
    $(".dataset-item").removeClass("bg-primary");
    $(".dataset-item").removeClass("text-white");
    $(".dataset-item").removeClass("active");
    $(".dataset-item .card").removeClass("bg-primary");

    link.getElementsByClassName("card")[0].classList.add("bg-primary");
    link.classList.add("text-white");
    link.classList.add("active");
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
        cell2.innerHTML = "<a class='word-item' onclick='queryWord(event,\""+data["words"][i]+"\");'>"+data['words'][i]+"</a>";
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


function updateWordTable(table_id, data)
{
    table = document.getElementById(table_id);
    tbody = table.getElementsByTagName("tbody")[0];

    for (i in data)
    {
        var row = tbody.insertRow(-1);  // Insert row at last position
        var cell1 = row.insertCell(0);  // Insert cells for Word, Distance
        // var cell2 = row.insertCell(1);
        cell1.innerHTML = "<a class='word-item'>"+data[i]+"</a>";
        // cell3.innerHTML = data["scores"][i];
    }
}


function setTargetLabel(target){
    document.getElementById("target-label").innerHTML = target;
}


function plotNeighbors(ctx_id, x, words)
{
    var ctx = document.getElementById(ctx_id).getContext("2d");

    var datasets = [];
    var dataset = {};
    dataset["pointRadius"] = 4;
    dataset["pointHoverRadius"] = 8;
    dataset["backgroundColor"] = "#2222FF";
    dataset["borderWidth"] = 2;
    dataset["data"] = [];
    dataset["labels"] = words;
    for (var i = 0; i < x.length; ++i)
    {

        dataset["data"].push({"x": x[i][0], "y": x[i][1], "label": words[i]});
    }
    datasets.push(dataset);

    var chart = new Chart(ctx,{
        type: "scatter",
        data: {
            datasets: datasets
        },
        options:
        {
            legend: false,
            plugins: {
                datalabels: {
                    anchor: function(ctx){
                        console.log(ctx);
                        return "end";
                    },
                    align: function(ctx){
                        return "eng";
                    },
                    color: function(ctx){
                        return "black";
                    },
                    font: {
                        weight: "bold"
                    },
                    formatter: function(value){
                        return value.label;
                    },
                    offset: 2,
                    padding: 0
                }
            }
        },
    });

    return chart;
}


function drawScatterPlot(target, x, labels)
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
    Plotly.newPlot(target, data, layout, chart_configs);
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
        updateWordTable("table-a", response["neighbors_ab"]);
        updateWordTable("table-b", response["neighbors_ba"]);
        drawScatterPlot("plot-a", response["x_ab"], [target].concat(response["neighbors_ab"]));
        drawScatterPlot("plot-b", response["x_ba"], [target].concat(response["neighbors_ba"]));
    });
}


$(document).ready(function(){
    $(".dataset-item")[0].click();


});