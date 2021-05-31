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

function updateWordTable(data)
{
    console.log(data);
}

function setDatasetLabel(label){
    var element = document.getElementById("selected-dataset-label");

    // Define the human-readable name of each dataset.
    // TODO: Make it persistent or sent from backend. I.e., server gives list of available datasets.
    labels = {
        "ukus": "English - UK vs. US",
        "hist-eng": "English - Historical",
        "arxiv-ai-phys": "ArXiv - cs.AI vs. phys.class-phys"
    }
    if (label in labels)
    {
        element.innerHTML = labels[label];
        element.classList.add("text-white");
    }
    else{
        element.innerHTML = label;
        element.classList.add("text-white");
    }
}

function loadDataset(evt)
{
    // Requests a dataset from the server side.
    // TODO: add a spinner when loading dataset.
    data = document.getElementById("select-dataset");
    value = data.value;

    $.ajax({
        method: "GET",
        url: "loadDataset",
        data: {"data": value}
    }).done(function(msg){
        // Once data is loaded, set the dataset label
        setDatasetLabel(value);

        // Then, get most shifted words
        $.ajax({
        method: "GET",
        url: "getMostShiftedWords",
        data: {"method": "global"}
            }).done(function(msg){
                console.log("words", msg);
            });
    });
}
