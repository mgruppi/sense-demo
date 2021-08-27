current_walkthrough_page = 0;
tutorial_on = false;


function make_popovers()
{
    //Create popovers to be triggered throughout the tour
    // Dataset item
    var ds_item = $(".dataset-item")[0];
    ds_item.setAttribute("data-bs-toggle", "popover");
    ds_item.setAttribute("title", "Step 1 ");
    ds_item.setAttribute("data-bs-content", "Let us begin by selecting a dataset to work with. We will use the English: Historical dataset, which compares documents in English from the 19th century to English of the 21st century.");
    ds_item.setAttribute("data-bs-trigger", "manual");
    ds_item.setAttribute("id", "wt-1");

    // Button next dataset
    var btn_next_ds = $("#btn-next-dataset")[0];
    btn_next_ds.setAttribute("data-bs-toggle", "popover");
    btn_next_ds.setAttribute("title", "Step 2");
    btn_next_ds.setAttribute("data-bs-content", "Click on <a class='btn btn-sm btn-primary unclickable'>Next</a> to continue.")
    btn_next_ds.setAttribute("data-bs-trigger", "manual");
    btn_next_ds.setAttribute("data-bs-html", "true");


    // Most shifted tables
    var tbl_most_shifted = $("#most-shifted-tables-content")[0];
    tbl_most_shifted.setAttribute("data-bs-toggle", "popover");
    tbl_most_shifted.setAttribute("data-bs-placement", "left");
    tbl_most_shifted.setAttribute("title", "Step 3");
    // tbl_most_shifted.setAttribute("data-bs-content", "These tables show the words ordered by the most semantically shifted for each alignment method. <button type='button' class='btn btn-small btn-primary'>Ok</button>");
    content_html = "<p>These tables show the words ordered by the most semantically shifted for each alignment method.</p>";
    content_html += "<a href='#' id='btn-popover-most-shifted' class='btn btn-sm btn-primary py-0'>Close</a>";
    $(document).on('click', "#btn-popover-most-shifted", filters_walkthrough);
    tbl_most_shifted.setAttribute("data-bs-content", content_html);
    tbl_most_shifted.setAttribute("data-bs-trigger", "manual");
    tbl_most_shifted.setAttribute("data-bs-html", "true");

    // Filter shifted tables
    var btn_group = $("#filter-btn-group")[0];
    btn_group.setAttribute("data-bs-toggle", "popover");
    btn_group.setAttribute("title", "Step 4");
    btn_group.setAttribute("data-bs-placement", "right");
    content_html = "<p>You can apply filters to highlight common or unique words discovered by each alignment method.</p>";
//    content_html += "<dl class='row'>";  // Using a description list <dl>
//    content_html += "<dt class='col-sm-3'><a class='btn btn-sm btn-outline-secondary highlight-common'>Common</a></dt>";
//    content_html += "<dd class='col-sm-9'>Def</dd>";
//    content_html += "<dt class='col-sm-3'><a class='btn btn-sm btn-outline-secondary highlight-unique'>Unique</a></dt>";
//    content_html += "<dd class='col-sm-9'>Def</dd>";
//    content_html += "</dl>";
    content_html += "<ul class='list-unstyled'><li class='mb-1'><a class='btn btn-sm btn-outline-secondary highlight-common unclickable'>Common</a> shows words that are discovered by all alignment methods.</li>";
    content_html += "<li class='mb-1'><a class='btn btn-sm btn-outline-secondary highlight-unique unclickable'>Unique</a> shows words uniquely discovered by each alignment method.</li></ul>"
    content_html += "<a href='#' id='btn-popover-filters' class='btn btn-sm btn-primary py-0'>Close</a>";
    btn_group.setAttribute("data-bs-content", content_html)
    btn_group.setAttribute("data-bs-trigger", "manual");
    btn_group.setAttribute("data-bs-html", "true");

    // Init BS popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
      return new bootstrap.Popover(popoverTriggerEl)
    });

}


function prompt_walkthrough()
{
    $("#tour-prompt-modal").modal("show");
}

function begin_walkthrough()
{
    tutorial_on = true;
    make_popovers();
    $("#tour-prompt-modal").modal("hide");
    document.getElementById("backdrop-div").classList.remove("d-none");

    // DATASET TAB
    // Show popovers
    $("#wt-1").popover("show");
    // Use z-index to ensure backdrop stays behind the relevant elements in each step
    document.getElementById("wt-1").style.zIndex = 2;
    document.getElementById("wt-1").getElementsByClassName("card")[0].style.zIndex=2;

    document.getElementById("wt-1").onclick = function(){
        datasetClick(this, 'hist-english');
        if (tutorial_on){
            $("#wt-1").popover("hide");
            $("#btn-next-dataset").popover("show");
            $("#btn-next-dataset").css("position", "relative").css("z-index", 2);
        }
    };
}


function shifted_walkthrough()
{
    $("#btn-next-dataset").popover("hide");
    $(".word-item").addClass("unclickable");
    $("#most-shifted-tables-content").popover("show");
    $("#most-shifted-tables-content").css("position", "relative").css("z-index", 2);
}

function filters_walkthrough()
{
    $("#most-shifted-tables-content").popover("hide");
    $("#filter-btn-group").popover("show");
    $("#filter-btn-group").css("z-index", 2);
    $(document).on("click", "#btn-popover-filters", word_walkthrough);
}


