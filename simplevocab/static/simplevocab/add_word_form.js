$(document).ready(function() {
    
    generateDropDownOptions();
    $("#id_discovery_context").keyup(generateDropDownOptions);

    var message_value = document.getElementById("wordlist").options[0].text;
    $( "select" )
        .on( "change", function() {
            var str = "";
            $( "select option:selected" ).each(function() {
            str += $( this ).text();
            } );
            if (str != message_value){
                $( "#id_word" ).val( str );
            }
        } )
        .trigger( "change" );

    function generateDropDownOptions(){
        var discovery_context_input = document.getElementById("id_discovery_context").value;
        var word_array_input = discovery_context_input.split(/[^a-z]/i);
        let word_array_input_index=0;
        var message_value = document.getElementById("wordlist").options[0].text;
        $(wordlist).empty();
        $(wordlist).append('<option value="" disabled selected>' + message_value + '</option>')
        var final_array = []
        while(word_array_input_index < word_array_input.length){
            var word = word_array_input[word_array_input_index].replace(/[^A-Za-z]/g, '').toLowerCase();
            if(word != "" && word.length > 2 && final_array.indexOf(word) === -1){
                final_array.push(word)
            }
            word_array_input_index++;
        }
        
        final_array.sort()
        let final_array_input_index=0
        while(final_array_input_index < final_array.length){
            $('#wordlist').append('<option>' + final_array[final_array_input_index] + '</option>');
            final_array_input_index++;
        }
    }
});