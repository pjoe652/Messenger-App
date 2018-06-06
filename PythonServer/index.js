
function loadOnline() {
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
	if (this.readyState == 4 && this.status == 200) {
		var obj = JSON.parse(this.response)
		var obj2 = JSON.parse(obj)
		document.getElementById("demo").innerHTML = obj2.data;
		}
	};
	xhttp.open("GET", "storeUsers", true);
	xhttp.timeout = 8000;
	xhttp.send(null); 
}

loadOnline()

var myVar = setInterval(loadOnline, 8000);

