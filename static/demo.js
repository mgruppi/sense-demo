function openTab(evt, target)
{
    var i, x, tablinks;
    x = document.getElementsByClassName("content-page");
    for (i=0; i < x.length; ++i)
    {
        x[i].style.display = "none";
        // Set inactive
    }
    document.getElementById(target).style.display = "block";
    // Set evt target as active and other inactive.
}