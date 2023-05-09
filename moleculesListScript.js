$(document).ready(
    function(){
        $(".displayContainer").hide();

        $("#displayButton").click(
            function(event){
                event.preventDefault();

                $("#degSlider").val(0);
                $("#degreeValue").html("Degree: 0");


                $.ajax({
                    url: "/displayMolecule.html", 
                    type: "POST", 
                    data: {
                        molSelected: $("#moleculeList").val()
                    }, 
                    success: function(data){
                        $("#moleculeDisplayed").html("Currently Displayed: " + $("#moleculeList").val() + "Molecule");
                        $("#moleculeContainer").html(data);
                        $(".displayContainer").show();
                        $("html, body").animate({scrollTop: $(document).height()}, 800);
                    }, 
                    error: function(){
                        alert("Cannot display the molecule.");
                    }
                });
            });

        $("#axisList").change(
            function(){
                $("#degSlider").val(0);
                $("#degreeValue").html("Degree: 0");
            });
        
         
        $("#degSlider").on("input", 
        function(event){
            event.preventDefault();

            $("#degreeValue").html("Degree: " + $(this).val());
            $("#moleculeDisplayed").html("Currently Displayed: " + $("#moleculeList").val() + "Molecule");

            $.ajax({
                url: "/rotateMolecule.html", 
                type: "POST", 
                data: {
                    theMolecule: $("#moleculeList").val(),
                    theAxis: $("#axisList").val(), 
                    theDegree: $(this).val()
                }, 
                success: function(data){
                    $("#moleculeContainer").html(data);
                }
            });
        });
    });