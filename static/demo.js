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

function progressUp(amount=20)
{
    progress_complete = Math.min(100, progress_complete+amount);
    document.getElementById("progress-bar").style.width = progress_complete.toString()+"%";
}


function updateWordTable(table_id, data)
{
    table = document.getElementById(table_id);
    tbody = table.getElementsByTagName("tbody")[0];
    console.log(data);

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


function queryWord(evt, target)
{
    setTargetLabel(target);
    $.ajax({
        method: "GET",
        url: "getWordContext",
        data: {"target": target}
    }).done(function(response){
//        console.log(response);
        var table_a = document.getElementById("table-a");
        clearTableBody(table_a);
        var table_b = document.getElementById("table-b");
        clearTableBody(table_b);
        updateWordTable("table-a", response["neighbors_ab"]);
        updateWordTable("table-b", response["neighbors_ba"]);
    });
}


$(document).ready(function(){
    $(".dataset-item")[0].click();
});