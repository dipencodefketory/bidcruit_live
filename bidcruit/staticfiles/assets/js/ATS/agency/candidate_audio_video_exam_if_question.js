
    var questions ='';  

   	
    var currentQuestion = 0;
    var viewingAns = 0;
    var correctAnswers = 0;
    var quizOver = false;
    var iSelectedAnswer = [];
  

    var seconds_get =200;
    var is_video = get_exam_input_type()
  console.log("======================",is_video);
    if(is_video == 'False')
    {

      is_video = false
    }
    else
    {
      is_video = true
    }
    console.log("exam input type",is_video)
    var total_exam_time = get_total_exam_time();//it is in hh mm formata
    console.log("total exam time",total_exam_time)
    var elapsed_time = get_elapsed_time()

    
    var audio_blobs = []
    console.log("elapsed time ",elapsed_time)
    console.log(total_exam_time,total_exam_time)    
    // alert("tota lex am time",total_exam_time)
    var total_exam_time_hours = parseInt(total_exam_time.split(":")[0])
    var total_exam_time_minutes = parseInt(total_exam_time.split(":")[1])
    var total_exam_time_seconds = parseInt(total_exam_time.split(":")[2])

    var elapsed_hours = parseInt(elapsed_time.split(":")[0])
    var elapsed_minutes = parseInt(elapsed_time.split(":")[1])
    var elapsed_seconds = parseInt(elapsed_time.split(":")[2])

    console.log("a",total_exam_time_hours)
    console.log("a",total_exam_time_minutes)
    console.log("a",total_exam_time_seconds)

   
    // var c=  // add seconds to display time
    // alert("total timezz")
    var t;
    var audio_file='';
    var active_player = null;
    var all_players = {}

// #config for record js 
var videoMaxLengthInSeconds = 120;
var options = {
        controls: true,
        bigPlayButton: false,
        width: 300,
        height: 300,
        fluid: false,
        controlBar: {
            playToggle: true,
            captionsButton: false,
            chaptersButton: false,            
            subtitlesButton: false,
            remainingTimeDisplay: false,
            progressControl: {
              seekBar: true
            },
            fullscreenToggle: false,
            playbackRateMenuButton: true,
            hideScrollbar: true,

            // liveui:false
          },
            plugins: {
              wavesurfer: {
                  backend: 'WebAudio',
                  waveColor: '#6fffe9',
                  progressColor: 'black',
                  displayMilliseconds: true,
                  debug: true,
                  cursorWidth: 1,
                  hideScrollbar: true,
                  plugins: [
                      // enable microphone plugin
                      WaveSurfer.microphone.create({
                          bufferSize: 4096,
                          numberOfInputChannels: 1,
                          numberOfOutputChannels: 1,
                          constraints: {
                              video: false,
                              audio: true
                          }
                      })
                  ]
              },
            record: {
                audio: true,
                video: is_video,
                maxLength: 600,
                debug: true,
                displayMilliseconds: false,
                // audioEngine: 'recorder.js'
            }
        }
    };

var input_element = null


