$(function() {
    $(document).on('click', '.btn-toggle-open', function(){
        console.log('1111111111111111111')
        var dropDown = $(this).closest('.acc__card').find('.open-custom-form');
        $(this).closest('.acc').find('.open-custom-form').not(dropDown).slideUp();

        if ($(this).hasClass('active')) {
          $(this).removeClass('active');
        } else {
          $(this).closest('.acc').find('.btn-toggle-open .active').removeClass('active');
          $(this).addClass('active');
        }

        dropDown.stop(false, true).slideToggle();
        // j.preventDefault();
    });

 
});