$(document).ready(function(){

    $(document).on('click','.edit-btn',function(){
        $('.catid').val($(this).data('id'));
        $('.edit_category_name').val($(this).data('name'));
        $("#Edit_subject_modal").modal("show");
    });

    $('#edit-sub-form').on('submit',function(e){
        e.preventDefault();
        var updatecategory={'cat_id':$('.catid').val(),'cat_name':$('.edit_category_name').val()}
        console.log('update sub', updatecategory)
        if(updatecategory){
            $.ajax({
                url:"/company/coding_update_category/",
                headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
                type:'POST',
                contentType: 'application/json; charset=UTF-8',
                data: JSON.stringify(updatecategory),
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
        var deletecategory={'category_id':$(this).closest('.descriptive_questions').find('[name="card-id"]').val()}
        console.log('deletesubject', deletecategory)
        var subject_card = $(this).closest('.sub-card');
        swal({
            title: "Are you sure?",
            text: "You will not be able to recover deleted category!",
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
                    url:"/company/coding_delete_category/",
                    headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
                    type:'POST',
                    contentType: 'application/json; charset=UTF-8',
                    data: JSON.stringify(deletecategory),
                    error: function (request, status, error) {
                          alert(error);
                    }
                }).done(function(response){
                    if(response == 'True'){
                        swal("Deleted!", "Your category has been deleted.", "success");
                        subject_card.remove();
                    }else{
                        swal("Error!", "Something Wrong !!", "error");
                    }
                });
            } else {
                swal("Cancelled", "Your category is safe :)", "error");
            }
        });
    })

    $('#add-sub-form').on('submit',async function(e){
        e.preventDefault();
        $('.no-data').remove();
        var edit=editsub();
        var delete_=deletesub();
        var category_name = $('#category_name').val();
        var sub_id = $('#sub_id').val();
        var add_data={'category_name':category_name,'sub_id':sub_id};
        createSubId=JSON.parse(await add_sub(add_data))
        var url = "/company/coding_question_view/" + createSubId['category_id'];
        var tabClone = `<div class="col-12 col-sm-6 col-md-12 col-lg-6 col-xl-3 sub-card">
									<div class="descriptive_questions">
										<a href="`+ url +`" target="_blank">
											<div class="questions_details_text">`+createSubId['category_name']+`</div>
											<div class="descriptive_questions_no">
												<div class="descriptive_question_heading">
                                                    <input type="text" name="card-id" value="`+createSubId['category_id']+`" hidden readonly>
													<div class="cardtitle">Total Question :</div>
													<span>0</span>
												</div>
											</div>
										</a>
										<div class="descriptive_questions_action">`
										if(edit=='True'){
											tabClone+=`<a class="edit-btn" data-id="`+createSubId['category_id']+`"  data-name="`+createSubId['category_name']+`"><i class="fas fa-edit"></i></a>`
										}
										if(delete_=='True'){
											tabClone+=`<a class="delete-btn"><i class="fas fa-trash-alt"></i></a>`
										}
										tabClone+=`</div>
									</div>
								</div>`;
        $('.sub-container').append(tabClone);
        $('#Add_subject_modal').modal('hide');
    })

async function add_sub(add_data){
        var return_data = await $.ajax({
            url:"/company/coding_add_category/",
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

