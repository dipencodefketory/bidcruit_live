$(function() {
    $("input[name='eachall']").click(function() {
        if ($("#eachques").is(":checked")) {
            $(".maksbox").hide();
            $("input[name=marks_of_basic_questions]").prop('required', false);
            $("input[name=marks_of_intermediate_questions]").prop('required', false);
            $("input[name=marks_of_advanced_questions]").prop('required', false);
            $("input[name=marks_of_basic_questions]").val('');
            $("input[name=marks_of_intermediate_questions]").val('');
            $("input[name=marks_of_advanced_questions]").val('');
        } else {
            $(".maksbox").show();
            $("input[name=marks_of_basic_questions]").prop('required', true);
            $("input[name=marks_of_intermediate_questions]").prop('required', true);
            $("input[name=marks_of_advanced_questions]").prop('required', true);
        }
    });
});
$(function() {
    $("input[name='question-wise-time']").click(function() {
        if($(this).is(':checked')){
           
            // $(".total-time").css('disabled', true);
            $("#total-time").attr('disabled','disabled');
            $("#total-time").val('');
        } else {
            // $(".total-time").css('disabled', false);
            $("#total-time").removeAttr('disabled');
        }
    });
});
$(function() {
    $("input[name='nagative-mark']").click(function() {
        if($(this).is(':checked')){

            $(".nagative-mark-add").removeAttr("readonly");
        } else {
            $(".nagative-mark-add").prop('readonly', true);
        }
    });
});

$(function() {
    $("input[name='examtype']").click(function() {
        if ($("#random").is(":checked")) {
            $(".question-wise").hide();
            $(".total-time").prop('disabled', false);

            $(".quescat").hide();
            $(".maksbox").show();

        } else {
            $(".quescat").show();
            $(".question-wise").show();
            if ($("#eachques").is(":checked")) {

                $(".maksbox").hide();
            } else {
                $(".maksbox").show();
            }
        }
    });
});

$('#advance-que').change(function() {
    var basic=$('#basic-que').val();
    var intermediate=$('#intermediate-que').val();
    var advance=$('#advance-que').val();
    var total=$('#total-que').val();
    var sum=parseInt(basic)+parseInt(intermediate)+parseInt(advance)
    console.log(sum)
    if(parseInt(total)!==sum){
        alert('please add total number of qustion')
         var advance=$('#advance-que').val('');
    }
})

//
//$('#advance-que').change(function() {
//    var basic=$('#basic-que').val();
//    var intermediate=$('#intermediate-que').val();
//    var advance=$('#advance-que').val();
//    var total=$('#total-que').val();
//    var sum=parseInt(basic)+parseInt(intermediate)+parseInt(advance)
//    console.log(sum)
//    if(parseInt(total)!==sum){
//        alert('please add total number of qustion')
//         var advance=$('#advance-que').val('');
//    }
//})

$('#advance-que').change(function() {
    var basic=$('#basic-que').val();
    var intermediate=$('#intermediate-que').val();
    var advance=$('#advance-que').val();
     var subject_id=$('#subject').val();

     var total_question_count = parseInt(basic) + parseInt(intermediate) + parseInt(advance)
     // var flag = true;
     if(typeof(total_question_count) != 'number'  || subject_id == "")
     {
         return false;
     }
     $.ajax({
             url:"/company/get_advance_count/",
                    headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
                    type:'POST',
                    contentType: 'application/json; charset=UTF-8',
                    data: JSON.stringify({'subject_id':subject_id}),
                    error: function (request, status, error) {
                          alert(error);
                    }
                }).done(function(response){
                response=JSON.parse(response)
                    if(response['status'] == true){
                        if(parseInt(advance) <= parseInt(response['advance_count'])){
                            check_queno_type(basic,intermediate,advance);
                        }
                        else{
                            alert("there are only  "+ response['advance_count'] + "question/questions in the advance category of mcq question bank")
                            $('#advance-que').val('');
                        }
                    }else{
                        swal("Error!", "Something Wrong !!", "error");
                    }
                });
})

$('#intermediate-que').change(function() {
    var basic=$('#basic-que').val();
    var intermediate=$('#intermediate-que').val();
    var advance=$('#advance-que').val();
     var subject_id=$('#subject').val();

     var total_question_count = parseInt(basic) + parseInt(intermediate) + parseInt(advance)
     // var flag = true;
     if(typeof(total_question_count) != 'number'  || subject_id == "")
     {
         return false;
     }

    $.ajax({
             url:"/company/get_intermediate_count/",
                    headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
                    type:'POST',
                    contentType: 'application/json; charset=UTF-8',
                    data: JSON.stringify({'subject_id':subject_id}),
                    error: function (request, status, error) {
                          alert(error);
                    }
                }).done(function(response){
                response=JSON.parse(response)
                    if(response['status'] == true){
                        if(parseInt(intermediate) <= parseInt(response['intermediate_count'])){
                            check_queno_type(basic,intermediate,advance);
                        }
                        else{
                            alert("there are only  "+ response['intermediate_count'] + "question/questions in the intermediate category of mcq question bank")
                            $('#intermediate-que').val('');
                        }
                    }else{
                        swal("Error!", "Something Wrong !!", "error");
                    }
                });

})

