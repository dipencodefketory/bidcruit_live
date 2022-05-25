$(document).ready(function(){
    $('.form-type-btn').on('click',function(){
       $('.btn-check').prop('checked', false);
       $(this).find('input[type=radio]').prop('checked', true);
       var pageName = $(this).data('item');
        if(pageName=='signup-freelancer'){
            document.location.href ="/agency/signup_freelancer/"     
        }
        else if(pageName=='signup-agency'){
            document.location.href ="/agency/signup_agency/"     
        }
    })
})