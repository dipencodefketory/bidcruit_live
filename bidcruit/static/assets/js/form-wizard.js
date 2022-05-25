$(function() {
	'use strict'
	$('#wizard1').steps({
		headerTag: 'h5',
		bodyTag: 'section',
		autoFocus: true,
		titleTemplate: '<span class="number">#index#<\/span> <span class="title">#title#<\/span>',
		onFinished: function (event, currentIndex){
				document.getElementById('TEST_FORM').submit();
            	// window.location.href = 'https://bidcruit.com/candidate/home/';
            	//window.location.href = "{% url 'candidate:home' %}";
		}
	});
	var finishButton = $('#wizard1').find('a[href="#next"]')
	$(finishButton).removeAttr("href");
    	$(finishButton).attr("disabled","disabled");
    	$(finishButton).attr("style","opacity:0.5");
	$('#wizard3').steps({
		headerTag: 'h3',
		bodyTag: 'section',
		autoFocus: true,
		titleTemplate: '<span class="number">#index#<\/span> <span class="title">#title#<\/span>',
		stepsOrientation: 1,
		onFinished: function (event, currentIndex){
		   $("#wizard1").steps("next");
		   $(finishButton).attr("href","#next");
		   $(finishButton).removeAttr("disabled");
		   $(finishButton).removeAttr("style");
		}
	});
	
});