if(!is_video)
{
  input_element = "audio"
  options['plugins']['record']['audio_engine'] = 'recorder.js'
  // options['plugins']['wavesurfer'] =  {
  //       backend: 'WebAudio',
  //       waveColor: '#6fffe9',
  //       progressColor: 'black',
  //       displayMilliseconds: true,
  //       debug: true,
  //       cursorWidth: 1,
  //       hideScrollbar: true,
  //       plugins: [
  //           // enable microphone plugin
  //           WaveSurfer.microphone.create({
  //               bufferSize: 4096,
  //               numberOfInputChannels: 1,
  //               numberOfOutputChannels: 1,
  //               constraints: {
  //                   video: false,
  //                   audio: true
  //               }
  //           })
  //       ]
  //   }
}
else{
  input_element = "video"
}
console.log("options",options)
console.log("input element",input_element)
   
    $(document).ready(function () 
    {
        // var c=200;

        if(input_element == "video")
        {
          $("wave").hide()
        }
        var b = parseInt(elapsed_hours)*3600 + parseInt(elapsed_minutes)*60 +elapsed_seconds
        var c = parseInt(total_exam_time_hours)*3600 + parseInt(total_exam_time_minutes)*60 +total_exam_time_seconds
        console.log("cccc",c)
        console.log("bbbb",b)
        c=c-b
        console.log("thev value of c is ",c)

        questions = get_mcqData();
        console.log("alll questions",questions)
        for(var i =0;i<questions.length;i++)
        {
          audio_blobs.push(null)
        }
        console.log("audio blobs",audio_blobs)

        // populate question no list
        var total_question = questions.length;

        for(var i=1; i<=total_question;i++){
            $('<li id="que-'+i+'" class="notvisited">'+i+'</li>').appendTo($('.question-no-list'));
        }

        
        create_all_questions(questions);
        console.log("after acreate all questions")
        // displayCurrentQuestion();
        
        // Display the thime	
        console.log("before timed count")			
        timedCount(c)
                    
       
        
        // On clicking next, display the next question
        $(".btn_next").on("click", function () 
        {
            active_player.record().stopDevice()  
            active_player = null
            var question_count = questions[currentQuestion].id;
            console.log("question count",question_count )

            if(audio_blobs[question_count-1] == null)
            {
              $('#que-'+question_count).attr('class', 'skip'); // calender color changes
            }
            else {
              $('#que-'+question_count).attr('class', 'answer');
            }
            if (!quizOver) 
            {
                
                var val = $("input[type='radio']:checked").val();
                var que_id_get = $("input[name='que_id_get']").val();
                var ans_response='';
                var que_id =$('#que_id').val();
                
                Calendar_color_change(val,que_id_get,ans_response);  
                console.log("current question ",currentQuestion)                   
                if(currentQuestion ==questions.length-1)
                   {
                    ans_response='null'
                    job_id=$('#job_id').val();
                    temp_id=$('#temp_id').val();
                    que_time=$('#timer_exam').text();
                    var formData = new FormData();
                    // formData.append("que_id",que_id);
                    // formData.append("que_time",que_time);
                    // formData.append("last",last);
                    // formData.append("ans",audio_file);
                    console.log("exam_paper_id",temp_id)

                    var final_question_ids = []
                    for(var i =0;i<audio_blobs.length;i++)
                    {
                      final_question_ids[i] = questions[i].dbid
                      var blob_tag = questions[i].dbid+"blob"
                      formData.append(blob_tag,audio_blobs[i])
                    }
                    // formData.append("blobs",audio_blobs);
                    formData.append("questions",final_question_ids);
                    $.ajax({
                            url:"/candidate/agency_audio_exam_fill/"+temp_id+"/"+job_id,
                        headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
                        type:'POST',
                        contentType: false,
                        processData: false,
                        enctype: 'multipart/form-data',
                        data: formData,
                        error: function (request, status, error) {
                              alert(error);
                        }
                   }).done(function(response){
                        window.location.replace("/candidate/agency_audio_result/"+temp_id+"/"+job_id);
                   });
                   } 
                    

               
                    // TODO: Remove any message -> not sure if this is efficient to call this each time....
                    // $('#que-'+que_id_get).attr('class', 'skip'); // calender color changes
                    
                    iSelectedAnswer[currentQuestion] = val;
                    ans_response=val;
                    currentQuestion++; // Since we have already displayed the first question on DOM ready
                    
                   
               
                if (currentQuestion < questions.length) 
                {
                    // displayCurrentQuestion();
                    displayQuestion(questions[currentQuestion].dbid);
                    console.log("current question now",questions[currentQuestion].dbid)
                    console.log("all_players")
                    active_player = all_players[questions[currentQuestion].dbid]
                    active_player.record().getDevice()
                } 
                else 
                {
                    
                    $('#timer_exam').html('Quiz Time Completed!');
                
                    // $(document).find(".preButton").text("View Answer");
                    // $(document).find(".nextButton").text("Play Again?");
                    quizOver = true;
                    clearTimeout(t); // stop the interval
                    alert('Completed!');
                    
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

        // On clicking next, display the prev question
        $(".btn_prev").on("click", function () 
        {
          console.log("current quest",currentQuestion)
            if((currentQuestion-1) ==-1)
            {
              alert("this is the first question!!!!!")
              return false
            }
            // alert("non stop")
            active_player.record().stopDevice()
            active_player = null
            var question_count = questions[currentQuestion].id;
            console.log("question count",question_count )

            if(audio_blobs[question_count-1] == null)
            {
              $('#que-'+question_count).attr('class', 'skip'); // calender color changes
            }
            else {
              $('#que-'+question_count).attr('class', 'answer');
            }
            if (!quizOver) 
            {
                
                var val = $("input[type='radio']:checked").val();
                var que_id_get = $("input[name='que_id_get']").val();
                var ans_response='';
                var que_id =$('#que_id').val();
                
                Calendar_color_change(val,que_id_get,ans_response);                     
                if(questions.length==questions[currentQuestion].id)
                        {
                            last=true;
                        }
                        else{
                            last=false;
                        }
                    ans_response='null'
                    job_id=$('#job_id').val();
                    temp_id=$('#temp_id').val();
                    que_time=$('#timer_exam').text();
                    var formData = new FormData();
                    formData.append("que_id",que_id);
                    formData.append("que_time",que_time);
                    formData.append("last",last);
                    formData.append("ans",audio_file);

               
                    // TODO: Remove any message -> not sure if this is efficient to call this each time....
                    // $('#que-'+que_id_get).attr('class', 'skip'); // calender color changes
                    
                    iSelectedAnswer[currentQuestion] = val;
                    ans_response=val;
                    currentQuestion--; // Since we have already displayed the first question on DOM ready
                    
                  console.log("currentWUESTION",currentQuestion)
               
                if (currentQuestion >= 0) 
                {
                    // displayCurrentQuestion();
                    displayQuestion(currentQuestion);
                    // active_player = all_players[currentQuestion]
                    console.log("all_plyers",)
                    active_player = all_players[questions[currentQuestion].dbid]

                    // active_player.record().getDevice()
                } 
                else 
                {
                    
                    // $('#timer_exam').html('Quiz Time Completed!');
                
                    // // $(document).find(".preButton").text("View Answer");
                    // // $(document).find(".nextButton").text("Play Again?");
                    // quizOver = true;
                    // clearTimeout(t); // stop the interval
                    // alert('Completed!');
                    // alert("this is the first question!!!")
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
        if (val == undefined) 
        {
            
            ans_response='null'
            $('#que-'+que_id_get).attr('class', 'skip'); // calender color changes

        }
        else{				
            $('#que-'+que_id_get).attr('class', 'answer'); // calender color changes
        } 

    }

    function timedCount(c)
    {	
        //console.log("timece coitunt called",c)
        // var hours = parseInt(c.split(":"),[0])
        // var minutes = parseInt(c.split(":"),[1])
        var hours = parseInt( c / 3600 ) % 24;
        // console.log("hours",hours)
        var minutes = parseInt( c / 60 ) % 60;
        // console.log("minutes",minutes)
        var seconds = c % 60;
        // console.log("seconds",seconds)
        var result = (hours < 10 ? "0" + hours : hours) + ":" + (minutes < 10 ? "0" + minutes : minutes) + ":" + (seconds  < 10 ? "0" + seconds : seconds);            
        $('#timer_exam').html(result);
        
        if(c == 0 )
        {
            //$('#timer_exam').html('Quiz Time Completed!');
            stop();
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
            timedCount(c)
        },1000);
    }


    // This displays the current question AND the choices
    function displayCurrentQuestion() 
    {
        
        //if(c == 185) { c = 180; timedCount(); }
        //console.log("In display current Question");
        var seconds_get = questions[currentQuestion].time;
        var question_count = questions[currentQuestion].id;
        var total_question = questions.length;
        var question_id = questions[currentQuestion].dbid;
        var question = questions[currentQuestion].question;
        var questionClass = $(document).find(".Question_listing .question_text");
        var choiceList = $(document).find(".Question_listing .choiceList");
       
        // Set the questionClass text to the current question
        $('#que_id').val(question_id);
        $(".question-no").text(question_count+'/'+total_question);
        $(questionClass).html(question);
        // Remove all current <li> elements (if any)
        $(choiceList).find(".app").remove();
        $(".question_selection_info ul li").css("border", "1px solid transparent");
        $("#que-"+question_count).css("border", "1px solid #0068ff");
 
        var audio_data_tag = ""
        // if(audio_blobs[question_count-1] != null)
        // {
        //   var  audio_data = window.URL.createObjectURL(audio_blobs[question_count-1])
        //   audio_data_tag = `src="`+audio_data + `"`
        //   console.log("audio data tag",audio_data_tag)
        // }
        var audio_show=`<div class="app">
        

        <div class="audio-controls">
          
          <button id="start_recording">Start Recording</button>
          <button id="stop_recording" disabled>Stop Recording</button>
          <button id="reset_recording" disabled>Reset Recording</button>
          <button id="preview_recording" disabled>Preview</button>

          <`+input_element+` id="audio" controls class="video-js vjs-light-skin" `+audio_data_tag+`></`+input_element+`>
        </div>
      <div>`;
       
        
      console.log(audio_data_tag)
        $(audio_show).appendTo(choiceList);

       
        var start_button = document.querySelector("#start_recording")
        var pause_button = document.querySelector("#pause_recording")
        var stop_button = document.querySelector("#stop_recording")
        var reset_button = document.querySelector("#reset_recording")
        var preview_button = document.querySelector("#preview_recording")

        console.log("start vuttoon",start_button)

       

      console.log("all audios",document.querySelectorAll("audio"))
        var player = videojs('audio', options, function() {
            // print version information at startup
            var msg = 'Using video.js ' + videojs.VERSION +
                ' with videojs-record ' + videojs.getPluginVersion('record') +
                ', videojs-wavesurfer ' + videojs.getPluginVersion('wavesurfer') +
                ' and wavesurfer.js ' + WaveSurfer.VERSION;
            videojs.log(msg);

            
          
        });

        console.log("after video js intialization",document.querySelector("audio"))

        c = seconds_get;
       
        // player.src({src: blobURL, type: blob.type});



      active_player = player

      //  player.play()
        console.log("playerrrrrrrr",player)
        //active_player = player
        start_button.onclick = function(){
            //alert("called")
            
           console.log("recorder",player.wavesurfer())
          //  player.record().stopDevice()
         
           
          
            //player.start()
           //console.log("2nd playerssssssssss",player)
            //$(".vjs-record-button").trigger("click")
            $(start_button).prop('disabled', true);
            $(stop_button).prop('disabled', false);
            $(reset_button).prop('disabled', true);
            $(preview_button).prop('disabled', true);

            console.log("player record",player.record())
            player.record().start()
            //start_button.attr("disabled","disabled")

        }

        // pause_button.onclick = function(){
        //     player.record().pause()
        // }

        stop_button.onclick = function(){
            $(stop_button).prop('disabled', true);
            $(reset_button).prop('disabled', false);
            $(preview_button).prop('disabled', false);
            player.record().stop()
            console.log("player.wavesurfer",player.wavesurfer())
        }

        reset_button.onclick = function(){
          $(start_button).prop('disabled', false);

          $(preview_button).prop('disabled', true);
            player.record().reset()
            player.record().getDevice()

            //  question_count = questions[currentQuestion].id;
            // console.log("question count",question_count )
            $('#que-'+question_count).removeClass(['answer', 'skip']);

            
        }

        preview_button.onclick = function(){
            console.log("player record",player)
           //functionality unfinsihed
            //document.querySelector("audio").play()
            // player.record().pause()
            // document.querySelector("audio").play()
            $("button.vjs-paused").trigger("click")

          
        }

        player.on('ready', function() {
          // alert()
            // console.log("player on ready",player.wavesurfer().surfer.microphone)
            // player.record().reset()
            // player.record().surfer.surfer.backend.ac.resume()
            // player.play()
            // console.log("play butttttoooooon",$(".vjs-icon-audio-perm"))
            player.record().getDevice()
          
            if(audio_blobs[question_count-1] != null)
            {
              console.log("==============",audio_blobs[question_count-1])
              console.log("audoio",window.URL.createObjectURL(audio_blobs[question_count-1]))
              console.log("audio blob",audio_blobs[question_count-1])
              // player.src({src:window.URL.createObjectURL(audio_blobs[question_count-1]),type:audio_blobs[question_count-1].type});
              // player.load();
              // player.play();

              // var audio_element = document.querySelector("audio")
              // console.log("audio  dynamic or not",audio_element)
              // audio_element.src = window.URL.createObjectURL(audio_blobs[question_count-1])
              // player.wavesurfer().surfer.pause();

              // var video = videojs("audio");
              // video.src(window.URL.createObjectURL(audio_blobs[question_count-1]));
            }
            
            
           
           
          


        });
        // error handling for getUserMedia
        player.on('deviceError', function() {
            console.log('device error:', player.deviceErrorCode);
        });
        // Handle error events of the video player
        player.on('error', function(error) {
            console.log('error:', error);
        });
        // user clicked the record button and started recording !
        player.on('startRecord', function() {
            console.log('started recording! Do whatever you need to');
        });
        // user completed recording and stream is available
        // Upload the Blob to your server or download it locally !
        player.on('finishRecord', function() {
            // the blob object contains the recorded data that
            // can be downloaded by the user, stored on server etc.
            var question_count = questions[currentQuestion].id;
            var audioBlob = player.recordedData;
            audio_blobs[question_count-1] = audioBlob
            console.log("audio blobs",audio_blobs)
            console.log('finished recording: ', audioBlob);

            
            console.log("question count",question_count )

              $('#que-'+question_count).attr('class', 'answer'); // calender color changes
        });
        /*
        (async () => {
            let leftchannel = [];
            let rightchannel = [];
            let recorder = null;
            let recording = false;
            let recordingLength = 0;
            let volume = null;
            let audioInput = null;
            let sampleRate = null;
            let AudioContext = window.AudioContext || window.webkitAudioContext;
            let context = null;
            let analyser = null;
            let canvas = document.querySelector('canvas');
            let canvasCtx = canvas.getContext("2d");
            
            let micSelect = document.querySelector('#micSelect');
            let stream = null;
            let tested = false;
            
            try {
              window.stream = stream = await getStream();
              console.log('Got stream');  
            } catch(err) {
              alert('Issue getting mic', err);
            }
            
            const deviceInfos = await navigator.mediaDevices.enumerateDevices();
            
            var mics = [];
            for (let i = 0; i !== deviceInfos.length; ++i) {
              let deviceInfo = deviceInfos[i];
              if (deviceInfo.kind === 'audioinput') {
                mics.push(deviceInfo);
                let label = deviceInfo.label ||
                  'Microphone ' + mics.length;
                console.log('Mic ', label + ' ' + deviceInfo.deviceId)
                const option = document.createElement('option')
                option.value = deviceInfo.deviceId;
                option.text = label;
                micSelect.appendChild(option);
              }
            }
            
            function getStream(constraints) {
              if (!constraints) {
                constraints = { audio: true, video: false };
              }
              return navigator.mediaDevices.getUserMedia(constraints);
            }
            
            
            setUpRecording();
            
            function setUpRecording() {
              context = new AudioContext();
              sampleRate = context.sampleRate;
              
              // creates a gain node
              volume = context.createGain();
              
              // creates an audio node from teh microphone incoming stream
              audioInput = context.createMediaStreamSource(stream);
              
              // Create analyser
              analyser = context.createAnalyser();
              
              // connect audio input to the analyser
              audioInput.connect(analyser);
              
              // connect analyser to the volume control
              // analyser.connect(volume);
              
              let bufferSize = 2048;
              let recorder = context.createScriptProcessor(bufferSize, 2, 2);
              
              // we connect the volume control to the processor
              // volume.connect(recorder);
              
              analyser.connect(recorder);
              
              // finally connect the processor to the output
              recorder.connect(context.destination); 
          
              recorder.onaudioprocess = function(e) {
                // Check 
                if (!recording) return;
                // Do something with the data, i.e Convert this to WAV
                console.log('recording');
                let left = e.inputBuffer.getChannelData(0);
                let right = e.inputBuffer.getChannelData(1);
                if (!tested) {
                  tested = true;
                  // if this reduces to 0 we are not getting any sound
                  if ( !left.reduce((a, b) => a + b) ) {
                    alert("There seems to be an issue with your Mic");
                    // clean up;
                    stop();
                    stream.getTracks().forEach(function(track) {
                      track.stop();
                    });
                    context.close();
                  }
                }
                // we clone the samples
                leftchannel.push(new Float32Array(left));
                rightchannel.push(new Float32Array(right));
                recordingLength += bufferSize;
              };
              visualize();
            };
            
            
          
            function mergeBuffers(channelBuffer, recordingLength) {
              let result = new Float32Array(recordingLength);
              let offset = 0;
              let lng = channelBuffer.length;
              for (let i = 0; i < lng; i++){
                let buffer = channelBuffer[i];
                result.set(buffer, offset);
                offset += buffer.length;
              }
              return result;
            }
            
            function interleave(leftChannel, rightChannel){
              let length = leftChannel.length + rightChannel.length;
              let result = new Float32Array(length);
          
              let inputIndex = 0;
          
              for (let index = 0; index < length; ){
                result[index++] = leftChannel[inputIndex];
                result[index++] = rightChannel[inputIndex];
                inputIndex++;
              }
              return result;
            }
            
            function writeUTFBytes(view, offset, string){ 
              let lng = string.length;
              for (let i = 0; i < lng; i++){
                view.setUint8(offset + i, string.charCodeAt(i));
              }
            }
          
            function start() {
              recording = true;
            //   document.querySelector('#msg').style.visibility = 'visible'
              // reset the buffers for the new recording
              leftchannel.length = rightchannel.length = 0;
              recordingLength = 0;
              console.log('context: ', !!context);
              if (!context) setUpRecording();
            }
          
            function stop() {
              console.log('Stop')
              recording = false;
            //   document.querySelector('#msg').style.visibility = 'hidden'
              
              
              // we flat the left and right channels down
              let leftBuffer = mergeBuffers ( leftchannel, recordingLength );
              let rightBuffer = mergeBuffers ( rightchannel, recordingLength );
              // we interleave both channels together
              let interleaved = interleave ( leftBuffer, rightBuffer );
              
              ///////////// WAV Encode /////////////////
              // from http://typedarray.org/from-microphone-to-wav-with-getusermedia-and-web-audio/
              //
          
              // we create our wav file
              let buffer = new ArrayBuffer(44 + interleaved.length * 2);
              let view = new DataView(buffer);
          
              // RIFF chunk descriptor
              writeUTFBytes(view, 0, 'RIFF');
              view.setUint32(4, 44 + interleaved.length * 2, true);
              writeUTFBytes(view, 8, 'WAVE');
              // FMT sub-chunk
              writeUTFBytes(view, 12, 'fmt ');
              view.setUint32(16, 16, true);
              view.setUint16(20, 1, true);
              // stereo (2 channels)
              view.setUint16(22, 2, true);
              view.setUint32(24, sampleRate, true);
              view.setUint32(28, sampleRate * 4, true);
              view.setUint16(32, 4, true);
              view.setUint16(34, 16, true);
              // data sub-chunk
              writeUTFBytes(view, 36, 'data');
              view.setUint32(40, interleaved.length * 2, true);
          
              // write the PCM samples
              let lng = interleaved.length;
              let index = 44;
              let volume = 1;
              for (let i = 0; i < lng; i++){
                  view.setInt16(index, interleaved[i] * (0x7FFF * volume), true);
                  index += 2;
              }
          
              // our final binary blob
              const blob = new Blob ( [ view ], { type : 'audio/wav' } );
              audio_file=blob;
            //   const audioUrl = URL.createObjectURL(blob);
            //   console.log('BLOB ', blob);
            //   console.log('URL ', audioUrl);
            //   document.querySelector('#audio').setAttribute('src', audioUrl);
            //   const link = document.querySelector('#download');
            //   link.setAttribute('href', audioUrl);
            //   link.download = 'output.wav';


             
            }
            
            // Visualizer function from
            // https://webaudiodemos.appspot.com/AudioRecorder/index.html
            //
            function audio_download(){

              // our final binary blob
              const blob = new Blob ( [ view ], { type : 'audio/wav' } );
              
              const audioUrl = URL.createObjectURL(blob);
              console.log('BLOB ', blob);
              console.log('URL ', audioUrl);
              document.querySelector('#audio').setAttribute('src', audioUrl);
              const link = document.querySelector('#download');
              link.setAttribute('href', audioUrl);
              link.download = 'output.wav';
            }
            function visualize() {
              WIDTH = canvas.width;
              HEIGHT = canvas.height;
              CENTERX = canvas.width / 2;
              CENTERY = canvas.height / 2;
          
              let visualSetting = 'circle';
              console.log(visualSetting);
              if (!analyser) return;
          
              if(visualSetting === "sinewave") {
                analyser.fftSize = 2048;
                var bufferLength = analyser.fftSize;
                console.log(bufferLength);
                var dataArray = new Uint8Array(bufferLength);
          
                canvasCtx.clearRect(0, 0, WIDTH, HEIGHT);
          
                var draw = function() {
          
                  drawVisual = requestAnimationFrame(draw);
          
                  analyser.getByteTimeDomainData(dataArray);
          
                  canvasCtx.fillStyle = 'rgb(200, 200, 200)';
                  canvasCtx.fillRect(0, 0, WIDTH, HEIGHT);
          
                  canvasCtx.lineWidth = 2;
                  canvasCtx.strokeStyle = 'rgb(0, 0, 0)';
          
                  canvasCtx.beginPath();
          
                  var sliceWidth = WIDTH * 1.0 / bufferLength;
                  var x = 0;
          
                  for(var i = 0; i < bufferLength; i++) {
          
                    var v = dataArray[i] / 128.0;
                    var y = v * HEIGHT/2;
          
                    if(i === 0) {
                      canvasCtx.moveTo(x, y);
                    } else {
                      canvasCtx.lineTo(x, y);
                    }
          
                    x += sliceWidth;
                  }
          
                  canvasCtx.lineTo(canvas.width, canvas.height/2);
                  canvasCtx.stroke();
                };
          
                draw();
          
              } else if(visualSetting == "frequencybars") {
                analyser.fftSize = 64;
                var bufferLengthAlt = analyser.frequencyBinCount;
                console.log(bufferLengthAlt);
                var dataArrayAlt = new Uint8Array(bufferLengthAlt);
          
                canvasCtx.clearRect(0, 0, WIDTH, HEIGHT);
          
                var drawAlt = function() {
                  drawVisual = requestAnimationFrame(drawAlt);
          
                  analyser.getByteFrequencyData(dataArrayAlt);
          
                  canvasCtx.fillStyle = 'rgb(0, 0, 0)';
                  canvasCtx.fillRect(0, 0, WIDTH, HEIGHT);
          
                  var barWidth = (WIDTH / bufferLengthAlt);
                  var barHeight;
                  var x = 0;
          
                  for(var i = 0; i < bufferLengthAlt; i++) {
                    barHeight = dataArrayAlt[i];
          
                    canvasCtx.fillStyle = 'rgb(' + (barHeight+100) + ',50,50)';
                    canvasCtx.fillRect(x,HEIGHT-barHeight/2,barWidth,barHeight/2);
          
                    x += barWidth + 1;
                  }
                };
          
                drawAlt();
          
              } else if(visualSetting == "circle") {
                analyser.fftSize = 32;
                let bufferLength = analyser.frequencyBinCount;
                console.log(bufferLength);
                let dataArray = new Uint8Array(bufferLength);
          
                canvasCtx.clearRect(0, 0, WIDTH, HEIGHT);
                
                let draw = () => {
                  drawVisual = requestAnimationFrame(draw);
                  
                  analyser.getByteFrequencyData(dataArray);
                  canvasCtx.fillStyle = 'rgb(0, 0, 0)';
                  canvasCtx.fillRect(0, 0, WIDTH, HEIGHT);
                  
                  // let radius = dataArray.reduce((a,b) => a + b) / bufferLength;
                  let radius = dataArray[2] / 2
                  if (radius < 20) radius = 20;
                  if (radius > 100) radius = 100;
                  // console.log('Radius ', radius)
                  canvasCtx.beginPath();
                  canvasCtx.arc(CENTERX, CENTERY, radius, 0, 2 * Math.PI, false);
                  // canvasCtx.fillStyle = 'rgb(50,50,' + (radius+100) +')';
                  // canvasCtx.fill();
                  canvasCtx.lineWidth = 6;
                  canvasCtx.strokeStyle = 'rgb(50,50,' + (radius+100) +')';
                  canvasCtx.stroke();
                }
                draw()
              }
          
            }
            
            
            micSelect.onchange = async e => {
              console.log('now use device ', micSelect.value);
              stream.getTracks().forEach(function(track) {
                track.stop();
              });
              context.close();
              
              stream = await getStream({ audio: {
                deviceId: {exact: micSelect.value} }, video: false });
              setUpRecording();
            }
          
            function pause() {
              recording = false;
              context.suspend()
            }
          
            function resume() {
              recording = true;
              context.resume();
            }
          
            document.querySelector('#record').onclick = (e) => {
              console.log('Start recording')
            //   timedCount();
              $("#record").attr("disabled", true);
              start();
            }
          
            document.querySelector('#stop').onclick = (e) => {
                $("#record").attr("disabled", false);
              stop();
            }
          })()
          // par question time add
          */

    
    }


    function create_all_questions(questions)
    {
      console.log("questions create all quesiotns",questions)
      var choiceList = $(document).find(".Question_listing .choiceList");

      

      for(var i=0;i<questions.length;i++)
      {
        var display_tag = ""
        if(i!=0)
        {
          display_tag = "display:none"
        }
        console.log("i ",i)
        var question_id = questions[i]['dbid']
        console.log("--------question_id",question_id)
        var audio_show=`<div class="app question_box" id="question_box_`+question_id  +`" style=`+display_tag+`>
        

        <div class="audio-controls">
          
          <button id="start_recording`+question_id+`" onclick="start_recording(`+question_id+`)">Start Recording</button>
          <button id="stop_recording`+question_id+`" onclick="stop_recording(`+question_id+`)" disabled>Stop Recording</button>
          <button id="reset_recording`+question_id+`" onclick="reset_recording(`+question_id+`)" disabled>Reset Recording</button>
          <button id="preview_recording`+question_id+`" onclick="preview_recording(`+question_id+`)" disabled>Preview</button>

          <`+input_element+` id="`+input_element+question_id+`" controls class="video-js vjs-light-skin" ></`+input_element+`>
        </div>
      <div>`
        console.log("before append")
      $(audio_show).appendTo(choiceList);

        var start_button = document.querySelector("#start_recording"+question_id)
        var pause_button = document.querySelector("#pause_recording"+question_id)
        var stop_button = document.querySelector("#stop_recording"+question_id)
        var reset_button = document.querySelector("#reset_recording"+question_id)
        var preview_button = document.querySelector("#preview_recording"+question_id)

        console.log("start vuttoon",start_button)

       
      var player_tag = input_element + question_id
      console.log("player_tag",player_tag)
        var player = videojs(player_tag, options, function() {
            // print version information at startup
            var msg = 'Using video.js ' + videojs.VERSION +
                ' with videojs-record ' + videojs.getPluginVersion('record') +
                ', videojs-wavesurfer ' + videojs.getPluginVersion('wavesurfer') +
                ' and wavesurfer.js ' + WaveSurfer.VERSION;
            videojs.log(msg);

            
          
        });
        // all_players.push(player)
        all_players[question_id] = player
        console.log("after video js intialization",document.querySelector("audio"))

        c = seconds_get;
       
        // player.src({src: blobURL, type: blob.type});




      // active_player = player

      //  player.play()
        console.log("playerrrrrrrr",player)
        //active_player = player
        // start_button.onclick = function(){
        //     console.log("question_id",question_id)
        //     console.log("stop button ",start_button)
        //     $(start_button).prop('disabled', true);
        //     $(stop_button).prop('disabled', false);
        //     $(reset_button).prop('disabled', true);
        //     $(preview_button).prop('disabled', true);

        //     console.log("player record",player.record())
        //     player.record().start()
        //     //start_button.attr("disabled","disabled")

        // }

        // // pause_button.onclick = function(){
        // //     player.record().pause()
        // // }

        // stop_button.onclick = function(){
        //     $(stop_button).prop('disabled', true);
        //     $(reset_button).prop('disabled', false);
        //     $(preview_button).prop('disabled', false);
        //     player.record().stop()
        //     console.log("player.wavesurfer",player.wavesurfer())
        // }

        // reset_button.onclick = function(){
        //   $(start_button).prop('disabled', false);

        //   $(preview_button).prop('disabled', true);
        //     player.record().reset()
        //     player.record().getDevice()

        //     //  question_count = questions[currentQuestion].id;
        //     // console.log("question count",question_count )
        //     // $('#que-'+question_count).removeClass(['answer', 'skip']);

            
        // }

        // preview_button.onclick = function(){
        //     console.log("player record",player)
        //    //functionality unfinsihed
        //     //document.querySelector("audio").play()
        //     // player.record().pause()
        //     // document.querySelector("audio").play()
        //     $("button.vjs-paused").trigger("click")

          
        // }

        player.on('ready', function() {
          console.log("player read message",this.id())

          if(this.id() == input_element+"1")
          {
            this.record().getDevice()
          }
          if(input_element == "video")
          {
            $("wave").hide()
          }
          // 
          
            // if(audio_blobs[question_count-1] != null)
            // {
            //   console.log("==============",audio_blobs[question_count-1])
            //   console.log("audoio",window.URL.createObjectURL(audio_blobs[question_count-1]))
            //   console.log("audio blob",audio_blobs[question_count-1])
            //   // player.src({src:window.URL.createObjectURL(audio_blobs[question_count-1]),type:audio_blobs[question_count-1].type});
            //   // player.load();
            //   // player.play();

            //   // var audio_element = document.querySelector("audio")
            //   // console.log("audio  dynamic or not",audio_element)
            //   // audio_element.src = window.URL.createObjectURL(audio_blobs[question_count-1])
            //   // player.wavesurfer().surfer.pause();

            //   // var video = videojs("audio");
            //   // video.src(window.URL.createObjectURL(audio_blobs[question_count-1]));
            // }
            
            
           
           
          


        });
        // error handling for getUserMedia
        player.on('deviceError', function() {
            console.log('device error:', player.deviceErrorCode);
        });
        // Handle error events of the video player
        player.on('error', function(error) {
            console.log('error:', error);
        });
        // user clicked the record button and started recording !
        player.on('startRecord', function() {
            console.log('started recording! Do whatever you need to');
        });
        // user completed recording and stream is available
        // Upload the Blob to your server or download it locally !
        player.on('finishRecord', function() {
            // the blob object contains the recorded data that
            // can be downloaded by the user, stored on server etc.
            // var question_count = questions[currentQuestion].id;
            // var audioBlob = player.recordedData;
            // audio_blobs[question_count-1] = audioBlob
            // console.log("audio blobs",audio_blobs)
            // console.log('finished recording: ', audioBlob);

            
            // console.log("question count",question_count )

            if(input_element == "video")
            {
              
              console.log(" video data",this.recordedData)
              audio_blobs[currentQuestion] = this.recordedData
            }
            else{
              console.log("inside player",player)
              console.log("audio data",this.recordedData)
              audio_blobs[currentQuestion] = this.recordedData
          
            }
            // player.recordedData.video
            console.log("audio blobs",audio_blobs)
            // audio_blobs[currentQuestion] = player.record().recordedData


              // $('#que-'+).attr('class', 'answer'); // calender color changes
        });
      }
     console.log("all players created",all_players)
     var initial_player = all_players[questions[0].dbid]
    //  console.log("initla player",initial_player)
    //   if(input_element == "video")
    //   {
    //     initial_player.record().getDevice()
    //   }
    //   else
    //   {
    //     console.log("triggered")
    //     $(".vjs-icon-audio-perm").trigger("click")
    //   }
      
      active_player = initial_player
    }

function start_recording(question_id)
{  
  var player = all_players[question_id]

  console.log("All_players",all_players)
  console.log("current player",player)
  var start_button = document.querySelector("#start_recording"+question_id)
  var pause_button = document.querySelector("#pause_recording"+question_id)
  var stop_button = document.querySelector("#stop_recording"+question_id)
  var reset_button = document.querySelector("#reset_recording"+question_id)
  var preview_button = document.querySelector("#preview_recording"+question_id)

  $(".btn_next").prop('disabled', true);
  $(".btn_prev").prop('disabled', true);
  console.log("question_id",question_id)
  console.log("stop button ",start_button)
  $(start_button).prop('disabled', true);
  $(stop_button).prop('disabled', false);
  $(reset_button).prop('disabled', true);
  $(preview_button).prop('disabled', true);

  console.log("player record",player.record())
  player.record().start()
}

function stop_recording(question_id)
{
  var player = all_players[question_id]
  console.log("player",player)
  var start_button = document.querySelector("#start_recording"+question_id)
  var pause_button = document.querySelector("#pause_recording"+question_id)
  var stop_button = document.querySelector("#stop_recording"+question_id)
  var reset_button = document.querySelector("#reset_recording"+question_id)
  var preview_button = document.querySelector("#preview_recording"+question_id)

  $(stop_button).prop('disabled', true);
  $(reset_button).prop('disabled', false);
  $(preview_button).prop('disabled', false);
  player.record().stop()

  $(".btn_next").prop('disabled', false);
  $(".btn_prev").prop('disabled', false);


  // if(input_element == "video")
  // {
    
  //   console.log(" video data",player.recordedData.video)
  //   audio_blobs[currentQuestion] = player.recordedData.video
  // }
  // else{
  //   console.log("inside player",player)
  //   console.log("audio data",player.recordedData)
  //   audio_blobs[currentQuestion] = player.recordedData

  // }
  // player.recordedData.video
  audio_blobs[currentQuestion] = player.record().recordedData
  console.log("player.wavesurfer",player.wavesurfer())
}

function reset_recording(question_id)
{
  var player = all_players[question_id]
  var start_button = document.querySelector("#start_recording"+question_id)
  var pause_button = document.querySelector("#pause_recording"+question_id)
  var stop_button = document.querySelector("#stop_recording"+question_id)
  var reset_button = document.querySelector("#reset_recording"+question_id)
  var preview_button = document.querySelector("#preview_recording"+question_id)

  $(start_button).prop('disabled', false);

  $(preview_button).prop('disabled', true);
    player.record().reset()
    player.record().getDevice()
    // player.wavesurfer().pause();
    //  question_count = questions[currentQuestion].id;
    // console.log("question count",question_count )
    // $('#que-'+question_count).removeClass(['answer', 'skip']);

    
}

function preview_recording(question_id)
{
  var player = all_players[question_id]
  var start_button = document.querySelector("#start_recording"+question_id)
  var pause_button = document.querySelector("#pause_recording"+question_id)
  var stop_button = document.querySelector("#stop_recording"+question_id)
  var reset_button = document.querySelector("#reset_recording"+question_id)
  var preview_button = document.querySelector("#preview_recording"+question_id)

  console.log("player record",player)
  //functionality unfinsihed
   //document.querySelector("audio").play()
   // player.record().pause()
   // document.querySelector("audio").play()
   $("button.vjs-paused").eq(currentQuestion).trigger("click")
}

function displayQuestion(question_box_index)
{ 
  console.log("quesiton box index",question_box_index)
  $(".question_box").hide()
  $("#question_box_"+question_box_index).show()
}