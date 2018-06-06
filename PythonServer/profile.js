
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

function loadChat() {
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
	if (this.readyState == 4 && this.status == 200) {
		var obj = JSON.parse(this.response)
		var obj2 = JSON.parse(obj)
		document.getElementById("chat").innerHTML = obj2.data;
		}
	};
	var param = document.getElementById('destination_chat').value;
	xhttp.open("GET", "updateChat?destination=" + param, true);
	xhttp.timeout = 2000;
	xhttp.send(); 
}

function loadStatus() {
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
	if (this.readyState == 4 && this.status == 200) {
		var obj = JSON.parse(this.response)
		var obj2 = JSON.parse(obj)
		document.getElementById("status").innerHTML = obj2.data;
		}
	};
	var param = document.getElementById('destination_chat').value;
	xhttp.open("GET", "updateStatus?destination=" + param, true);
	xhttp.timeout = 2000;
	xhttp.send(); 
}

var uploadField = document.getElementById("file");
uploadField.onchange = function() {
    if(this.files[0].size > 5242880){
       alert("File is too big!");
       this.value = "";
    };
};

document.getElementById("filebutton").disabled = true;
var uploadField = document.getElementById("file");
uploadField.onchange = function() {
	document.getElementById("filebutton").disabled = false;
    document.getElementById("filebutton").style.cursor = "pointer";
	document.getElementById("filebutton").style.opacity = "1";
};

loadStatus()
loadChat()
loadOnline()

var myVar2 = setInterval(loadStatus, 2000);

var myVar2 = setInterval(loadChat, 2000);

var myVar = setInterval(loadOnline, 8000);
  