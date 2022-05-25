$(function() {
    $("input[name='eachall']").click(function() {
        if ($("#eachques").is(":checked")) {
            $(".maksbox").hide();
            $("input[name=marks_of_basic_questions]").prop('required', false);
            $("input[name=marks_of_intermediate_questions]").prop('required', false);
            $("input[name=marks_of_advanced_questions]").prop('required', false);
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
            $(".total-time").prop('disabled', true);
            $("#total-time").val('');
        } else {
            $(".total-time").prop('disabled', false);
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
     $.ajax({
             url:"/company/image_get_advance_count/",
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
                            alert("there are only  "+ response['advance_count'] + "question/questions in the advance category of image question bank")
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
    $.ajax({
             url:"/company/image_get_intermediate_count/",
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
                            alert("there are only  "+ response['intermediate_count'] + "question/questions in the intermediate category of image question bank")
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
    $.ajax({
             url:"/company/image_get_basic_count/",
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
                            alert("there are only  "+ response['basic_count'] + "question/questions in the basic category of Image question bank")
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


$('#basic-mark').change(function() {
    var basic=$('#basic-que').val();
    var basic_mark=$('#basic-mark').val();
    var total_mark=(parseInt(basic)*parseInt(basic_mark));
    $('#total_exam_mark').val(total_mark);
})

$('#intermediate-mark').change(function() {
    var basic=$('#basic-que').val();
    var intermediate=$('#intermediate-que').val();
    var basic_mark=$('#basic-mark').val();
    var intermediate_mark=$('#intermediate-mark').val();
    var total_mark=(parseInt(basic)*parseInt(basic_mark))+(parseInt(intermediate)*parseInt(intermediate_mark));
    $('#total_exam_mark').val(total_mark);
})
$('#advance-mark').change(function() {
    var basic=$('#basic-que').val();
    var intermediate=$('#intermediate-que').val();
    var advance=$('#advance-que').val();
    var basic_mark=$('#basic-mark').val();
    var intermediate_mark=$('#intermediate-mark').val();
    var advance_mark=$('#advance-mark').val();
    var total_mark=(parseInt(basic)*parseInt(basic_mark))+(parseInt(intermediate)*parseInt(intermediate_mark))+(parseInt(advance)*parseInt(advance_mark));
    $('#total_exam_mark').val(total_mark);
})


//alert("there are only  "+ response['basic_count'] + "question/questions in the basic category of Image question bank")