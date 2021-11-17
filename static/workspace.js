
function handle_dataset_select(target)
{

}

function request_analysis()
{
    var target_a = document.getElementById("select-first").value;
    var target_b = document.getElementById("select-second").value;
    $.ajax({
        method: "GET",
        url: "runAnalysis",
        data: {"target_a": target_a, "target_b": target_b}
    }).done(function(response)
    {
        console.log(response["words"]);
    })
}


$(document).ready(function(){
      $(".dataset-select").on("change",
      function(evt){
        handle_dataset_select(evt.target);
      });
});