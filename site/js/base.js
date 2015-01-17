// jquery ready

$(document).ready(function(){
    // dynamically resize textarea
    $('textarea').autosize();
});


// confirm exit
var confirmExit = false;
function confirm_leaving(evt) {
 if ( confirmExit ) return "Your changes are not saved!";
}
// Catch before unloading the page
window.onbeforeunload = confirm_leaving


// search box

searchIsDisabled = false;

function searchChange(e) {
// Update search buttons status according to search box content.
// Ignore empty or whitespace search term.
var value = e.value.replace(/\s+/, '');
if (value == '' || searchIsDisabled) {searchSetDisabled(true); }  else { searchSetDisabled(false); }
}

function searchSetDisabled(flag) {
// Enable or disable search
document.getElementById('gobutton').disabled = flag;
}

