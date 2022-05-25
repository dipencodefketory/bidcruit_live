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


$('#subject').change(function() {
    var subject_id=$('#subject').val();
     // var flag = true;
     
    $.ajax({
             url:"/agency/descriptive_get_count/",
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
                        console.log(response)
                        $('#totalque').text(response['basic_count'])
                        // if(parseInt(basic) <= parseInt(response['basic_count'])){
                        //     check_queno_type(basic);
                        // }
                        // else{
                        //     alert("there are only "+response['basic_count'] + "question/questions in the descriptive question_bank")
                        //     $('#total-que').val('');
                        // }
                    }else{
                        swal("Error!", "Something Wrong !!", "error");
                    }
                });


})

function check_queno_type(basic)
{
    var basic_que=0;

    if(basic!==''){
        basic_que=basic;
    }
    var total=$('#total-que').val();
    var sum=parseInt(basic_que);
    if(parseInt(total)<sum){
        alert('please add total number of qustion')
        $('#total-que').val('');

    }
}

