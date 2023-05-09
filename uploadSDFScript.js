$(document).ready(
    function(){
        $("#uploadFile").submit(
            function(event){
                event.preventDefault();

                $("#submitUploadButton").prop("disabled", true);
                $("#submitUploadButton").text("Uploading...");


                var formD = new FormData();
                formD.append('theName', $("#molName").val());
                formD.append('theFile', $('#userFile')[0].files[0]);

                $.ajax({
                    url: "/uploadSDFFile.html", 
                    type: "POST", 
                    data: formD, 
                    processData: false, 
                    contentType: false, 
                    success: function(data){
                        $("#submitUploadButton").text("Upload File");
                        alert("Status: " + data);
                        $("#molName").val('');
                        $("#userFile").val('');
                        $("#submitUploadButton").prop("disabled", false);
                    },
                    error: function(){
                        $("#submitUploadButton").text("Upload File");
                        alert("Failed to upload SDF File.");
                        $("#submitUploadButton").prop("disabled", false);
                    }
                });
            });
    });