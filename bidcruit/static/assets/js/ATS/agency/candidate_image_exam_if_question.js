

			var questions = '';
			var currentQuestion = 0;
			var viewingAns = 0;
			var correctAnswers = 0;
			var quizOver = false;
			var iSelectedAnswer = [];

			var seconds_get = '';
			var c=seconds_get;  // add seconds to display time
			var t;
			var image_path='';
			$(document).ready(function ()
			{
			    questions = get_mcqData();
				// populate question no list
				var total_question = questions.length;
                console.log(questions)
                for(var i=1; i<=total_question;i++){
					$('<li id="que-'+i+'" class="notvisited">'+i+'</li>').appendTo($('.question-no-list'));
				}



				displayCurrentQuestion();

				// Display the thime
				timedCount();

				
                $(".rdiobox").change(function(){
                    image_path=$(this).next('.ans_option_image').find('img').attr('src');
                });
				// On clicking next, display the next question
				$(".btn_next").on("click", function ()
				{

					if (!quizOver)
					{

						var val = $("input[type='radio']:checked").val();
						var que_id_get = $("input[name='que_id_get']").val();
						var ans_response='';

						Calendar_color_change(val,que_id_get,ans_response);
                        var que_id =$('#que_id').val();
						if (val == undefined )
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
                            url:"/candidate/agency_image_exam_fill/"+temp_id+"/"+job_id,
                            headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
                            type:'POST',
                            contentType: 'application/json; charset=UTF-8',
                            data: JSON.stringify({'mcq_ans':ans_response,'que_id':que_id,'que_time':que_time,'image_path':image_path,'last':last}),
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

						if (val !== '')
						{
							// TODO: Remove any message -> not sure if this is efficient to call this each time....
							// $('#que-'+que_id_get).attr('class', 'skip'); // calender color changes

							iSelectedAnswer[currentQuestion] = val;
							ans_response=val;
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
				if (val == undefined)
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
					if(questions.length==questions[currentQuestion].id)
                       {
                            return false;
                       }
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
				var base_url= window.location.protocol+'//'+window.location.host
				//if(c == 185) { c = 180; timedCount(); }
				//console.log("In display current Question");
				var seconds_get = questions[currentQuestion].time;
				var question_count = questions[currentQuestion].id;
				var question_id = questions[currentQuestion].dbid;
				var total_question = questions.length;
				var question = questions[currentQuestion].question;
				var questionClass = $(document).find(".Question_listing .question_text");
				var choiceList = $(document).find(".Question_listing .choiceList");
				var numChoices = questions[currentQuestion].choices.length;
				// Set the questionClass text to the current question
				$(".question-no").text(question_count+'/'+total_question);
                $('#que_id').val(question_id);
				$(questionClass).text(question);
				$(".Question_listing .question_image").html('<img src="'+base_url+ questions[currentQuestion].q_image+'">')

				// Remove all current <li> elements (if any)
				$(choiceList).find(".option_tab_q").remove();
				var choice;


				$(".question_selection_info ul li").css("border", "1px solid transparent");
				$("#que-"+question_count).css("border", "1px solid #0068ff");

				for (i = 0; i < numChoices; i++)
				{
					choice = questions[currentQuestion].choices[i];
                    choices=questions[currentQuestion].choice_no[i];
                    console.log(questions[currentQuestion].choicesimage)
                    if (questions[currentQuestion].choicesimage[i]==null){

                        var ans_image ='<div class="ans_option_image"></div>';
                    }
                    else{
				        var ans_image ='<div class="ans_option_image"><img src="'+base_url+''+questions[currentQuestion].choicesimage[i]+'"></div>';
                    }

					if(iSelectedAnswer[currentQuestion] == i) {
						$('<div class="option_tab_q"><label class="rdiobox"><input name="basic_radio" checked="checked" type="radio" value=' + choices + ' data-parsley-multiple="basic_radio"><span>' +  ' ' + choice  + '</span></label>'+ans_image+'<input type="hidden" value="'+question_count+'" name="que_id_get"></div>').appendTo(choiceList);
					} else {
						$('<div class="option_tab_q"><label class="rdiobox"><input name="basic_radio" type="radio" value=' + choices + ' data-parsley-multiple="basic_radio"><span>' +  ' ' + choice  + '</span></label>'+ans_image+'<input type="hidden" value="'+question_count+'" name="que_id_get"></div>').appendTo(choiceList);
					}
				}
				c = seconds_get;

			}
