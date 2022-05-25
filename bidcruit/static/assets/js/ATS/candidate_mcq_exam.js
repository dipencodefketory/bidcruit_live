var currentQuestion = 0;
var viewingAns = 0;
var correctAnswers = 0;
var quizOver = false;
var iSelectedAnswer = [];
var review = false;
var questions='';
var seconds_get = '';
var seconds_get = parseInt(get_totaltime());
var c=seconds_get;   // add seconds to display time
var t;
var ans=[];
$(document).ready(function ()
{
    questions = get_mcqData();
    for(jj=0;jj<questions.length;jj++){
        ans.push({
            q_id: questions[jj]['dbid'],
            q_ans:''
        });

    }
    // populate question no list
    var total_question = questions.length;

    for(var i=1; i<=total_question;i++){
        $('<li id="que-'+i+'" class="notvisited">'+i+'</li>').appendTo($('.question-no-list'));
    }

    displayCurrentQuestion();
    $(".btn_previous").attr('disabled', 'disabled');

    // Display the thime
    timedCount();

    $(".btn_previous").on("click", function ()
    {

        if (!quizOver)
        {

            var val = $("input[type='radio']:checked").val();
            var que_id_get = $("input[name='que_id_get']").val();
            var ans_response='';

            Calendar_color_change(val,que_id_get,ans_response);

            if(currentQuestion == 0) { return false; }

            // iSelectedAnswer[currentQuestion] = val;
            // ans_response=val;
            // currentQuestion++; // Since we have already displayed the first question on DOM ready

            if(currentQuestion == 1) {
            $(".btn_previous").attr('disabled', 'disabled');
            }
                iSelectedAnswer[currentQuestion] = val;
                // ans_response=val;
                currentQuestion--; // Since we have already displayed the first question on DOM ready
                if (currentQuestion < questions.length)
                {
                    displayCurrentQuestion();

                }
        } else {
            // if(viewingAns == 3) { return false; }
            // currentQuestion = 0; viewingAns = 3;
            // viewResults();
        }
    });


var seconds_get = parseInt(get_totaltime());
    $(".btn_clear").on("click", function ()
    {

        var que_id_get = $("input[name='que_id_get']").val();
        $("input[name='basic_radio']").prop("checked", false);



    });

    $(".btn_review").on("click", function ()
    {
        var que_id_get = $("input[name='que_id_get']").val();
        review=true;
        $('#que-'+que_id_get).attr('class', 'review'); // calender color changes

    });



    // On clicking next, display the next question
    $(".btn_next").on("click", function ()
    {

        if (!quizOver)
        {
            var val = $("input[type='radio']:checked").val();
            var que_id_get = $("input[name='que_id_get']").val();
            var ans_response='';
            var que_id =$('#que_id').val();
            Calendar_color_change(val,que_id_get,ans_response);
            if (val == undefined)
            {
                ans_response=''
            }

           else
            {

                for(j=0;j<ans.length;j++)
                {
                    if(ans[j].q_id==que_id){
                            ans[j].q_ans=val
                    }
                }
                console.log(ans)
                // TODO: Remove any message -> not sure if this is efficient to call this each time....
                // $('#que-'+que_id_get).attr('class', 'skip'); // calender color changes
                var last=false;
                iSelectedAnswer[currentQuestion] = val;
                ans_response=val;

            }
            if(questions.length==questions[currentQuestion].id)
                {
                    last=true;
                }
                else{
                    last=false;
                }
                job_id=$('#job_id').val();
                temp_id=$('#temp_id').val();
                que_time=$('#timer_exam').text();

                $.ajax({
                    url:"/candidate/mcq_exam_fill/"+temp_id+"/"+job_id,
                    headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
                    type:'POST',
                    contentType: 'application/json; charset=UTF-8',
                    data: JSON.stringify({'mcq_ans':ans_response,'que_id':que_id,'que_time':que_time,'last':last}),
                    error: function (request, status, error) {
                          alert(error);
                    }
                }).done(function(response){
                    last=JSON.parse(response['last'])

                    if(last == true){
                        window.location.href='http://'+response['url']
                    }
                });
            currentQuestion++;
            if(currentQuestion >= 1) {
                    $('.btn_previous').prop("disabled", false);
                }

                if (currentQuestion < questions.length)
                {

                    displayCurrentQuestion();

                    review=false;
                }
                else
                {

                    $('#timer_exam').html('Quiz Time Completed!');

                    // $(document).find(".preButton").text("View Answer");
//                     $(document).find(".nextButton").text("Play Again?");
                    last=true
                   $( ".btn_next" ).trigger( "click" );
                    quizOver = true;
                    return false;

                }

        }
        else
        { // quiz is over and clicked the next button (which now displays 'Play Again?'

            // quizOver = false; $('#timer_exam').html('Time Remaining:'); iSelectedAnswer = [];
            // // $(document).find(".btn_next").text("Next Question");
            // // $(document).find(".preButton").text("Previous Question");
            // $(".btn_previous").attr('disabled', 'disabled');

            // viewingAns = 1;
            // displayCurrentQuestion();

        }
    });


    //Calendar click event
    $('.question-no-list li').click(function() {

        var calendar_no = this.id;
        var calendar_val_New=calendar_no.split('-');
        var no_get = calendar_val_New[1];

        currentQuestion = Number(no_get);

        $(".question_selection_info ul li").css("border", "1px solid transparent");
        $(this).css("border", "1px solid #0068ff");
        if (!quizOver)
        {

            var val = $("input[type='radio']:checked").val();
            var que_id_get = $("input[name='que_id_get']").val();
            var ans_response='';


            if(currentQuestion == 0) { return false; }

            // iSelectedAnswer[currentQuestion] = val;
            // ans_response=val;
            // currentQuestion++; // Since we have already displayed the first question on DOM ready

            if(currentQuestion == 1) {
                $(".btn_previous").attr('disabled', 'disabled');
            }else{
                $(".btn_previous").removeAttr('disabled');
            }
            iSelectedAnswer[currentQuestion] = val;
            // ans_response=val;
            currentQuestion--; // Since we have already displayed the first question on DOM ready
            if (currentQuestion < questions.length)
            {
                displayCurrentQuestion();

            }
        } else {
            // if(viewingAns == 3) { return false; }
            // currentQuestion = 0; viewingAns = 3;
            // viewResults();
        }


    });


});


