/*
function press(id){ 
document.getElementById(id).className = "pressed" 
} 

function release(id){ 
document.getElementById(id).className = "released"
} 

function toggle(what) {
ob=document.getElementById(what)
if (ob.value=="Y") {
  ob.value=""
  release(what+'B')
  } 
else {
  ob.value="Y"
  press(what+'B')
  }
}

function select(what,option) {
ob=document.getElementById(what)
release(what+ob.value)
ob.value=option
press(what+option)
}

function enable(id,set) {
ob=document.getElementById(id)
if (set==1) {
  if (ob.className=='disreleased') {ob.className="released"}
  if (ob.className=='dispressed') {ob.className="pressed"}
  ob.disabled=0
  }
else  {
  if (ob.className=='released') {ob.className="disreleased"}
  if (ob.className=='pressed') {ob.className="dispressed"}
  ob.disabled=1 
  ob.style.visibility='visible';
  }  
}


function show(showID,set) {
ob=document.getElementById(showID)
if (set==1) {
  ob.disabled=0
  ob.style.visibility='visible';
  ob.focus(); 
  }
else  {
  ob.disabled=1;    
  ob.style.visibility='hidden';
  }  
}

function combo(selection,textID) {
show(textID,selection.selectedIndex==selection.length-1) 
}
*/

/* work around for nav list in IE */
/*
function startList() {
	if (document.all&&document.getElementById) {
		navRoot = document.getElementById("navpanel");
		for (i=0; i<navRoot.childNodes.length; i++) {
			node = navRoot.childNodes[i];
			if (node.nodeName=="LI") {
				node.onmouseover=function() {
					this.className+=" over";
				}
				node.onmouseout=function() {
					this.className=this.className.replace(" over", "");
				}
			}
		}
	}
}
*/

/* --------- additions for pages --------- */
/*
function sizePage() {
//for page height - works on IE even!
element=document.getElementById('main');
element.style.height=(getWindowHeight()-12)+"px";
//window.alert("page="+getWindowHeight()+"height="+element.style.height);
}

function sizeText() {
element=document.getElementById('text');
element.style.height=(getWindowHeight()-82)+"px";
sizePage();
//element.style.height=(document.getElementById('page').clientHeight-document.getElementById('header').clientHeight-42)+"px";
//width=(document.getElementById('page').clientWidth-24);
//element.style.width="100px";
//element.style.width=width+"px";
//document.getElementById('texttitle').style.width=(width-80)+"px";
//repeating this will fix glitches on Firefox, but not IE6
//width=(document.getElementById('page').clientWidth-24);
//element.style.width=width+"px";
//window.alert("width="+width+" shouldbe="+(document.getElementById('page').clientWidth-24))
//window.alert("width="+element.style.width+" titlewidth="+document.getElementById('texttitle').style.width)
//window.alert("height="+element.style.height);
}
*/

function sizeArea(t) {
//dynamically resizing textarea
a=t.value.split('\n');
b=1;
for (x=0;x < a.length; x++) {
 if (a[x].length >= t.cols) b+= Math.floor(a[x].length/t.cols);
 }
 b+= a.length;
 if (b > t.rows) t.rows = b;
}


// We keep here the state of the search box
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

function searchFocus(e) {
// Update search input content on focus
if (e.value == 'search') {
  e.value = '';
  e.className = '';
  searchIsDisabled = false;
  }
}

function searchBlur(e) {
 // Update search input content on blur
if (e.value == '') {
  e.value = 'search';
  e.className = 'disabled';
  searchIsDisabled = true;
  }
}

// warn of unsaved pages

var confirmExit = false;
function confirm_leaving(evt) {
 if ( confirmExit ) return "Your changes are not saved!";
}
// Catch before unloading the page
window.onbeforeunload = confirm_leaving
	