$('#basic-que').change(function() {
    var basic=$('#basic-que').val();
    var intermediate=$('#intermediate-que').val();
    var advance=$('#advance-que').val();
    var subject_id=$('#subject').val();

    var total_question_count = parseInt(basic) + parseInt(intermediate) + parseInt(advance)
     // var flag = true;
     if(typeof(total_question_count) != 'number'  || subject_id == "")
     {
         return false;
     }

    $.ajax({
             url:"/company/get_basic_count/",
                    headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
                    type:'POST',
                    contentType: 'application/json; charset=UTF-8',
                    data: JSON.stringify({'subject_id':subject_id}),
                    error: function (request, status, error) {
                          alert(error);
                    }
                }).done(function(response){
                response=JSON.parse(response)
                    if(response['status'] == true){
                        if(parseInt(basic) <= parseInt(response['basic_count'])){
                            check_queno_type(basic,intermediate,advance);
                        }
                        else{
                            alert("there are only  "+ response['basic_count'] + "question/questions in the basic category of mcq question bank")
                            $('#basic-que').val('');
                        }
                    }else{
                        swal("Error!", "Something Wrong !!", "error");
                    }
                });


})

function check_queno_type(basic,intermediate,advandce)
{
    var basic_que=0;
    var intermediate_que=0;
    var advandce_que=0;

    if(basic!==''){
        basic_que=basic;
    }
    if(intermediate!==''){
        intermediate_que=intermediate;
    }
    if(advandce!==''){
        advandce_que=advandce;
    }
    var total=$('#total-que').val();
    var sum=parseInt(basic_que)+parseInt(intermediate_que)+parseInt(advandce_que);
    if(parseInt(total)<sum){
        alert('please add total number of qustion')
        $('#basic-que').val('');
        $('#intermediate-que').val('');
        $('#advandce-que').val('');
    }
}
 

$('.mark').change(function() {
    var basic=0;
    var basic_mark=0;
    var intermediate=0;
    var advance=0;
    var intermediate_mark=0;
    var advance_mark=0;
    if ($('#basic-que').val()==''){
        basic=0;
        basic_mark=0;
    }
    else{
        basic=parseInt($('#basic-que').val());
        if($('#basic-mark').val()==''){
            basic_mark=0;
        }
        else{
            basic_mark=$('#basic-mark').val();
        }
    }

    if ($('#intermediate-que').val()==''){
        intermediate=0;
        intermediate_mark=0;
    }
    else{
        intermediate=parseInt($('#intermediate-que').val());
        if($('#intermediate-mark').val()==''){
            intermediate_mark=0;
        }
        else{
            intermediate_mark=$('#intermediate-mark').val();
        }
    }

    if ($('#advance-que').val()==''){
        advance=0;
        advance_mark=0;
    }
    else{
        advance=parseInt($('#advance-que').val());
        if($('#advance-mark').val()==''){
            advance_mark=0;
        }
        else{
            advance_mark=$('#advance-mark').val();
        }
    }
    
    console.log($('#intermediate-que').val())
    console.log(intermediate_mark)
    var total_mark=(parseInt(basic)*parseInt(basic_mark))+(parseInt(intermediate)*parseInt(intermediate_mark))+(parseInt(advance)*parseInt(advance_mark));
    $('#total_exam_mark').val(total_mark);
})


$('.que').change(function() {
    var basic=0;
    var basic_mark=0;
    var intermediate=0;
    var advance=0;
    var intermediate_mark=0;
    var advance_mark=0;
    if ($('#basic-que').val()==''){
        basic=0;
        basic_mark=0;
    }
    else{
        basic=parseInt($('#basic-que').val());
        if($('#basic-mark').val()==''){
            basic_mark=0;
        }
        else{
            basic_mark=$('#basic-mark').val();
        }
    }

    if ($('#intermediate-que').val()==''){
        intermediate=0;
        intermediate_mark=0;
    }
    else{
        intermediate=parseInt($('#intermediate-que').val());
        if($('#intermediate-mark').val()==''){
            intermediate_mark=0;
        }
        else{
            intermediate_mark=$('#intermediate-mark').val();
        }
    }

    if ($('#advance-que').val()==''){
        advance=0;
        advance_mark=0;
    }
    else{
        advance=parseInt($('#advance-que').val());
        if($('#advance-mark').val()==''){
            advance_mark=0;
        }
        else{
            advance_mark=$('#advance-mark').val();
        }
    }
    
    console.log($('#intermediate-que').val())
    console.log(intermediate_mark)
    var total_mark=(parseInt(basic)*parseInt(basic_mark))+(parseInt(intermediate)*parseInt(intermediate_mark))+(parseInt(advance)*parseInt(advance_mark));
    $('#total_exam_mark').val(total_mark);
})


   

