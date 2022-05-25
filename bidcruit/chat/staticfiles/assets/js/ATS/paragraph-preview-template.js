$(function(){
    $('.upload-action').on('click',function(){ //file upload funtion
        //add code
    })

    $('.print-action').on('click',function(){ //print funtion
        //add code
    })

    $('.mini-nav').on('click',function(){ //show navigation funtion
        //add code
    })


    $(document).on('click','.slide-tab-btn',function(){
        currentListEle = $(this);
        if(currentListEle.closest('.slide-list').find('.detail-section').is(":visible")){
            console.log('true')
            $('.short-details').show();
            $('.detail-section').slideUp();
            currentListEle.closest('.title-section').find('.short-details').show('fast');
            currentListEle.closest('.slide-list').find('.detail-section').slideUp();
        }else{
            console.log('false')
            $('.short-details').show();
            $('.detail-section').slideUp();
            currentListEle.closest('.title-section').find('.short-details').hide('fast');
            currentListEle.closest('.slide-list').find('.detail-section').slideDown();
        }
    })
    $(document).on('click','.delete-btn',function(){ //remove list
        var div_to_del = $(this).closest('.slide-list')
        var deletepara={'para_id':$(this).closest('.slide-list').find('[name="para-id"]').val()}
        console.log('deletepara',deletepara)
        // var deletesubject={'sub_id':$(this).closest('.fx-mini-card').find('[name="card-id"]').val()}
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
                    div_to_del.remove()
                    $.ajax({
                        url:"/company/delete_paragraph/",
                        headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
                        type:'POST',
                        contentType: 'application/json; charset=UTF-8',
                        data: JSON.stringify(deletepara),
                        error: function (request, status, error) {
                            alert(error);
                        }
                    }).done(function(response){
                        if(response == 'True'){
                            swal("Deleted!", "Your paragraph has been deleted.", "success");
                            div_to_del.remove();
                        }else{
                            swal("Error!", "Something Wrong !!", "error");
                        }
                    });
            } else {
                swal("Cancelled", "Your paragraph is safe :)", "error");
            }
        });
        
    })
})