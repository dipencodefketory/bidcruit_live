function show_detail(taskid){
    $('#taskManagerModal').html('');
    var a='';
    $.ajax({
        type:"POST",
        headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
        url:"/company/gettask/",
        data:{"task_id":taskid,'tasktype':'taskget'},
    }).done(function(response){
        if(response['status']==true){
        a=`<div class="modal-dialog modal-lg task_details_view" role="document">
        <div class="modal-content modal-content-demo">
            <div class="modal-header">
                <div class="pophead">
                    <h6 class="modal-title">`+response['title']+`</h6>
                    <div class="right-ele">
                        <div class="pop-type"><label class="task-batch" style="color:`+response['category_color']+`;background: `+response['category_color']+`33;">`+response['category']+`</label></div>
                        <div class="pop-selector">
                            <form>
                                <input class="btn_re_m_task" type="submit" name="" value="Submit">
                            </form>
                        </div>
                    </div>
                </div>
                
                <button aria-label="Close" class="close" data-dismiss="modal" type="button"><span aria-hidden="true">&times;</span></button>
            </div>
            <div class="modal-body">
                <div class="row row-sm upper-set mb-2">
                    <div class="col-12 fxd-sm">
                        <div class="fx-label font_w_b">Assignee : <span class="assignee_user_n">`+response['assignee']+`</span></div>
                    </div>
                </div>
                <div class="row row-sm upper-set">
                    <div class="col-3 fxd-sm">
                        <div class="fx-label font_w_b">Jobs :</div>
                        <div class="fx-info-lable" style="color: #0068FF;">`+response['job']+`</div>
                    </div>`
                        if(response['applied_candidate']!=null){
                                a+=`<div class="col-3">
                                    <div class="fx-label">Candidate :</div>
                                    <div class="fx-info-lable" style="color: #0068ff;font-width:bold;">`+response['applied_candidate']+`</div>
                                </div>`
                        }
                        if(response['internal_candidate']!=null){
                            a+=`<div class="col-3">
                                <div class="fx-label">Candidate :</div>
                                <div class="fx-info-lable" style="color: #0068ff;font-width:bold;">`+response['internal_candidate']+`</div>
                            </div>`
                        }
                                a+=`<div class="col-3">
                                    <div class="fx-label">Due Date :</div>
                                    <div class="fx-info-lable">`+response['due_date']+`</div>
                                </div>
                                <div class="col-3">
                                    <div class="fx-label">Priority :</div>
                                    <div class="fx-info-lable">`+response['priority']+`</div>
                                </div>
                            </div>
                            <div class="row row-sm lower-set">
                                <div class="col-12">
                                    <h6>Task Description:</h6>
                                    <p>`+response['description']+`</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>`
        }
        else{
            a='Wrong data'
        }
        $('#taskManagerModal').append(a);
        $('#taskManagerModal').modal('show');
    })
    
};

function edit_detail(taskid){
    $.ajax({
        type:"POST",
        headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
        url:"/company/gettask/",
        data:{"task_id":taskid,'tasktype':'taskedit'},
    }).done(function(response){
        console.log(response)
        if(response['status']==true){
                        var editFormData = response;
                        $('#task_id').val(editFormData.taskid)
                        //$("#editTaskManager-form").reset();
                        var editName = $('.task-editname');
                        var editTaskDesc = $('.task-edit-description');
                        var editCate = $('.task-edit-cat > option');
                        var editJob = $('.task-edit-job > option');
                        var editCandidate = $('.task-edit-candidate > option');
                        var editOwner = $('.task-edit-owner > option');
                        var editAssign = $('.task-edit-assign > option');
                        var editDueDate = $('#editTaskDate');
                        var editStatus = $('.task-edit-status > option')

                        editName.val(editFormData.title);
                        
                        
                        // $("input:radio[name='select_priority'][value='"+ editFormData.priority +"']")[0].checked = true
                        $("input:radio[name='select_priority'][value='"+ editFormData.priority +"']").prop('checked', true);
                        editTaskDesc.val(editFormData.description);
                        editCate.each(function(){
                            getCatVal = $(this).val();
                            if(getCatVal == editFormData.category){
                            $(this).prop('selected',true)
                            }
                        })
                        editJob.each(function(){
                        getJobVal = $(this).val();
                        if(getJobVal == editFormData.job){
                            $(this).prop('selected',true)
                        }
                    })
                    if(editFormData.candidates!=null){
                    $('.task-edit-candidate').html('')
                        for (var i=0; i<editFormData.candidates.length; i++) {
                            $('.task-edit-candidate').append('<option value="'+editFormData.candidates[i].id+'">'+editFormData.candidates[i].name+ '</option>');
                        }
                    }
                    editCandidate.each(function(){
                        getCandidateVal = $(this).val();
                        if(getCandidateVal == editFormData.candidate){
                            $(this).prop('selected',true)
                        }
                    })
                    editOwner.each(function(){
                        getOwnerVal = $(this).val();
                        if(getOwnerVal == editFormData.owner){
                            $(this).prop('selected',true)
                        }
                    })
                    $(".task-edit-assign").val(editFormData.assignee).change();
                    $(".txtDate_target_Date").val(editFormData.due_date);
                   
                  
                        $("#editTaskManager").modal('show');
                }
            })
    }
$(document).ready(function(){
   $('.delete-btn').on('click',function(){
       //ajax requrest
       $(this).closest('.task-list').remove();
   })

//    $(document).on('focus','.txtDate_target_Date',function(){
//     $(this).datepicker({
//         showOtherMonths: true,
//         selectOtherMonths: true,
//         minDate: 0,
//     });
//    })


var dtToday = new Date();
var month = dtToday.getMonth() + 1;
var day = dtToday.getDate();
var year = dtToday.getFullYear();
if(month < 10)
    month = '0' + month.toString();
if(day < 10)
    day = '0' + day.toString();
var minDate= year + '-' + month + '-' + day;
$('.txtDate_target_Date').attr('min', minDate);


})
$(window).ready(function(){
    $('.select2').select2({
        tags: true
    });
})


$('.job').change(function(){
    console.log($(this).val())
    $.ajax({
        type:"POST",
        headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
        url:"/company/get_applied_candidate/",
        data:{'job_id':$(this).val()},
    }).done(function(response){
        response=JSON.parse(response)
        $('.candidate').html('')
        // $.each(response, function( key, value ) {
        //     console.log(key,value)
        //     // 
        //   })
        console.log(response.length)
        for (var i=0; i<response.length; i++) {
            console.log(response[i].id)
            $('.candidate').append('<option value="'+response[i].id+'">'+response[i].name+ '</option>');
        }
    })

})