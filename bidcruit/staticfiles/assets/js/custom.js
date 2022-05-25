$(function() {
	'use strict'

	// ______________LOADER
	$("#global-loader").fadeOut("slow");


	// This template is mobile first so active menu in navbar
	// has submenu displayed by default but not in desktop
	// so the code below will hide the active menu if it's in desktop
	if (window.matchMedia('(min-width: 992px)').matches) {
		$('.main-navbar .active').removeClass('show');
		$('.main-header-menu .active').removeClass('show');
	}
	// Shows header dropdown while hiding others
	$('.main-header .dropdown > a').on('click', function(e) {
		e.preventDefault();
		$(this).parent().toggleClass('show');
		$(this).parent().siblings().removeClass('show');
		$(this).find('.drop-flag').removeClass('show');
	});

	// ______________Full screen
	$(document).on("click", ".fullscreen-button", function toggleFullScreen() {

		if ((document.fullScreenElement !== undefined && document.fullScreenElement === null) || (document.msFullscreenElement !== undefined && document.msFullscreenElement === null) || (document.mozFullScreen !== undefined && !document.mozFullScreen) || (document.webkitIsFullScreen !== undefined && !document.webkitIsFullScreen)) {
			$('body').addClass("fullscreen");
			if (document.documentElement.requestFullScreen) {
				document.documentElement.requestFullScreen();
			} else if (document.documentElement.mozRequestFullScreen) {
				document.documentElement.mozRequestFullScreen();
			} else if (document.documentElement.webkitRequestFullScreen) {
				document.documentElement.webkitRequestFullScreen(Element.ALLOW_KEYBOARD_INPUT);
			} else if (document.documentElement.msRequestFullscreen) {
				document.documentElement.msRequestFullscreen();
			}
		} else {
				$('body').removeClass("fullscreen");
			if (document.cancelFullScreen) {
				document.cancelFullScreen();
			} else if (document.mozCancelFullScreen) {
				document.mozCancelFullScreen();
			} else if (document.webkitCancelFullScreen) {
				document.webkitCancelFullScreen();
			} else if (document.msExitFullscreen) {
				document.msExitFullscreen();
			}
		}

	})

	// ______________ RATING STAR



	// ______________Cover Image
	$(".cover-image").each(function() {
		var attr = $(this).attr('data-image-src');
		if (typeof attr !== typeof undefined && attr !== false) {
			$(this).css('background', 'url(' + attr + ') center center');
		}
	});

	// ______________Search
	$('body, .main-header form[role="search"] button[type="reset"]').on('click keyup', function(event) {
		if (event.which == 27 && $('.main-header form[role="search"]').hasClass('active') ||
		$(event.currentTarget).attr('type') == 'reset') {
		closeSearch();
		}
	});
	function closeSearch() {
		var $form = $('.main-header form[role="search"].active')
		$form.find('input').val('');
		$form.removeClass('active');
	}
	// Show Search if form is not active // event.preventDefault() is important, this prevents the form from submitting
	$(document).on('click', '.main-header form[role="search"]:not(.active) button[type="submit"]', function(event) {
		event.preventDefault();
		var $form = $(this).closest('form'),
		$input = $form.find('input');
		$form.addClass('active');
		$input.focus();
	});
	// if your form is ajax remember to call `closeSearch()` to close the search container
	$(document).on('click', '.main-header form[role="search"].active button[type="submit"]', function(event) {
		event.preventDefault();
		var $form = $(this).closest('form'),
		$input = $form.find('input');
		$('#showSearchTerm').text($input.val());
		closeSearch()
	});



	/* ----------------------------------- */

	// Showing submenu in navbar while hiding previous open submenu
	$('.main-navbar .with-sub').on('click', function(e) {
		e.preventDefault();
		$(this).parent().toggleClass('show');
		$(this).parent().siblings().removeClass('show');
	});
	// this will hide dropdown menu from open in mobile
	$('.dropdown-menu .main-header-arrow').on('click', function(e) {
		e.preventDefault();
		$(this).closest('.dropdown').removeClass('show');
	});
	// this will show navbar in left for mobile only
	$('#mainNavShow, #azNavbarShow').on('click', function(e) {
		e.preventDefault();
		$('body').addClass('main-navbar-show');
	});
	// this will hide currently open content of page
	// only works for mobile
	$('#mainContentLeftShow').on('click touch', function(e) {
		e.preventDefault();
		$('body').addClass('main-content-left-show');
	});
	// This will hide left content from showing up in mobile only
	$('#mainContentLeftHide').on('click touch', function(e) {
		e.preventDefault();
		$('body').removeClass('main-content-left-show');
	});
	// this will hide content body from showing up in mobile only
	$('#mainContentBodyHide').on('click touch', function(e) {
		e.preventDefault();
		$('body').removeClass('main-content-body-show');
	})
	// navbar backdrop for mobile only
	$('body').append('<div class="main-navbar-backdrop"></div>');
	$('.main-navbar-backdrop').on('click touchstart', function() {
		$('body').removeClass('main-navbar-show');
	});
	// Close dropdown menu of header menu
	$(document).on('click touchstart', function(e) {
		e.stopPropagation();
		// closing of dropdown menu in header when clicking outside of it
		var dropTarg = $(e.target).closest('.main-header .dropdown').length;
		if (!dropTarg) {
			$('.main-header .dropdown').removeClass('show');
		}
		// closing nav sub menu of header when clicking outside of it
		if (window.matchMedia('(min-width: 992px)').matches) {
			// Navbar
			var navTarg = $(e.target).closest('.main-navbar .nav-item').length;
			if (!navTarg) {
				$('.main-navbar .show').removeClass('show');
			}
			// Header Menu
			var menuTarg = $(e.target).closest('.main-header-menu .nav-item').length;
			if (!menuTarg) {
				$('.main-header-menu .show').removeClass('show');
			}
			if ($(e.target).hasClass('main-menu-sub-mega')) {
				$('.main-header-menu .show').removeClass('show');
			}
		} else {
			//
			if (!$(e.target).closest('#mainMenuShow').length) {
				var hm = $(e.target).closest('.main-header-menu').length;
				if (!hm) {
					$('body').removeClass('main-header-menu-show');
				}
			}
		}
	});
	$('#mainMenuShow').on('click', function(e) {
		e.preventDefault();
		$('body').toggleClass('main-header-menu-show');
	})
	$('.main-header-menu .with-sub').on('click', function(e) {
		e.preventDefault();
		$(this).parent().toggleClass('show');
		$(this).parent().siblings().removeClass('show');
	})
	$('.main-header-menu-header .close').on('click', function(e) {
		e.preventDefault();
		$('body').removeClass('main-header-menu-show');
	})

	$(".card-header-right .card-option .fe fe-chevron-left").on("click", function() {
		var a = $(this);
		if (a.hasClass("icofont-simple-right")) {
			   a.parents(".card-option").animate({
				width: "35px",
			})
		} else {
		   a.parents(".card-option").animate({
			width: "180px",
			})
		}
		$(this).toggleClass("fe fe-chevron-right").fadeIn("slow")
	});

	 // ___________TOOLTIP
	$('[data-toggle="tooltip"]').tooltip();
	// colored tooltip
	$('[data-toggle="tooltip-primary"]').tooltip({
		template: '<div class="tooltip tooltip-primary" role="tooltip"><div class="arrow"><\/div><div class="tooltip-inner"><\/div><\/div>'
	});
	$('[data-toggle="tooltip-secondary"]').tooltip({
		template: '<div class="tooltip tooltip-secondary" role="tooltip"><div class="arrow"><\/div><div class="tooltip-inner"><\/div><\/div>'
	});

	// __________POPOVER
	$('[data-toggle="popover"]').popover();
	$('[data-popover-color="head-primary"]').popover({
		template: '<div class="popover popover-head-primary" role="tooltip"><div class="arrow"><\/div><h3 class="popover-header"><\/h3><div class="popover-body"><\/div><\/div>'
	});
	$('[data-popover-color="head-secondary"]').popover({
		template: '<div class="popover popover-head-secondary" role="tooltip"><div class="arrow"><\/div><h3 class="popover-header"><\/h3><div class="popover-body"><\/div><\/div>'
	});
	$('[data-popover-color="primary"]').popover({
		template: '<div class="popover popover-primary" role="tooltip"><div class="arrow"><\/div><h3 class="popover-header"><\/h3><div class="popover-body"><\/div><\/div>'
	});
	$('[data-popover-color="secondary"]').popover({
		template: '<div class="popover popover-secondary" role="tooltip"><div class="arrow"><\/div><h3 class="popover-header"><\/h3><div class="popover-body"><\/div><\/div>'
	});
	$(document).on('click', function(e) {
		$('[data-toggle="popover"],[data-original-title]').each(function() {
			//the 'is' for buttons that trigger popups
			//the 'has' for icons within a button that triggers a popup
			if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
				(($(this).popover('hide').data('bs.popover') || {}).inState || {}).click = false // fix for BS 3.3.6
			}
		});
	});



	// ______________Horizontal-menu Active Class
	$(document).ready(function() {
		$(".horizontalMenu-list li a").each(function() {
			var pageUrl = window.location.href.split(/[?#]/)[0];
			if (this.href == pageUrl) {
				$(this).addClass("active");
				$(this).parent().addClass("active"); // add active to li of the current link
				$(this).parent().parent().prev().addClass("active"); // add active class to an anchor
				$(this).parent().parent().prev().click(); // click the item to make it drop
			}
		});
	});


	// ______________Active Class
	$(document).ready(function() {
		$(".horizontalMenu-list li a").each(function() {
			var pageUrl = window.location.href.split(/[?#]/)[0];
			if (this.href == pageUrl) {
				$(this).addClass("active");
				$(this).parent().addClass("active"); // add active to li of the current link
				$(this).parent().parent().prev().addClass("active"); // add active class to an anchor
				$(this).parent().parent().prev().click(); // click the item to make it drop
			}
		});
		$(".horizontal-megamenu li a").each(function() {
			var pageUrl = window.location.href.split(/[?#]/)[0];
			if (this.href == pageUrl) {
				$(this).addClass("active");
				$(this).parent().addClass("active"); // add active to li of the current link
				$(this).parent().parent().parent().parent().parent().parent().parent().prev().addClass("active"); // add active class to an anchor
				$(this).parent().parent().prev().click(); // click the item to make it drop
			}
		});
		$(".horizontalMenu-list .sub-menu .sub-menu li a").each(function() {
			var pageUrl = window.location.href.split(/[?#]/)[0];
			if (this.href == pageUrl) {
				$(this).addClass("active");
				$(this).parent().addClass("active"); // add active to li of the current link
				$(this).parent().parent().parent().parent().prev().addClass("active"); // add active class to an anchor
				$(this).parent().parent().prev().click(); // click the item to make it drop
			}
		});
	});

	// ______________ Back to Top
	$(window).on("scroll", function(e) {
		if ($(this).scrollTop() > 0) {
			$('#back-to-top').fadeIn('slow');
		} else {
			$('#back-to-top').fadeOut('slow');
		}
	});
	$("#back-to-top").on("click", function(e) {
		$("html, body").animate({
			scrollTop: 0
		}, 600);
		return false;
	});

	// ______________ Header-Search
	$(document).ready(function(){
		var submitIcon = $('.search-icon');
		var searchBox = $('.input-search');
		var isOpen = false;
		submitIcon.click(function(){
			if(isOpen == false){
				searchBox.addClass('input-search-open');
				isOpen = true;
			} else {
				searchBox.removeClass('input-search-open');
				isOpen = false;
			}
        });

    });

	// ______________ Search
	$('.icon').click(function() {
		$('.search').toggleClass('expanded');
		$('.box').toggleClass('open');
	});

	// ______________Toast
	$(".toast").toast();



	// ______________Skins

	////////////////////////////////////////////////////
	/*  ############# Horizontal version ########*/
	//////////////////////////////////////////////////


	/* ###########  Horizontal color  ###########*/

	// $('body').addClass('horizontal-color'); //

	/* ###########  Horizontal dark  ###########*/

	// $('body').addClass('horizontal-dark'); //

	/* ###########  Horizontalmenu-white  ###########*/

	// $('body').addClass('horizontalmenu-white'); //


	////////////////////////////////////////////////////
	/*  ############# Leftmenu version ########*/
	//////////////////////////////////////////////////

	/* ###########  Firstmenu Dark  ###########*/

	// $('body').addClass('first-menu-dark'); //


	/* ########### Second-menu-dark  ###########*/

	//  $('body').addClass('second-menu-dark');  //


	/* ###########  Firstmenu White  ###########*/

	// $('body').addClass('firstmenu-white'); //



	////////////////////////////////////////////////////
	/*  ############# Single Leftmenu ########*/
	//////////////////////////////////////////////////

	/* ###########  Singlemenu color  ###########*/

	// $('body').addClass('singlemenu-color'); //


	/* ########### Singlemenu dark  ###########*/

	//  $('body').addClass('singlemenu-dark');  //


	/* ###########  Singlemenu White  ###########*/

	// $('body').addClass('singlemenu-white'); //


	////////////////////////////////////////////////////
	/*  ############# Body Style ########*/
	//////////////////////////////////////////////////


	/* ###########  Body Style  ###########*/

	// $('body').addClass('body-style'); //

	/*New js*/

// c


// check box content hide and show
$(document).ready(function(){
//    $(".answer").show();
   $(".coupon_question").click(function() {
        if($(this).is(":checked")) {
         $(".answer").hide();
        } else {
           $(".answer").show();
        }
   });
 });

//clone and remove section
//$(document).ready(function(){
//    $('.btn-primary').on('click', function(){
//        var $item = $(this).closest('.element').clone();
//        $item.find('.btn').removeClass('btn-primary').addClass('btn-danger');
//        $item.find('.btn').html('<span class="fas fa-times"></span> Remove');
//        $item.find('.btn').attr('onClick', '$(this).closest(".element").remove();');
//        $item.appendTo('.results');
//    });
//});

// ################################################# Switcher #########################################

// ______________Switcher

	$(document).on("click", '#myonoffswitch6', function () {
		if (this.checked) {
			$('body').addClass('body-style');
			$('body').removeClass('body-default');
			localStorage.setItem("body-style", "True");
		}
		else {
			$('body').removeClass('body-style');
			localStorage.setItem("body-style", "false");
		}
	});


	$(document).on("click", '#myonoffswitch7', function () {
		if (this.checked) {
			$('body').addClass('body-default');
			$('body').removeClass('body-style');
			localStorage.setItem("body-default", "True");
		}
		else {
			$('body').removeClass('body-default');
			localStorage.setItem("body-default", "false");
		}
	});

	$(document).on("click", '#myonoffswitch1', function () {
		if (this.checked) {
			$('body').addClass('first-menu-dark');
			$('body').removeClass('firstmenu-white');
			localStorage.setItem("first-menu-dark", "True");
		}
		else {
			$('body').removeClass('first-menu-dark');
			localStorage.setItem("first-menu-dark", "false");
		}
	});

	$(document).on("click", '#myonoffswitch2', function () {
		if (this.checked) {
			$('body').addClass('second-menu-dark');
			localStorage.setItem("second-menu-dark", "True");
		}
		else {
			$('body').removeClass('second-menu-dark');
			localStorage.setItem("second-menu-dark", "false");
		}
	});
	$(document).on("click", '#myonoffswitch13', function () {
		if (this.checked) {
			$('body').addClass('reset');
			$('body').removeClass('body-style');
			$('body').removeClass('first-menu-dark');
			$('body').removeClass('second-menu-dark');
			$('body').removeClass('firstmenu-white');
			$('body').removeClass('secondmenu-white');
			$('body').removeClass('singlemenu-color');
			$('body').removeClass('singlemenu-dark');
			$('body').removeClass('singlemenu-white');
			localStorage.setItem("reset", "True");

		}
		else {
			$('body').removeClass('reset');
			localStorage.setItem("reset", "false");
		}
	});


	$(document).on("click", '#myonoffswitch20', function () {
		if (this.checked) {
			$('body').addClass('singlemenu-dark');
			$('body').removeClass('singlemenu-color');
			localStorage.setItem("singlemenu-dark", "True");
		}
		else {
			$('body').removeClass('singlemenu-dark');
			localStorage.setItem("singlemenu-dark", "false");
		}
	});

	$(document).on("click", '#myonoffswitch21', function () {
		if (this.checked) {
			$('body').addClass('singlemenu-color');
			$('body').removeClass('singlemenu-dark');
			$('body').removeClass('singlemenu-white');
			localStorage.setItem("singlemenu-color", "True");
		}
		else {
			$('body').removeClass('singlemenu-color');
			localStorage.setItem("singlemenu-color", "false");
		}
	});

	$(document).on("click", '#myonoffswitch3', function () {
		if (this.checked) {
			$('body').addClass('firstmenu-white');
			$('body').removeClass('body-style');
			$('body').removeClass('first-menu-dark');
			$('body').removeClass('second-menu-dark');
			localStorage.setItem("reset", "True");
		}
		else {
			$('body').removeClass('reset');
			localStorage.setItem("reset", "false");
		}
	});

	$(document).on("click", '#myonoffswitch4', function () {
		if (this.checked) {
			$('body').addClass('secondmenu-white');
			$('body').removeClass('body-style');
			$('body').removeClass('first-menu-dark');
			$('body').removeClass('second-menu-dark');
			localStorage.setItem("reset", "True");
		}
		else {
			$('body').removeClass('reset');
			localStorage.setItem("reset", "false");
		}
	});

	$(document).on("click", '#myonoffswitch5', function () {
		if (this.checked) {
			$('body').addClass('horizontal-color');
			$('body').removeClass('horizontal-dark');
			$('body').removeClass('horizontalmenu-white');
			localStorage.setItem("reset", "True");
		}
		else {
			$('body').removeClass('reset');
			localStorage.setItem("reset", "false");
		}
	});

	$(document).on("click", '#myonoffswitch17', function () {
		if (this.checked) {
			$('body').addClass('horizontal-dark');
			$('body').removeClass('horizontal-color');
			localStorage.setItem("reset", "True");
		}
		else {
			$('body').removeClass('reset');
			localStorage.setItem("reset", "false");
		}
	});

	$(document).on("click", '#myonoffswitch22', function () {
		if (this.checked) {
			$('body').addClass('horizontalmenu-white');
			$('body').removeClass('horizontal-color');
			localStorage.setItem("reset", "True");
		}
		else {
			$('body').removeClass('reset');
			localStorage.setItem("reset", "false");
		}
	});

	$(document).on("click", '#myonoffswitch25', function () {
		if (this.checked) {
			$('body').addClass('singlemenu-white');
			$('body').removeClass('singlemenu-color');
			localStorage.setItem("leftmenu-white", "True");
		}
		else {
			$('body').removeClass('leftmenu-white');
			localStorage.setItem("leftmenu-white", "false");
		}
	});

	$("a[data-theme]").click(function() {
		$("head link#theme").attr("href", $(this).data("theme"));
		$(this).toggleClass('active').siblings().removeClass('active');
	});

	$(document).ready(function(){
        var form_classes = ['mcq','image']
        $(document).on("submit",".mcq_exam_template,.image_exam_template",function(){
            var basic_question_count = parseInt($('#basic-que').val());
            var intermediate_question_count=parseInt($('#intermediate-que').val());
            var advanced_question_count=parseInt($('#advance-que').val());
            var total_question_count = parseInt($('#total-que').val());
            var total_question_calc = basic_question_count + intermediate_question_count + advanced_question_count
            var flag = true;
            console.log("total_question_calc ",total_question_calc)
            if(typeof(total_question_calc) != 'number')
            {
                alert("please fill no of questions field for all difficulty .")
                flag = false;
            }
            else
            {
                if(total_question_calc != total_question_count)
                {
                    alert("sum of questions of category doesnt match the total quesitons count!!")
                    flag = false;
                }
            }
            console.log("the form is",$(this));
            // if(form_classes.includes())
            return flag;
        })
    })



});