function Calendar_color_change(val,que_id_get,ans_response){

    var cs1 = $("#que-"+que_id_get).attr("class");



    if(cs1 != 'review'){

        if(review == true){
                ans_response=val;

        }else{

            if (val == undefined)
            {

                ans_response='null'
                $('#que-'+que_id_get).attr('class', 'skip'); // calender color changes

            }
            else{

                $('#que-'+que_id_get).attr('class', 'answer'); // calender color changes
            }
        }
    }

    }
function timedCount()
{
    var hours = parseInt( c / 3600 ) % 24;
    var minutes = parseInt( c / 60 ) % 60;
    var seconds = c % 60;
    var result = (hours < 10 ? "0" + hours : hours) + ":" + (minutes < 10 ? "0" + minutes : minutes) + ":" + (seconds  < 10 ? "0" + seconds : seconds);
    $('#timer_exam').html(result);

    if(c == 0 )
    {
        $('#timer_exam').html('Quiz Time Completed!');
            var val = $("input[type='radio']:checked").val();
            var que_id_get = $("input[name='que_id_get']").val();
            var ans_response='';
            var que_id =$('#que_id').val();
            var last=true;
            Calendar_color_change(val,que_id_get,ans_response);
            if (val == undefined)
            {
                ans_response=''
            }
           else
            {
                for(j=0;j<ans.length;j++)
                {
                    if(ans[j].q_id==que_id){
                            ans[j].q_ans=val
                    }
                }
                iSelectedAnswer[currentQuestion] = val;
                ans_response=val;
            }
                job_id=$('#job_id').val();
                temp_id=$('#temp_id').val();
                que_time=$('#timer_exam').text();

                $.ajax({
                    url:"/candidate/mcq_exam_fill/"+temp_id+"/"+job_id,
                    headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
                    type:'POST',
                    contentType: 'application/json; charset=UTF-8',
                    data: JSON.stringify({'mcq_ans':ans_response,'que_id':que_id,'que_time':que_time,'last':last}),
                    error: function (request, status, error) {
                          alert(error);
                    }
                }).done(function(response){
                    last=JSON.parse(response['last'])

                    if(last == true){
                        window.location.href='http://'+response['url']
                    }
                });
        return false;
    }
    if(c <= 10 )
    {
        $("#timer_exam").css("color", "red");
    }
    c = c - 1;
    t = setTimeout(function()
    {
        timedCount()
    },1000);
}


// This displays the current question AND the choices
function displayCurrentQuestion()
{

    //if(c == 185) { c = 180; timedCount(); }
    //console.log("In display current Question");
    var question_count = questions[currentQuestion].id;
    var question_id = questions[currentQuestion].dbid;

    var total_question = questions.length;
    var question = questions[currentQuestion].question;
    var questionClass = $(document).find(".Question_listing .question_text");
    var choiceList = $(document).find(".Question_listing .choiceList");
    var numChoices = questions[currentQuestion].choices.length;
    // Set the questionClass text to the current question
    $(".question-no").text(question_count+'/'+total_question);
    $(questionClass).text(question);
    $('#que_id').val(question_id);
    // Remove all current <li> elements (if any)
    $(choiceList).find(".option_tab_q").remove();
    var choice;


    $(".question_selection_info ul li").css("border", "1px solid transparent");
    $("#que-"+question_count).css("border", "1px solid #0068ff");
    for (i = 0; i < numChoices; i++)
    {
        choice = questions[currentQuestion].choices[i];
        choices=questions[currentQuestion].choice_no[i];
        chk_ans=''
        for(j=0;j<ans.length;j++)
        {
            if(ans[j].q_id==question_id){
                if(ans[j]['q_ans']==''){

                }
                else{
                    console.log(ans[j]['q_id'])
                    chk_ans=ans[j]['q_ans']
                }
            }
        }

            if(chk_ans == choices) {
                $('<div class="option_tab_q"><label class="rdiobox"><input name="basic_radio" checked="checked" type="radio" value=' + choices + ' data-parsley-multiple="basic_radio"><span>' +  ' ' + choice  + '</span></label><input type="hidden" value="'+question_count+'" name="que_id_get"></div>').appendTo(choiceList);
            } else {
                $('<div class="option_tab_q"><label class="rdiobox"><input name="basic_radio" type="radio" value=' + choices + ' data-parsley-multiple="basic_radio"><span>' +  ' ' + choice  + '</span></label><input type="hidden" value="'+question_count+'" name="que_id_get"></div>').appendTo(choiceList);
            }

    }
//    c = seconds_get
}
 