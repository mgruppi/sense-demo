current_walkthrough_page = 0;


function make_popovers()
{
    // Dataset item
    var ds_item = $(".dataset-item")[0];
    ds_item.setAttribute("data-bs-toggle", "popover");
    ds_item.setAttribute("title", "Step 1 ");
    ds_item.setAttribute("data-bs-content", "Explanation");
    ds_item.setAttribute("id", "wt-1");

    // Button next dataset
    var btn_next_ds = $("#btn-next-dataset")[0];
    btn_next_ds.setAttribute("data-bs-toggle", "popover");
    btn_next_ds.setAttribute("title", "Step 2");
    btn_next_ds.setAttribute("data-bs-content", "Click here to continue.")

    // Most shifted tables
    var tbl_most_shifted = $(".most-shifted-tables")[0];
    tbl_most_shifted.setAttribute("data-bs-toggle", "popover");
    tbl_most_shifted.setAttribute("data-bs-placement", "top");
    tbl_most_shifted.setAttribute("title", "Step 3");
    tbl_most_shifted.setAttribute("data-bs-content", "These tables show the words ordered by the most semantically shifted for each alignmend method.");

    // Init BS popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
      return new bootstrap.Popover(popoverTriggerEl)
    });

}

function begin_walkthrough()
{
    make_popovers();

    openTab("none", "content-2");
    $("#wt-1").popover("show");
    $("#btn-next-dataset").popover("show");
    // $(".most-shifted-tables").popover("show");
}