console.log("loaded script ");

function displayWordData(x){
    var text = $("#a-" + x).text()
    if (text == "Show Word Details"){
        $("#a-" + x).text("Hide Word Details");
    } else
    {
        $("#a-" + x).text("Show Word Details");
    }
    $( "#" + x ).slideToggle( "slow" );

}  

