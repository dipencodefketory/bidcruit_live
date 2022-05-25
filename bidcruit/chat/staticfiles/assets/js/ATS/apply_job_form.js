$(document).ready(function(){

    $("#tncCheckBox").on('click',function(){ //footer checkbox event
        if($(this).is(':checked')){
            $('#tncPrompt').modal();
        }else{
            $("#submitAjtForm").attr('type','button')
            $("#submitAjtForm").attr('name','button')
            $("#submitAjtForm").attr('disabled','')
        }
    })

    $('#cancleBtnOfTnC').on('click',function(){ //decline button action
        $("#tncCheckBox").prop('checked',false);
        $("#popUpModelClose").trigger('click');
    })
    $("#agreeBtnOfTnC").on('click',function(){ //agree button action
        $("#submitAjtForm").attr('type','submit')
        $("#submitAjtForm").attr('name','submit')
        $("#submitAjtForm").removeAttr('disabled')
        $("#popUpModelClose").trigger('click');
    })
    $("#otpPopup").modal({
        show: false,
        backdrop: 'static'
    });
      function snakBarShow(getParamOfMsg){ //Activity of Snackbar
      //{msg:"Snackbars contain a text label that directly relates to the process being performed"}
      var newMsg = getParamOfMsg;
      console.log(newMsg)
      $("#snackbar").html('');
      $("#snackbar").append('<p>'+newMsg+'<p>');
      $("#snackbar").addClass('show')
      setTimeout(function(){ $("#snackbar").find('p').remove() }, 3000);
    }
    $('#otpActionBtn').on('click',function(){
        $('#otpPopup').modal();
         var seconds = 30;
         var  timer_start=0;
         timer_start = setInterval(function () {
            console.log(seconds)
            if (seconds >= 10) {
                 $("#lblCount").html('00:'+seconds);
            }
            else if (seconds < 10) {
                 $("#lblCount").html('00:0'+seconds);
            }
            seconds--;

            if (seconds == 0) {
                $("#lblCount").html('00:00');
                clearInterval(timer_start);
                $('#resend').removeAttr('href');
                $('#resend').attr('type','button');
            }

        }, 1000);
        var email=$('#registerInputemail').val();
        $.ajax({
				  url:"/accounts/apply_job_cadidate_sendotp",
				  type:'POST',
				  headers:{'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
				  data:{email:email}
				})
				.done(function(response){
				    response=JSON.parse(response)

					if(response.status==true){
					     snakBarShow('Email Send.');
					}
					else{
					    $(".email_error").remove();
						$("<span class='email_error' style='padding: 3px;color: red;'>"+response.message +"!!</span>").insertAfter(".email-input");
						$('#btn-email-proceed').attr('disabled','disabled');
						$("#submitAjtForm").attr('type','button')
                        $("#submitAjtForm").attr('name','button')
                        $("#submitAjtForm").attr('disabled','')
					}
				})
    })



    $('#verify').on('click',function(){
    if($('#first').val()!=='' && $('#second').val()!=='' && $('#third').val()!=='' && $('#fourth').val()!=='' && $('#fifth').val()!=='' && $('#sixth').val()!=='')
        {
            var otp=$('#first').val().toString()+$('#second').val().toString()+$('#third').val().toString()+$('#fourth').val().toString()+$('#fifth').val().toString()+$('#sixth').val().toString()
            var email=$('#registerInputemail').val();
            $.ajax({
                      url:"/accounts/job_apply_verify_otp",
                      type:'POST',
                      headers:{'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
                      data:{email:email,otp:otp}
                    })
                    .done(function(response){
                        response=JSON.parse(response)
                        if(response.status==true){
                            snakBarShow(response.message);
                            $('#otpPopup').modal('hide');
                            $('#otpActionBtn').css('display','none');
                            $("<span class='email_error' style='padding: 3px;color: green;'> Verified Email !!</span>").insertAfter("#registerInputemail");
                            $("#submitAjtForm").attr('type','submit')
                            $("#submitAjtForm").attr('name','submit')
                            $("#submitAjtForm").removeAttr('disabled')
                        }
                        else{
                            snakBarShow(response.message);
                            $("#submitAjtForm").attr('type','button')
                            $("#submitAjtForm").attr('name','button')
                            $("#submitAjtForm").attr('disabled','')
                        }
                    })
        }
        else{
            snakBarShow('Please Enter 6 digit OTP.');
        }
    })


    $('#resend').on('click',function(){
        var seconds = 30;
         var  timer_start=0;
         timer_start = setInterval(function () {
            console.log(seconds)
            if (seconds >= 10) {
                 $("#lblCount").html('00:'+seconds);
            }
            else if (seconds < 10) {
                 $("#lblCount").html('00:0'+seconds);
            }
            seconds--;

            if (seconds == 0) {
                $("#lblCount").html('00:00');
                clearInterval(timer_start)
            }

        }, 1000);
        var email=$('#registerInputemail').val();
        $.ajax({
				  url:"/accounts/apply_job_cadidate_sendotp",
				  type:'POST',
				  headers:{'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
				  data:{email:email}
				})
				.done(function(response){
				    response=JSON.parse(response)

					if(response.status==true){
					     snakBarShow('Email Send.');
					}
					else{
					    $(".email_error").remove();
						$("<span class='email_error' style='padding: 3px;color: red;'>"+response.message +"!!</span>").insertAfter(".email-input");
						$('#btn-email-proceed').attr('disabled','disabled');
						$("#submitAjtForm").attr('type','button')
                        $("#submitAjtForm").attr('name','button')
                        $("#submitAjtForm").attr('disabled','')
					}
				})
    });


    $(document).on("input", "#registerInputemail",function(e) {
        $(".email_error").remove();
	    $('#btn-email-proceed').removeAttr('disabled');
	    $('#otpActionBtn').show();
    });
    $("#registerInputemail").change(function(){
			var email=$(this).val();
			if(email!=""){
				$.ajax({
				  url:"/accounts/check_email_is_valid",
				  type:'POST',
				  headers:{'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
				  data:{email:email}
				})
				.done(function(response){
					if(response=="True"){

						$(".email_error").remove();
						$("<span class='email_error' style='padding: 3px;color: red;'>Email already exists !!</span>").insertAfter(".email-input");
						$('#btn-email-proceed').attr('disabled','disabled');
						$('#otpActionBtn').css('display','none');
					}else if(response=="Invalid"){


						$(".email_error").remove();
						$("<span class='email_error' style='padding: 3px;color: red;'> Invalid Email !!</span>").insertAfter("#registerInputemail");
						$('#btn-email-proceed').attr('disabled','disabled');
						$('#otpActionBtn').hide();
						$("#submitAjtForm").attr('type','button')
                        $("#submitAjtForm").attr('name','button')
                        $("#submitAjtForm").attr('disabled','')
					}
					else{

						$(".email_error").remove();
						$('#btn-email-proceed').removeAttr('disabled');
						$("#submitAjtForm").attr('type','button')
                        $("#submitAjtForm").attr('name','button')
                        $("#submitAjtForm").attr('disabled','')

					}
				}).fail(function(){
					  console.log("failed");
				})
			}else{
				$(".email_error").remove();
			}
		});
});



