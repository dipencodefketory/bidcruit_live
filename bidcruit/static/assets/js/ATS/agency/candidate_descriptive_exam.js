
var questions = '';
var currentQuestion = 0;
var viewingAns = 0;
var correctAnswers = 0;
var quizOver = false;
var iSelectedAnswer = [];
var ans_response='';
var seconds_get = '';
var c=seconds_get;  // add seconds to display time
var t;
var ans=[];
$(document).ready(function ()
{
    // populate question no list
    questions = get_mcqData();
    for(jj=0;jj<questions.length;jj++){
        ans.push({
            q_id: questions[jj]['dbid'],
            q_ans:''
        });

    }
    var total_question = questions.length;

    for(var i=1; i<=total_question;i++){
        $('<li id="que-'+i+'" class="notvisited">'+i+'</li>').appendTo($('.question-no-list'));
    }



    displayCurrentQuestion();

    // Display the thime
    timedCount();



    // On clicking next, display the next question
    $(".btn_next").on("click", function ()
    {

        if (!quizOver)
					{
                        var last=false;
                        var que_id_get = $("input[name='que_id_get']").val();
						tinyMCE.triggerSave();
						var val =$("#quillEditor_"+que_id_get).val();
						var que_id =$('#que_id').val();

						if (val == '' )
						{
						    ans_response='';
						}
                        else{
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
                            url:"/candidate/descriptive_exam_fill/"+temp_id+"/"+job_id,
                            headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
                            type:'POST',
                            contentType: 'application/json; charset=UTF-8',
                            data: JSON.stringify({'que_id':que_id,'que_time':que_time,'last':last,'ans':ans_response}),
                            error: function (request, status, error) {
                                  alert(error);
                            }
                       }).done(function(response){
                            last=JSON.parse(response['last'])

                            if(last == true){
//                                url=JSON.parse(response['url'])
//                                console.log(response['url'])
                                window.location.href='http://'+response['url']
                            }
                       });

                        Calendar_color_change(val,que_id_get,ans_response);

                        iSelectedAnswer[currentQuestion] = val;
                        currentQuestion++; // Since we have already displayed the first question on DOM ready
                        if (currentQuestion < questions.length)
                        {
                            displayCurrentQuestion();
                        }
                        else
                        {
                            $('#timer_exam').html('Quiz Time Completed!');
                            // $(document).find(".preButton").text("View Answer");
                            // $(document).find(".nextButton").text("Play Again?");
                            quizOver = true;
                            clearTimeout(t); // stop the interval
                            alert('Quiz Time Completed!');
                            return false;

                        }



					}
        else
        { // quiz is over and clicked the next button (which now displays 'Play Again?'

            // quizOver = false; $('#timer_exam').html('Time Remaining:'); iSelectedAnswer = [];
            // // $(document).find(".btn_next").text("Next Question");
            // // $(document).find(".preButton").text("Previous Question");

            // viewingAns = 1;
            // displayCurrentQuestion();


        }
    });



});


function Calendar_color_change(val,que_id_get,ans_response){

    var cs1 = $("#que-"+que_id_get).attr("class");
    if (val == '')
    {

        ans_response='null'
        $('#que-'+que_id_get).attr('class', 'skip'); // calender color changes

    }
    else{
        $('#que-'+que_id_get).attr('class', 'answer'); // calender color changes
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
        //$('#timer_exam').html('Quiz Time Completed!');
        $(".btn_next").trigger( "click" );
    }
    if(c <= 10 )
    {
        $("#timer_exam").css("color", "red");
    }else{
        $("#timer_exam").css("color", "#031b4e");
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
    var seconds_get = questions[currentQuestion].time;
    var question_count = questions[currentQuestion].id;
    var question_id = questions[currentQuestion].dbid;
    var total_question = questions.length;
    var question = questions[currentQuestion].question;
    var questionClass = $(document).find(".Question_listing .question_text");
    var choiceList = $(document).find(".Question_listing .choiceList");
    // var numChoices = questions[currentQuestion].choices.length;
    // Set the questionClass text to the current question
    console.log(question_id)
    $('#que_id').val(question_id);
    $(".question-no").text(question_count+'/'+total_question);
    $(questionClass).html(question);
    // Remove all current <li> elements (if any)
        tinymce.remove();

    $(choiceList).find(".option_tab_q").remove();
    var choice;


    $(".question_selection_info ul li").css("border", "1px solid transparent");
    $("#que-"+question_count).css("border", "1px solid #0068ff");


    var Data_clone_a ="<div class='question_response_detail'><textarea id='quillEditor_"+question_count+"'></textarea></div>";

    $('<div class="option_tab_q">'+Data_clone_a+'<input type="hidden" value="'+question_count+'" name="que_id_get"></div>').appendTo(choiceList);

    // tiny code
    let tiny_id = "#quillEditor_" + question_count;
    tinymce.init({
        selector: tiny_id,
        menubar: false,
        plugins: [
            'advlist autolink lists',
            'visualblocks code',

        ],
        toolbar:
        'bold italic  | alignleft aligncenter ' +
        'alignright alignjustify | bullist numlist  | ',
        content_style: 'body { font-family:Helvetica,Arial,sans-serif; font-size:14px }'
    });

    // for (i = 0; i < numChoices; i++)
    // {
    // 	choice = questions[currentQuestion].choices[i];

    // 	if(iSelectedAnswer[currentQuestion] == i) {
    // 		$('<div class="option_tab_q"><label class="rdiobox"><input name="basic_radio" checked="checked" type="radio" value=' + i + ' data-parsley-multiple="basic_radio"><span>' +  ' ' + choice  + '</span></label><input type="hidden" value="'+question_count+'" name="que_id_get"></div>').appendTo(choiceList);
    // 	} else {
    // 		$('<div class="option_tab_q"><label class="rdiobox"><input name="basic_radio" type="radio" value=' + i + ' data-parsley-multiple="basic_radio"><span>' +  ' ' + choice  + '</span></label><input type="hidden" value="'+question_count+'" name="que_id_get"></div>').appendTo(choiceList);
    // 	}
    // }

    c = seconds_get;  // par question time add

}
