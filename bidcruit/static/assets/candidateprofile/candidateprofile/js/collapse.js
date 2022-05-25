// Accordion all expand and callpase

$(document).ready(function () {

  $(".toggle-accordion").on("click", function () {
    var accordionId = $(this).attr("accordion-id"),
      numPanelOpen = $(accordionId + ' .collapse.show').length;

    $(this).toggleClass("active");

    if (numPanelOpen == 0) {
      openAllPanels(accordionId);
    } else {
      closeAllPanels(accordionId);
    }
  })
  openAllPanels = function (aId) {
    console.log("setAllPanelOpen");
    $(aId + ' .panel-collapse:not(".show")').addClass('show').animate({duration:500});
  }
  closeAllPanels = function (aId) {
    console.log("setAllPanelclose");
    $(aId + ' .panel-collapse.show').removeClass('show').animate({duration:500});
  }
  /////open and close timeline
  $("#right-side").hover(function () {
    $(".custome-callpase").addClass("main");
  });
  $(document).on("click", function (e) {
    if ($(e.target).is("#user-login-wrapper") === false) {
      $(".custome-callpase").removeClass("main");
    }
  });

//on click smooth scroll to the section

$('.small-circle').find('a[href^="#"]').on('click', function (e) {
  e.preventDefault();
  var target = this.hash;
  var $target = $(target);
  $target.addClass('flash');
  $('html, body').stop().animate({
    'scrollTop': $target.offset().top + -80
  }, 900, 'swing', function () {
    // window.location.hash = target;
  });
});

});

//sidebar fixed on page scroll
$(function () {
  var top = $('#right-side').offset().top - parseFloat($('#right-side').css('marginTop').replace(/auto/, 0));
  var footTop = $('#footer').offset().top - parseFloat($('#footer').css('marginTop').replace(/auto/, 0));

  var maxY = footTop - $('#right-side').outerHeight();

  $(window).scroll(function (evt) {
    var y = $(this).scrollTop();
    if (y >= top - $('#header').height()) {
      if (y < maxY) {

      } else {
        $('#right-side').addClass("fixed")
      }
    } else {
      $('#right-side').removeClass("fixed");
    }
  });
 
});



// When click on accordian scrool
jQuery( document ).ready( function( $ ) {
  $('a[data-toggle="collapse"]').click( function( ) {
  
  setTimeout(function(){
   var $panel = $('.panel-collapse').closest('.panel');
      $('html,body').animate({
          scrollTop: $panel.offset().top - 100
      }, 700); 
  }, 700 );
  });
  });