function word_walkthrough()
{
    // Filter shifted tables

    $("#filter-btn-group").popover("hide");

    $(".word-item").removeClass("unclickable");

    var word_item = $(".word-item")[0];
    word_item.setAttribute("data-bs-toggle", "popover");
    word_item.setAttribute("title", "Step 5");
    word_item.setAttribute("data-bs-placement", "left");
    content_html = "<p>You can click on a word to explore the semantic differences across both input corpora.</p>";
    content_html = "<p>Click on the word <b>" + word_item.innerHTML + "</b> to inspect it.";
    word_item.setAttribute("data-bs-content", content_html)
    word_item.setAttribute("data-bs-trigger", "manual");
    word_item.setAttribute("data-bs-html", "true");

    word_item.onclick = function()
    {
        queryWord(this, word_item.innerHTML);
        nextTab();
        closest_walkthrough();
    }

    $(".word-item").popover("show");
}


function closest_walkthrough()
{
    $(".word-item").popover("hide");
    $("#query-panel").css("z-index", 2);
    $("#btn-next-closest").css("position", "relative").css("z-index", 2);

    var q_content = $("#query-content")[0];
    q_content.setAttribute("data-bs-toggle", "popover");
    q_content.setAttribute("title", "Step 6");
    q_content.setAttribute("data-bs-placement", "left");
    content_html = "<p>This page shows the nearest neighbors of the target word you previously selected.</p>";
    content_html += "<p>You can see the list of words as well as a 2d projection of such words in the <b>View</b> panel.";
    content_html += "<p>You can use the tabs on top to change the order of the mapping between corpora.";
    content_html += "<p>Once you are done, click <a class='btn btn-sm btn-primary unclickable'>Next</a> to continue.</p>";
    content_html += "<a href='#' id='btn-popover-closest' class='btn btn-sm btn-primary py-0'>Close</a>";

    q_content.setAttribute("data-bs-content", content_html);
    q_content.setAttribute("data-bs-trigger", "manual");
    q_content.setAttribute("data-bs-html", "true");

    $(document).on("click", "#btn-popover-closest", function(){
        $("#query-content").popover("hide");
    });

    $("#btn-next-closest").click(function(){
        $("#query-content").popover("hide");
        if(tutorial_on){
            examples_walkthrough();
        }
    });

    $("#query-content").popover("show");
}


function examples_walkthrough()
{
    $("#example-rows").css("position", "relative").css("z-index", 2);
    var ex_content = $("#example-rows")[0];
    var tgt_word = document.getElementById("target-word-sent").innerHTML;
    ex_content.setAttribute("data-bs-toggle", "popover");
    ex_content.setAttribute("title", "Step 7");
    ex_content.setAttribute("data-bs-placement", "left");
    content_html = "<p>This pages shows examples of the selected target word ("+ tgt_word +") used in sentences on the first corpus (19th century English) and examples of sentences on the second corpus (21st century English).</p>";
    content_html += "<a href='#' id='btn-popover-examples' class='btn btn-sm btn-primary py-0'>Close</a>";
    ex_content.setAttribute("data-bs-content", content_html);
    ex_content.setAttribute("data-bs-trigger", "manual");
    ex_content.setAttribute("data-bs-html", "true");

    $("#example-rows").popover("show");
    $(document).on('click', "#btn-popover-examples", example_source_walkthrough);
}

function example_source_walkthrough()
{
    $("#example-rows").popover("hide");
    var tgt_word = document.getElementById("target-word-sent").innerHTML;
    var src_content = $("#sent-src")[0];
    src_content.setAttribute("data-bs-toggle", "popover");
    src_content.setAttribute("title", "Step 8");
    src_content.setAttribute("data-bs-placement", "top");
    content_html = "<p>This is an example of the word " + tgt_word + " in a sentence from the 19th century English corpus.</p>";
    content_html += "<a href='#' id='btn-popover-examples-src' class='btn btn-sm btn-primary py-0'>Close</a>";
    src_content.setAttribute("data-bs-content", content_html);
    src_content.setAttribute("data-bs-trigger", "manual");
    src_content.setAttribute("data-bs-html", "true");

    $("#sent-src").popover("show");
    $(document).on('click', "#btn-popover-examples-src", example_target_walkthrough);
}


function example_target_walkthrough()
{
    $("#sent-src").popover("hide");
    var tgt_content = $("#sent-tgt")[0];
    var tgt_word = document.getElementById("target-word-sent").innerHTML;
    tgt_content.setAttribute("data-bs-toggle", "popover");
    tgt_content.setAttribute("title", "Step 9");
    tgt_content.setAttribute("data-bs-placement", "top");
    content_html = "<p>These are examples of the word " + tgt_word + " in sentences from the 21st century English corpus.</p>";
    content_html += "<a href='#' id='btn-popover-examples-tgt' class='btn btn-sm btn-primary py-0'>Close</a>";
    tgt_content.setAttribute("data-bs-content", content_html);
    tgt_content.setAttribute("data-bs-trigger", "manual");
    tgt_content.setAttribute("data-bs-html", "true");

    $("#sent-tgt").popover("show");
    $(document).on('click', "#btn-popover-examples-tgt", conclude_walkthrough);
}


function conclude_walkthrough()
{
    $("#conclude-modal").modal("show");
    $("#sent-tgt").popover("hide");
    $("#backdrop-div").addClass("d-none");
    tutorial_on = false;
}


function restart_walkthrough()
{
    $("#conclude-modal").modal("hide");
    openTab(this, "content-2");
}