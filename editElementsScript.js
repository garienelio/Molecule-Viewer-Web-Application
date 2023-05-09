$(document).ready(
    function(){
        let mode = '1';
        $(".removingElement").hide();

        $("#b1").click(
            function(){
                $(".addingElement").toggle();
                $(".removingElement").toggle();

                if(mode == '1'){
                    $("#b1").html("Change to Add Mode");
                    mode = '2';
                } else{
                    $("#b1").html("Change to Remove Mode");
                    mode = '1';
                }
            });

        $("#addForm").submit(
            function(event){
                event.preventDefault();

                $.post("/add.html", 
                {
                    eNumber: $("#elementNumber").val(),
                    eCode: $("#elementCode").val(),
                    eName: $("#elementName").val(),
                    eColor1: $("#elementColor1").val(),
                    eColor2: $("#elementColor2").val(),
                    eColor3: $("#elementColor3").val(),
                    eRadius: $("#elementRadius").val()
                }, 
                function(data){
                    alert("Status: " + data);
                    $("#elementNumber").val('');
                    $("#elementCode").val('');
                    $("#elementName").val('');
                    $("#elementColor1").val('');
                    $("#elementColor2").val('');
                    $("#elementColor3").val('');
                    $("#elementRadius").val('');
                    location.reload();
                });
            });
        
        $("#removeForm").submit(
            function(event){
                event.preventDefault();

                $.ajax({
                    url: "/remove.html", 
                    type: "POST", 
                    data: {
                        element: $("#elementToRemove").val()
                    }, 
                    success: function(data){
                        alert("Status: " + data);
                        $('#elementToRemove option[value="' + $.escapeSelector($("#elementToRemove").val()) + '"]').remove();
                    }, 
                    error: function(){
                        alert("Failed to delete the element.");
                    }
                });
            });
    });