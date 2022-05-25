$(document).ready(function(){
    
    $(document).on('click','.edit-btn',function(){
        $('.subid').val($(this).data('id'));
        $('.edit_subject_name').val($(this).data('name'));
        $("#Edit_subject_modal").modal("show");
    });
    
    $('#edit-sub-form').on('submit',function(e){
        e.preventDefault();
        var updatesubject={'sub_id':$('.subid').val(),'sub_name':$('.edit_subject_name').val()}
        console.log('update sub', updatesubject)
        if(updatesubject){
            $.ajax({
                url:"/company/update_subject/",
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
        var deletesubject={'sub_id':$(this).closest('.fx-mini-card').find('[name="card-id"]').val()}
        var subject_card = $(this).closest('.fx-mini-card');
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
                    url:"/company/delete_subject/",
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
        var sub_name = $('#subject_name').val();
        var add_data={'subject_name':sub_name};
        createSubId=JSON.parse(await add_sub(add_data))
        console.log('createSubId>>>',createSubId)
        var url = "/company/preview_paragraph/" + createSubId['subject_id'];
        var tabClone = `<div class="fx-mini-card card">
                            <a href="`+ url +`" target="_blank">
                                <div class="fx-col title-field">
                                    <input type="text" name="card-id" value="`+createSubId['subject_id']+`" hidden readonly>    
                                    <input type="text" name="card-title" value="`+createSubId['subject_name']+`" class="text-capitalize form-control form-control-sm disabledEditText" placeholder="add subject title" readonly>
                                </div>
                                <div class="fx-col bind-sm-row">
                                    <div class="fx-left">
                                        <label class="tq-title text-capitalize">total question</label>
                                        <label class="tq-count">0</label>
                                    </div>
                                </div>
                            </a>
                            <div class="fx-right">
                                <div class="edit-btn" data-id="`+createSubId['subject_id']+`" data-name="`+createSubId['subject_name']+`"><i class="fas fa-edit"></i></div>
                                <div class="delete-btn"><i class="fas fa-trash-alt"></i></div>
                            </div>
                        </div>`;
        $('.grid-card-layout').append(tabClone);
        $('#Add_subject_modal').modal('hide');
    })

async function add_sub(add_data){
        var return_data = await $.ajax({
            url:"/company/add_subject/",
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

