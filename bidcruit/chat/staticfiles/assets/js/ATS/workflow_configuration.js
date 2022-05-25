$(document).ready(function(){
//console.log('workflow page loaded...');
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
})


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
    