
function handle_dataset_select(target)
{

}

function request_analysis()
{
    var target_a = document.getElementById("select-first").value;
    var target_b = document.getElementById("select-second").value;
    var normalize = document.getElementById("normalizeVectors").checked;
    $.ajax({
        method: "GET",
        url: "runAnalysis",
        data: {"target_a": target_a, "target_b": target_b,
                "normalize": normalize}
    }).done(function(response)
    {
        console.log(response);
    })
}


$(document).ready(function(){
      $(".dataset-select").on("change",
      function(evt){
        handle_dataset_select(evt.target);
      });
});