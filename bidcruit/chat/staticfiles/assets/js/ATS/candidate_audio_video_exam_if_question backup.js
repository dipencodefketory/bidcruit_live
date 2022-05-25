
    var questions ='';  

   	
    var currentQuestion = 0;
    var viewingAns = 0;
    var correctAnswers = 0;
    var quizOver = false;
    var iSelectedAnswer = [];
  
    var seconds_get =200;

    var total_exam_time = get_total_exam_time();//it is in hh mm formata
    console.log("total exam time",total_exam_time   )
    var elapsed_time = get_elapsed_time()

    

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
    $(document).ready(function () 
    {
        // var c=200;

        var b = parseInt(elapsed_hours)*3600 + parseInt(elapsed_minutes)*60 +elapsed_seconds
        var c = parseInt(total_exam_time_hours)*3600 + parseInt(total_exam_time_minutes)*60 +total_exam_time_seconds
        console.log("cccc",c)
        console.log("bbbb",b)
        c=c-b
        console.log("thev value of c is ",c)

        questions = get_mcqData();
        // populate question no list
        var total_question = questions.length;

        for(var i=1; i<=total_question;i++){
            $('<li id="que-'+i+'" class="notvisited">'+i+'</li>').appendTo($('.question-no-list'));
        }

        

        displayCurrentQuestion();
        
        // Display the thime	
        console.log("before timed count")			
        timedCount(c)
                    
       
        
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
                    $.ajax({
                        url:"/candidate/audio_exam_fill/"+temp_id+"/"+job_id,
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
                        last=JSON.parse(response['last'])

                        if(last == true){
//                                url=JSON.parse(response['url'])
//                                console.log(response['url'])
                            window.location.href='http://'+response['url']
                        }
                   });

               
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
        console.log("hours",hours)
        var minutes = parseInt( c / 60 ) % 60;
        console.log("minutes",minutes)
        var seconds = c % 60;
        console.log("seconds",seconds)
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
        audio_show=`<div class="app">
        <select name="" id="micSelect"></select>
      
        <div class="audio-controls">
          <button id="record">Record</button>
          <button id="stop">Stop</button>
          <audio id="audio" controls></audio>
        </div>
    
        <canvas width="500" height="300"></canvas>
      <div>`;
        $(audio_show).appendTo(choiceList);
			
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
        c = seconds_get;  // par question time add

    }
