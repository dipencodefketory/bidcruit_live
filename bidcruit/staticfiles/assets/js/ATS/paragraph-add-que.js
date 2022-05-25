$(function(){

tinymce.init({
    selector: 'textarea#edit-textarea',
    menubar: false,
    plugins: 'lists advlist',
    toolbar: 'bullist numlist bold',
    branding: 'False'
});
   
    $('#addMoreQueList').on('click',function(){ // add new clone of question
    var questionCount = $(document).find('.question-container .showOption-layout').length;
    var printCountOfQuoteNum = ''
    if(questionCount == 0){ printCountOfQuoteNum = 1;}else{ printCountOfQuoteNum = parseInt(questionCount) + 1;}
    var queFormClone = `<div class="showOption-layout">
                            <div class="que-head-section">
                                <div class="count-que_lable">
                                    <label class="text-capitalize">Que.</label>
                                    <input type="text" class="required form-control form-control-sm quote-text h6" name="pq-quote-label" value="">
                                </div>
                            </div>
                            <div class="group-opt grid-view">
                                <div class="grid-col">
                                    <div class="fx-col-sm">
                                        <div class="top-row">
                                            <input type="radio" name="inlineRadioOptionsSelect-`+printCountOfQuoteNum+`" class="form-control-sm" value="a" checked>
                                            <label class="smp-opt-num text-uppercase" for="inlineRadioBtn1">a</label>
                                        </div>
                                        <div class="bottom-row">
                                            <input type="text" class="required form-control form-control-sm opt-input-text" name="opt-input-1" value="">
                                        </div>
                                    </div>
                                </div>
                                <div class="grid-col">
                                    <div class="fx-col-sm">
                                        <div class="top-row">
                                            <input type="radio" name="inlineRadioOptionsSelect-`+printCountOfQuoteNum+`" class="form-control-sm" value="b">
                                            <label class="smp-opt-num text-uppercase" for="inlineRadioBtn2">b</label> 
                                        </div>
                                        <div class="bottom-row">
                                            <input type="text" class="required form-control form-control-sm opt-input-text" name="opt-input-2" value="">
                                        </div>
                                    </div>
                                </div>
                                <div class="grid-col">
                                    <div class="fx-col-sm">
                                        <div class="top-row">
                                            <input type="radio" name="inlineRadioOptionsSelect-`+printCountOfQuoteNum+`" class="form-control-sm"  value="c">
                                            <label class="smp-opt-num text-uppercase" for="inlineRadioBtn3">c</label>
                                        </div>
                                        <div class="bottom-row">
                                            <input type="text" class="required form-control form-control-sm opt-input-text" name="opt-input-3" value="">
                                        </div>
                                    </div>
                                </div>
                                <div class="grid-col">
                                    <div class="fx-col-sm">
                                        <div class="top-row">
                                            <input type="radio" name="inlineRadioOptionsSelect-`+printCountOfQuoteNum+`" class="form-control-sm" value="d">
                                            <label class="smp-opt-num text-uppercase" for="inlineRadioBtn4">d</label>
                                        </div>
                                        <div class="bottom-row">
                                            <input type="text" class="required form-control form-control-sm opt-input-text" name="opt-input-4" value="">
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="delete-quote mg-t-10 mg-b-10">
                                <button class="que-delete-btn btn-sm btn btn-danger text-capitalize">
                                    <i class="fas fa-trash-alt"></i>delete
                                </button>
                            </div>
                        </div>`;
        $('.question-container').append(queFormClone);       
    })

$(document).on('click','.que-delete-btn',function(){ //delete question 
    $(this).closest('.showOption-layout').remove();
})

// $("#savePageBtn").on('click',function(){
//     // $(document).find('#paraQuesForm').validate();
// })
// $('#saveAndNewaddBtn').on('click',function(){
//     $(document).find('#paraQuesForm').validate();
//     var questionCount = $(document).find('.question-container .showOption-layout').length;
//     console.log($(document).find("input[type='text'][name='pq-quote-label']"));
//     for (var i = 1; i < questionCount; i++) {
//         console.log($(document).find("input[type='text'][name='pq-quote-label']"));
//         console.log($(document).find("input[type='text'][name='pq-quote-label']"));
//         console.log($(document).find("input[type='text'][name='pq-quote-label']"));
//         console.log($(document).find("input[type='text'][name='pq-quote-label']"));
//         console.log($(document).find("input[type='text'][name='pq-quote-label']"))
//     }
// })

  })
