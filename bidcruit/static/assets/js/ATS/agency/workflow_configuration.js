$(document).ready(function(){
    console.log('workflow page loaded...');
    appendSubmitActButton();
    $("#interviewerList").select2({
        closeOnSelect : false,
        placeholder : "Placeholder"
        // allowHtml: true,
        // allowClear: true,
        // tags: true
    });
    
    $("input[name='mcq-action']").change(function(){
        if($(this).val()=='manual'){
            $('#mcq').hide();
            $("#mcq").find('input').each(function( index ){
                $(this).removeAttr('required')
            })
            
        }
        else if($(this).val()=='auto'){
            $('#mcq').show();
            $("#mcq").find('input').each(function( index ){
                $(this).attr('required',true)
            })
        }
    })
    // image
    $("input[name='image-action']").change(function(){
        if($(this).val()=='manual'){
            $('#image').hide();
            $("#image").find('input').each(function( index ){
                $(this).removeAttr('required')
            })
            
        }
        else if($(this).val()=='auto'){
            $('#image').show();
            $("#image").find('input').each(function( index ){
                $(this).attr('required',true)
            })
        }
    })
    $("input[name='jcr-action']").change(function(){
        if($(this).val()=='manual'){
            $('#jcr').hide();
            $("#jcr").find('input').each(function( index ){
                $(this).removeAttr('required')
            })
            
        }
        else if($(this).val()=='auto'){
            $('#jcr').show();
            $("#jcr").find('input').each(function( index ){
                $(this).attr('required',true)
            })
        }
    })
    
    $(".nextBtn").on('click',function(){
        var TabId = $(this).parent().parent('.tab-pane');
        $('.tab-pane').removeClass('active');
        TabId.next().addClass('active')
        leftPanelTabAct()
    });
    $(".prevBtn").on('click',function(){
        var TabId = $(this).parent().parent('.tab-pane');
        $('.tab-pane').removeClass('active');
        TabId.prev().addClass('active')
        leftPanelTabActPrev()
    });
    
    
    $(".nextBtnWithValid").on('click',function(){ //MCQ and Image form Validation
        var testFormDomEle = $(this).parent().prev(".testFormContainer");
        if(testFormDomEle.find('.selectionInputs').is(":visible")){
            var totalMark = testFormDomEle.find('.grandMark').text();
            var shortInputVal = testFormDomEle.find('.selectionInputs .col-4:first-child input[type=number]').val();
            var rejectInputVal = testFormDomEle.find('.selectionInputs .col-4:last-child input[type=number]').val();
            if(shortInputVal == '' && rejectInputVal == '' ){
                testFormDomEle.find('.markValidMsg').html('');
                testFormDomEle.find('.markValidMsg').html('input value is required.'); 
                resetMsg();
            }else if(parseInt(shortInputVal) < parseInt(rejectInputVal) || parseInt(shortInputVal) == parseInt(rejectInputVal)){
                testFormDomEle.find('.markValidMsg').html('');
                testFormDomEle.find('.markValidMsg').html('Rejected Input value should be less than to Short List.');
                resetMsg();
            }else if(parseInt(totalMark) < parseInt(rejectInputVal) || parseInt(totalMark) == parseInt(rejectInputVal)){
                testFormDomEle.find('.markValidMsg').html('');
                testFormDomEle.find('.markValidMsg').html('Rejected List Input value must be less than to Total Mark.');
                resetMsg();
            }else if(parseInt(totalMark) < parseInt(shortInputVal)){
                testFormDomEle.find('.markValidMsg').html('');
                testFormDomEle.find('.markValidMsg').html('Short List Input value must be equaL or less than to Total Mark.');
                resetMsg();
            }else{
                testFormDomEle.find('.markValidMsg').html('');
                $('.tab-pane').removeClass('active');
                testFormDomEle.parent('.tab-pane').next().addClass('active');
                leftPanelTabAct();
            }
        }else{
            testFormDomEle.find('.markValidMsg').html('');
            $('.tab-pane').removeClass('active');
            testFormDomEle.parent('.tab-pane').next().addClass('active');
            leftPanelTabAct();
        }
        //parseInt(totalMark) < parseInt(shortInputVal) || parseInt(totalMark) < parseInt(rejectInputVal) || parseInt(totalMark) == parseInt(shortInputVal) || parseInt(totalMark) == parseInt(rejectInputVal
    })
    
    $(".checkpoint-input input[type=radio]").on('click',function(){
       var getValOfRadio =  $(this).val();
       if(getValOfRadio == 'manual'){
           $(this).closest('.testFormContainer').find('.selectionInputs input').attr('required',false);
           $(this).closest('.testFormContainer').find('.selectionInputs').hide();
       }
       if(getValOfRadio == 'auto'){
           $(this).closest('.testFormContainer').find('.selectionInputs input').attr('required',true);
           $(this).closest('.testFormContainer').find('.selectionInputs').show();
       }
    })
    
    })
    
    // $(window).ready(function(){
    //     $('.formWizardList .tab-pane:last-child').find('.nextBtn, .nextBtnWithValid').remove();
    // })
    function leftPanelTabActPrev(){
        $('.formWizardList .tab-pane').each(function(index){
            if($(this).hasClass('active')){
                var rewrdIndx = index == 0 ? 0 : index - 1;
                $(".wf-tabs-container li a").removeClass('active');
                $(document).find('.wf-tabs-container li').eq(rewrdIndx).find('a').addClass('active')
            }
        })
    }
    function leftPanelTabAct(){
        $('.formWizardList .tab-pane').each(function(index){
            if($(this).hasClass('active')){
                $(".wf-tabs-container li a").removeClass('active');
                $(document).find('.wf-tabs-container li').eq(index).find('a').addClass('active')
            }
        })
    }
    
    
    function appendSubmitActButton(){
        console.log('append submit button')
        var finishButtonVisible = "";
        finishButtonVisible += `<div class="col-12 footer_section">
                                    <div class="action_btn_section">
                                        <button class="btn btn-sm btn-primary" id="submit" type="button">Save &amp; Finish</button>
                                    </div>
                                </div>`; 
        $(".tab-content tab-pane:last-child row col-12:last-child").after(finishButtonVisible);
    }
    function resetMsg(){
        setTimeout(function(){
            $('.markValidMsg').html('');
        },2800)
    }
        