$(function() {

    var total_basic_avl;
    var total_intermediate_avl;
    var total_advance_avl;

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

    $("input[name='question-wise-time']").click(function() {
        if($(this).is(':checked')){
           
            // $(".total-time").css('disabled', true);
            $("#total-time").attr('disabled','disabled');
            $("#total-time").val('');
            $("#total-time").removeClass("error");
            $("#total-time-error").html("");
            

        } else {
            // $(".total-time").css('disabled', false);
            $("#total-time").removeAttr('disabled');

        }
    });

    $("input[name='nagative-mark']").click(function() {
        if($(this).is(':checked')){

            $(".nagative-mark-add").removeAttr("readonly");
            $(".nagative-mark-add").attr('required','true');
        } else {
            $(".nagative-mark-add").prop('readonly', true);
            $(".nagative-mark-add").removeAttr("required");
            $(".nagative-mark-add").removeClass("error");
            $("#negative_mark_percent-error").html("");
            
            
        }
    });


    $("input[name='examtype']").click(function() {
        if ($("#random").is(":checked")) {
            $(".question-wise").hide();
            //$(".total-time").prop('disabled', false);
            $("#total-time").removeAttr('disabled');
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

        if(parseInt(advance) > parseInt(total_advance_avl)){
            alert("There are only  "+ total_advance_avl + "questions available in the advance category of mcq question bank")
            $('#advance-que').val('');
        }else{
            check_queno_type(basic,intermediate,advance);
        }

    })


    $('#intermediate-que').change(function() {
        var basic=$('#basic-que').val();
        var intermediate=$('#intermediate-que').val();
        var advance=$('#advance-que').val();
        var subject_id=$('#subject').val();
    
        var total_question_count = parseInt(basic) + parseInt(intermediate) + parseInt(advance)

        if(typeof(total_question_count) != 'number'  || subject_id == ""){
             return false;
        }
         
        if(parseInt(intermediate) > parseInt(total_intermediate_avl)){
            alert("There are only  "+ total_intermediate_avl + "questions available in the intermediate category of mcq question bank")
            $('#intermediate-que').val('');
        }else{
            check_queno_type(basic,intermediate,advance);
        }

    })


    $('#basic-que').change(function() {
        var basic=$('#basic-que').val();
        var intermediate=$('#intermediate-que').val();
        var advance=$('#advance-que').val();
        var subject_id=$('#subject').val();
    
        var total_question_count = parseInt(basic) + parseInt(intermediate) + parseInt(advance)
         // var flag = true;
        if(typeof(total_question_count) != 'number'  || subject_id == ""){
             return false;
        }

        if(parseInt(basic) > parseInt(total_basic_avl)){
            alert("There are only  "+ total_basic_avl + "questions available in the basic category of mcq question bank")
            $('#basic-que').val('');
        }else{
            check_queno_type(basic,intermediate,advance);
        }
        
    })



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

    $('#subject').change(function(){
        let subject_id = $('#subject').val();
        $.ajax({
            url:"/agency/mcq_total_questions/" + subject_id + "",
            headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
            type:'POST',
            error: function (request, status, error) {
                    alert(error);
            }
        }).done(function(response){
            response=JSON.parse(response)
            console.log(response)
            if(response['status'] == true){

                total_basic_avl = response['basic_count'];
                total_intermediate_avl = response['intermediate_count'];
                total_advance_avl = response['advance_count'];
                $('.avl_basic').text('Available question :' + response['basic_count'])
                $('.avl_inter').text('Available question :' + response['intermediate_count'])
                $('.avl_advance').text('Available question :' + response['advance_count'])
            }else{
                alert('something went wrong !!')
            }
        });
    });
    
});


function check_queno_type(basic,intermediate,advandce)
{
    console.log('callled', basic, intermediate, advandce);
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
    
    var sum=parseInt(basic_que)+parseInt(intermediate_que)+parseInt(advandce_que);
    $('#total-que').val(sum);
   
}
 



   

