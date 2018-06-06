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

document.getElementById("profile").disabled = true;

var uploadField = document.getElementById("file");

uploadField.onchange = function() {
	document.getElementById("profile").disabled = false;
    document.getElementById("profile").style.cursor = "pointer";
	document.getElementById("profile").style.opacity = "1";
};

var uploadField = document.getElementById("file");
uploadField.onchange = function() {
    if(this.files[0].size > 5242880){
       alert("File is too big!");
       this.value = "";
    };
};


loadOnline()

var myVar = setInterval(loadOnline, 8000);
  