(function () {

    function refreshPage(){
            window.location.reload();
        };

    let Submit = document.getElementById("Submit");

    Submit.addEventListener("click", function() {
        let image_url = document.getElementById("image_url").value;

        let jsonData = JSON.stringify({"image_url": image_url});

        let xhttp = new XMLHttpRequest();

        xhttp.onload = function() {
            if (this.readyState === 4) {
                if(this.status === 200) {
                    console.log(xhttp.responseText)
                } else {
                    console.log("Ops, error...");
                }
            }

            refreshPage();
        };

        xhttp.open("POST", "/upload", true);
        xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xhttp.send(jsonData);


    });

}())

