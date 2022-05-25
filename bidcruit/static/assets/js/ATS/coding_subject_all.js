$(document).ready(function(){

    $(document).on('click','.edit-btn',function(){
        $('.subid').val($(this).data('id'));
//        $('.edit_subject_name').val($(this).data('name'));
        $("#Edit_subject_modal").modal("show");
    });

    $(document).on('click','input[name=subjecttype]',function(){
       let flag = $(this).val();
       if(flag == 'frontend'){
            $('.backend-subject').css('display','none');
            $('.frontend-subject').css('display','block');
       }
       if(flag == 'backend'){
            $('.frontend-subject').css('display','none');
            $('.backend-subject').css('display','block');
       }
    });

    $('#edit-sub-form').on('submit',function(e){
        e.preventDefault();
        var updatesubject={'sub_id':$('.subid').val(),'api_sub_id':$('.edit_subject_name').val()}
        console.log('update sub', updatesubject)
        if(updatesubject){
            $.ajax({
                url:"/company/coding_update_subject/",
                headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
                type:'POST',
                contentType: 'application/json; charset=UTF-8',
                data: JSON.stringify(updatesubject),
                error: function (request, status, error) {
                    alert(error);
                }
            }).done(function(response){
                if(response=="True"){
                    $("#Edit_subject_modal").modal("hide");
                    window.location.reload();
                }
                else{
                    alert('Something went wrong !');
                    $("#Edit_subject_modal").modal("hide");
                }
            });
        }
    })
    $(document).on('click','.delete-btn',function(){
        var deletesubject={'sub_id':$(this).closest('.descriptive_questions').find('[name="card-id"]').val()}
        console.log('deletesubject', deletesubject)
        var subject_card = $(this).closest('.sub-card');
        swal({
            title: "Are you sure?",
            text: "You will not be able to recover deleted subjects!",
            type: "warning",
            showCancelButton: true,
            confirmButtonClass: "btn-danger",
            confirmButtonText: "Yes, delete it!",
            cancelButtonText: "Cancel",
            closeOnConfirm: false,
            closeOnCancel: false
        },function(isConfirm) { //send ajax request for detele category action
            if (isConfirm){
                $.ajax({
                    url:"/company/coding_delete_subject/",
                    headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
                    type:'POST',
                    contentType: 'application/json; charset=UTF-8',
                    data: JSON.stringify(deletesubject),
                    error: function (request, status, error) {
                          alert(error);
                    }
                }).done(function(response){
                    if(response == 'True'){
                        swal("Deleted!", "Your subject has been deleted.", "success");
                        subject_card.remove();
                    }else{
                        swal("Error!", "Something Wrong !!", "error");
                    }
                });
            } else {
                swal("Cancelled", "Your subject is safe :)", "error");
            }
        });
    })

    $('#add-sub-form').on('submit',async function(e){
        e.preventDefault();
        $('.no-data').remove();
        var edit=editsub();
        var delete_=deletesub();
        var sub_name = $('#subject_name').val();
        var type = $('input[name="subjecttype"]:checked').val();
        var add_data={'subject_id':sub_name,'type':type};
        createSubId=JSON.parse(await add_sub(add_data))
        var url = "/company/coding_category_all/" + createSubId['subject_id'];
        var buttons=`<div class="descriptive_questions_action">`
        if(type == 'backend'){
        if(edit=='True'){
            buttons += `<a class="edit-btn questions_edit" data-id="`+createSubId['subject_id']+`"  data-name="`+createSubId['subject_name']+`"><i class="fas fa-edit"></i></a>`
           }
        }else{
        if(delete_=='True'){
            buttons = `<a class="delete-btn questions_trash"><i class="fas fa-trash-alt"></i></a>`
            }
        }
        buttons+=`</div>`
        var tabClone = `<div class="col-12 col-sm-6 col-md-12 col-lg-6 col-xl-3 sub-card">
									<div class="descriptive_questions">
										<a href="`+ url +`" target="_blank">
											<div class="questions_details_text">`+createSubId['subject_name']+` <span>(`+createSubId['type']+`)</span></div>
											<div class="descriptive_questions_no">
												<div class="descriptive_question_heading">
                                                    <input type="text" name="card-id" value="`+createSubId['subject_id']+`" hidden readonly>
													<div class="cardtitle">Total Categories :</div>
													<span>0</span>
												</div>
											</div>
										</a>
										`+ buttons +`
									</div>
								</div>`;
        $('.sub-container').append(tabClone);
        $('#Add_subject_modal').modal('hide');
    })

async function add_sub(add_data){
        var return_data = await $.ajax({
            url:"/company/coding_add_subject/",
            headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
            type:'POST',
            contentType: 'application/json; charset=UTF-8',
            data: JSON.stringify(add_data),
            error: function (request, status, error) {
                    console.log(error);
            }
        }).done(function(response){

        });
        return return_data

    };
});

