$(document).ready(function(){

    $(document).on('click','.edit-btn',function(){

    });

    $(document).on('click','.questions_trash',function(){
        var q_id=$(this).attr('id')
        q_id={'question_id':q_id.split("-")[1]};
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
                    url:"/agency/mcq_delete_question/",
                    headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
                    type:'POST',
                    contentType: 'application/json; charset=UTF-8',
                    data: JSON.stringify(q_id),
                    error: function (request, status, error) {
                          alert(error);
                    }
                }).done(function(response){
                    if(response == 'True'){
                        swal("Deleted!", "Your Question has been deleted.", "success");
                    }else{
                        swal("Error!", "Something Wrong !!", "error");
                    }
                });
            } else {
                swal("Cancelled", "Your Question is safe :)", "error");
            }
        });

});

});