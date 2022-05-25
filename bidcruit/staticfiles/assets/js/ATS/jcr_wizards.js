

$(function() {
    
	'use strict'
	
	var primary = 0;
	var secondary = 0;
	var objective = 0;
	var updateCategoryList = [];
	var index_to_move = null;

	var wizard = $('#wizard2').steps({
		headerTag: 'h3',
		bodyTag: 'section',
		autoFocus: true,
		titleTemplate: '<span class="number">#index#<\/span> <span class="title">#title#<\/span>',
		onStepChanging: function(event, currentIndex, newIndex) {
			var response = changestep(currentIndex,newIndex);
			if (response ==  true){
				return true
			}else{
				return false
			}
		},
		onStepChanged: function (event, currentIndex, newIndex) {

 
			// console.log('currentIndex',currentIndex);
			// console.log('newIndex',newIndex);
			// if(primary == 0 && secondary == 0){
			// 	$('#wizard2').steps("setStep", 3);
			// }else if(primary == 0 && objective == 0){
			// 	$('#wizard2').steps("setStep", 2);
			// }else if(secondary == 0  && objective == 0 ){
			// 	 $('#wizard2').steps("setStep", 1);
			// }else if(primary == 0 ){
			// 	$('#wizard2').steps("setStep", 2);
		    // }else if(secondary == 0){
			// 	$('#wizard2').steps("setStep", 1);
			// }else if(objective == 0 ){
			// 	$('#wizard2').steps("setStep", 1);
			// }

			// console.log('currentIndex',currentIndex);
			// console.log('newIndex',newIndex);

			// if (flag == true){
			// 	$('#wizard2').steps("setStep", index_to_move);
				
			// }
		},
	});


	function changestep( currentIndex, newIndex){

		var myInput_primary = $('#myInput_primary').val();
		var myInput_secondary = $('#myInput_secondary').val();
		var myInput_objective = $('#myInput_objective').val();
		
		$('#get_primary_input').val(myInput_primary);
		$('#get_secondary_input').val(myInput_secondary);
		$('#get_objective_input').val(myInput_objective);

		primary = myInput_primary;
		secondary = myInput_secondary;
		objective = myInput_objective;

		if (currentIndex < newIndex) {
			// Step 1 form validation
			if (currentIndex === 0) {
				
			   
				var total_perct = parseInt(myInput_primary) + parseInt(myInput_secondary) + parseInt(myInput_objective);
			 
				if (total_perct == 100) {		
					
					
				   	updateCategoryList.push({'category': 'primary-list','cat_value': primary,'id': null,'addDetailsItem': ''});
					updateCategoryList.push({'category': 'secondary-list','cat_value': secondary,'id': null,'addDetailsItem': ''});
					updateCategoryList.push({'category': 'objective-list','cat_value': objective,'id': null,'addDetailsItem': ''});
					
					console.log(updateCategoryList);
					return true;

				}else{
					alert("Total not 100");
					return false;
				}
			   
			}
			// Step 2 form validation
			if (currentIndex === 1) {

				// updateCategoryList[0].addDetailsItem.push()
				// console.log(updateCategoryList)
				
				var main_section_list = $('.particular_Primary').find('.section_sub_box_inner');
				var Total_main_section = $('.particular_Primary').find('.section_sub_box_inner').length;

				var main_cat_no = true;
				var main_cat_total_no = 0;

				var sub_main_cat_no = true;
			    var sub_main_cat_total_check = true

				var question_sections = true;
				
			    var question_total_check = true;
				var question_in_arr_check = true;

				var addDetailsItem = [];
			    
				var flag = true;
				console.log('Total Main section : ',Total_main_section);
				$.each(main_section_list, function(i){
					if(flag){
						if(main_section_list.eq(i).hasClass('section_sub_box_inner')){
							if(main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-main ').val() !== "" && main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-main ').val() != 0){
								if(main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-text').val() !== ""){
									main_cat_total_no += parseInt(main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-main').val());
									main_cat_no = false;
									

									var cat_type = main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-text').val();
									var cate_percent = parseInt(main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-main').val());

									addDetailsItem.push({'cat_type': cat_type,'cate_percent': cate_percent,'id': null,'cat_subtype': []});

									var sub_main_section_list = main_section_list.eq(i).find('.question-section');
									var Total_sub_main_section = main_section_list.eq(i).find('.question-section').length;
									var sub_main_cat_total_no = 0;

									console.log('Total SUB Main section : ',Total_sub_main_section);
									$.each(sub_main_section_list, function(j){
										if(flag){
											if(sub_main_section_list.eq(j).hasClass('question-section')){
												if(sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-main').val() !== "" && sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-main').val() != 0){
													if(sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-text').val() !== ""){
														sub_main_cat_total_no += parseInt(sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-main').val());
														sub_main_cat_no = false;

														var arr_single_value_list=[];
														var question_total_no = 0;
														var checkMetchingOfSelector = sub_main_section_list.eq(j).find(".question_text_num_cho .switch-field input[type='radio']:checked").val();
														var question_section_list = sub_main_section_list.eq(j).find('.parent-lavel-select .select-input__field');

														var question = sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-text').val();
														var q_percent = parseInt(sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-main').val());
													
														addDetailsItem[i].cat_subtype.push({'question': question,'q_percent': q_percent,'matching':checkMetchingOfSelector,'id': null,'details': []});

														$.each(question_section_list, function(x){
															if(flag){	
																if(question_section_list.eq(x).find('.number_field_box').val() !== "" ){
																	if(question_section_list.eq(x).hasClass('select-input__field')){
																		if(question_section_list.eq(x).find('.option-label').val() !== ""){
																			question_total_no += parseInt(question_section_list.eq(x).find('.number_field_box').val());
																			arr_single_value_list.push(parseInt(question_section_list.eq(x).find('.number_field_box').val())); 
																			question_sections = false;

																			var title_option = question_section_list.eq(x).find('.option-label').val();
																			var percent_option = parseInt(question_section_list.eq(x).find('.number_field_box').val());
																		
																			addDetailsItem[i].cat_subtype[j].details.push({'title': title_option,'percent': percent_option,'id': null});

																		}else{
																			question_sections = true;
																			question_section_list.eq(x).find('.option-label').addClass('ntValidShadow');
																			question_section_list.eq(x).find('.option-label').focus();
																			setTimeout(function(){
																				question_section_list.eq(x).find('.option-label').removeClass('ntValidShadow');
																			},2500)
																			var msg = "You Must Enter Add Option Text and Value"
																			snakBarShow(msg);
																			flag = false;
																			return false;
																		}
																	}
																}else{
																	question_sections = true;
																	question_section_list.eq(x).find('.number_field_box').addClass('ntValidShadow');
																	question_section_list.eq(x).find('.number_field_box').focus();
																	setTimeout(function(){
																		question_section_list.eq(x).find('.number_field_box').removeClass('ntValidShadow');
																	},2500)
																	var msg = "You Must Enter Add Option Text and Value"
																	snakBarShow(msg);
																	flag = false;
																	return false;
																}
															}
														})

														console.log('Check Type >>>>>>>> '+j+'=',checkMetchingOfSelector);
														console.log('Total Option sum >>>>> '+j+'=',question_total_no);
														console.log('Array list >>>>> '+j+'=',arr_single_value_list);
														if(flag){
															if(checkMetchingOfSelector == 'multiple'){
																question_in_arr_check = false;
																if(question_total_no == 100){ 
																	question_total_check = false;
																}else{
																	question_total_check = true;
																	var showMsg = "The total option field not exceed 100% in multi type";
																	snakBarShow(showMsg);	
																	flag = false;
																}
															}else if(checkMetchingOfSelector == 'single'){
																question_total_check = false;
																
																if(find_duplicate_in_array(arr_single_value_list)==true){
																	if(arr_single_value_list.includes(100)) {
																		question_in_arr_check = false;
																	} else {
																		question_in_arr_check = true;
																		var showMsg = "you must any one option field 100% in single type";
																		snakBarShow(showMsg);	
																		flag = false;														
																	}
																}else{
																	question_in_arr_check = true;
																	var showMsg = "100 Allow only one time in single type";
																	snakBarShow(showMsg);
																	flag = false;
																}
															}
														}
														console.log('question total check >>>>> '+j+'=',question_total_check);
														console.log('question total check arrr >>>>> '+j+'=',question_in_arr_check);

													}else{
														sub_main_cat_no = true;
														sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-text').addClass('ntValidShadow');
														sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-text').focus();
														setTimeout(function(){
															sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-text').removeClass('ntValidShadow');
														},2500)
														var msg = "You Must Enter Add New Question and Value"
														snakBarShow(msg);
														flag = false;
														return false;
													}
					
												}else{
													sub_main_cat_no = true;
													sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-main').addClass('ntValidShadow');
													sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-main').focus();
													setTimeout(function(){
														sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-main').removeClass('ntValidShadow');
													},2500)
													var msg = "You Must Enter Add New Question and Value"
													snakBarShow(msg);
													flag = false;
													return false;
												}
									
											}
										}
									})

									if(flag){
										if(sub_main_cat_total_no == 100){ 
											sub_main_cat_total_check = false;
										}else{
											sub_main_cat_total_check = true;	

											var msg = "Questions Total Jcr Not Exceed 100%"
											snakBarShow(msg);
											flag = false;
											return false;								
										}
									}
									console.log('sub Total check',sub_main_cat_total_no);
									console.log('sub check ',sub_main_cat_total_check);

								}else{
									main_cat_no = true;
									main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-text').addClass('ntValidShadow');
									main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-text').focus();
									setTimeout(function(){
										main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-text').removeClass('ntValidShadow');
									},2500)
									var msg = "You Must Enter Add New Category and Value"
									snakBarShow(msg);
									flag = false;
									return false;
								}
							}else{
								main_cat_no = true;
								main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-main').addClass('ntValidShadow');
								main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-main').focus();
								setTimeout(function(){
									main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-main ').removeClass('ntValidShadow');
								},2500)
								var msg = "You Must Enter Add New Category and Value"
								snakBarShow(msg);
								flag = false;
								return false;
							}
								
						}
					}
				})
				console.log('sub main cat total_no check ',sub_main_cat_total_check);
				if(!main_cat_no && main_cat_total_no == 100 && !sub_main_cat_no && !sub_main_cat_total_check && !question_sections && !question_total_check && !question_in_arr_check){
					console.log('yyyyyyyyyyyyyyyy');
					//alert('all Done');
					updateCategoryList[0].addDetailsItem=addDetailsItem
					console.log(updateCategoryList);
					return true;
				}else{
					console.log('nnnnnnnnnnnnnnnn');
					if(flag){
						if(main_cat_total_no !=100 ){
							var msg = "Category Total Jcr Not Exceed 100%"
							snakBarShow(msg);
						}
					}
					
					return false;
				}

				
			}
			if (currentIndex === 2) {
				
				var main_section_list = $('.particular_secondary').find('.section_sub_box_inner');
				var Total_main_section = $('.particular_secondary').find('.section_sub_box_inner').length;

				var main_cat_no = true;
				var main_cat_total_no = 0;

				var sub_main_cat_no = true;
			    var sub_main_cat_total_check = true

				var question_sections = true;
				
			    var question_total_check = true;
				var question_in_arr_check = true;

				var addDetailsItem = [];
			    
				var flag = true;
				console.log('Total Main section : ',Total_main_section);
				$.each(main_section_list, function(i){
					if(flag){
						if(main_section_list.eq(i).hasClass('section_sub_box_inner')){
							if(main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-main ').val() !== "" && main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-main ').val() != 0){
								if(main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-text').val() !== ""){
									main_cat_total_no += parseInt(main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-main').val());
									main_cat_no = false;
									

									var cat_type = main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-text').val();
									var cate_percent = parseInt(main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-main').val());

									addDetailsItem.push({'cat_type': cat_type,'cate_percent': cate_percent,'id': null,'cat_subtype': []});

									var sub_main_section_list = main_section_list.eq(i).find('.question-section');
									var Total_sub_main_section = main_section_list.eq(i).find('.question-section').length;
									var sub_main_cat_total_no = 0;

									console.log('Total SUB Main section : ',Total_sub_main_section);
									$.each(sub_main_section_list, function(j){
										if(flag){
											if(sub_main_section_list.eq(j).hasClass('question-section')){
												if(sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-main').val() !== "" && sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-main').val() != 0){
													if(sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-text').val() !== ""){
														sub_main_cat_total_no += parseInt(sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-main').val());
														sub_main_cat_no = false;

														var arr_single_value_list=[];
														var question_total_no = 0;
														var checkMetchingOfSelector = sub_main_section_list.eq(j).find(".question_text_num_cho .switch-field input[type='radio']:checked").val();
														var question_section_list = sub_main_section_list.eq(j).find('.parent-lavel-select .select-input__field');

														var question = sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-text').val();
														var q_percent = parseInt(sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-main').val());
													
														addDetailsItem[i].cat_subtype.push({'question': question,'q_percent': q_percent,'matching':checkMetchingOfSelector,'id': null,'details': []});

														$.each(question_section_list, function(x){
															if(flag){	
																if(question_section_list.eq(x).find('.number_field_box').val() !== "" ){
																	if(question_section_list.eq(x).hasClass('select-input__field')){
																		if(question_section_list.eq(x).find('.option-label').val() !== ""){
																			question_total_no += parseInt(question_section_list.eq(x).find('.number_field_box').val());
																			arr_single_value_list.push(parseInt(question_section_list.eq(x).find('.number_field_box').val())); 
																			question_sections = false;

																			var title_option = question_section_list.eq(x).find('.option-label').val();
																			var percent_option = parseInt(question_section_list.eq(x).find('.number_field_box').val());
																		
																			addDetailsItem[i].cat_subtype[j].details.push({'title': title_option,'percent': percent_option,'id': null});

																		}else{
																			question_sections = true;
																			question_section_list.eq(x).find('.option-label').addClass('ntValidShadow');
																			question_section_list.eq(x).find('.option-label').focus();
																			setTimeout(function(){
																				question_section_list.eq(x).find('.option-label').removeClass('ntValidShadow');
																			},2500)
																			var msg = "You Must Enter Add Option Text and Value"
																			snakBarShow(msg);
																			flag = false;
																			return false;
																		}
																	}
																}else{
																	question_sections = true;
																	question_section_list.eq(x).find('.number_field_box').addClass('ntValidShadow');
																	question_section_list.eq(x).find('.number_field_box').focus();
																	setTimeout(function(){
																		question_section_list.eq(x).find('.number_field_box').removeClass('ntValidShadow');
																	},2500)
																	var msg = "You Must Enter Add Option Text and Value"
																	snakBarShow(msg);
																	flag = false;
																	return false;
																}
															}
														})

														console.log('Check Type >>>>>>>> '+j+'=',checkMetchingOfSelector);
														console.log('Total Option sum >>>>> '+j+'=',question_total_no);
														console.log('Array list >>>>> '+j+'=',arr_single_value_list);
														if(flag){
															if(checkMetchingOfSelector == 'multiple'){
																question_in_arr_check = false;
																if(question_total_no == 100){ 
																	question_total_check = false;
																}else{
																	question_total_check = true;
																	var showMsg = "The total option field not exceed 100% in multi type";
																	snakBarShow(showMsg);	
																	flag = false;
																}
															}else if(checkMetchingOfSelector == 'single'){
																question_total_check = false;
																
																if(find_duplicate_in_array(arr_single_value_list)==true){
																	if(arr_single_value_list.includes(100)) {
																		question_in_arr_check = false;
																	} else {
																		question_in_arr_check = true;
																		var showMsg = "you must any one option field 100% in single type";
																		snakBarShow(showMsg);	
																		flag = false;														
																	}
																}else{
																	question_in_arr_check = true;
																	var showMsg = "100 Allow only one time in single type";
																	snakBarShow(showMsg);
																	flag = false;
																}
															}
														}
														console.log('question total check >>>>> '+j+'=',question_total_check);
														console.log('question total check arrr >>>>> '+j+'=',question_in_arr_check);

													}else{
														sub_main_cat_no = true;
														sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-text').addClass('ntValidShadow');
														sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-text').focus();
														setTimeout(function(){
															sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-text').removeClass('ntValidShadow');
														},2500)
														var msg = "You Must Enter Add New Question and Value"
														snakBarShow(msg);
														flag = false;
														return false;
													}
					
												}else{
													sub_main_cat_no = true;
													sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-main').addClass('ntValidShadow');
													sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-main').focus();
													setTimeout(function(){
														sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-main').removeClass('ntValidShadow');
													},2500)
													var msg = "You Must Enter Add New Question and Value"
													snakBarShow(msg);
													flag = false;
													return false;
												}
									
											}
										}
									})

									if(flag){
										if(sub_main_cat_total_no == 100){ 
											sub_main_cat_total_check = false;
										}else{
											sub_main_cat_total_check = true;	

											var msg = "Questions Total Jcr Not Exceed 100%"
											snakBarShow(msg);
											flag = false;
											return false;								
										}
									}
									console.log('sub Total check',sub_main_cat_total_no);
									console.log('sub check ',sub_main_cat_total_check);

								}else{
									main_cat_no = true;
									main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-text').addClass('ntValidShadow');
									main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-text').focus();
									setTimeout(function(){
										main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-text').removeClass('ntValidShadow');
									},2500)
									var msg = "You Must Enter Add New Category and Value"
									snakBarShow(msg);
									flag = false;
									return false;
								}
							}else{
								main_cat_no = true;
								main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-main').addClass('ntValidShadow');
								main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-main').focus();
								setTimeout(function(){
									main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-main ').removeClass('ntValidShadow');
								},2500)
								var msg = "You Must Enter Add New Category and Value"
								snakBarShow(msg);
								flag = false;
								return false;
							}
								
						}
					}
				})
				console.log('sub main cat total_no check ',sub_main_cat_total_check);
				if(!main_cat_no && main_cat_total_no == 100 && !sub_main_cat_no && !sub_main_cat_total_check && !question_sections && !question_total_check && !question_in_arr_check){
					console.log('yyyyyyyyyyyyyyyy');
				//	alert('all Done');
					updateCategoryList[1].addDetailsItem=addDetailsItem
					console.log(updateCategoryList);
					return true;
				}else{
					console.log('nnnnnnnnnnnnnnnn');
					if(flag){
						if(main_cat_total_no !=100 ){
							var msg = "Category Total Jcr Not Exceed 100%"
							snakBarShow(msg);
						}
					}
					
					return false;
				}
				
			}
			if (currentIndex === 3) {
				
				var main_section_list = $('.particular_objective').find('.section_sub_box_inner');
				var Total_main_section = $('.particular_objective').find('.section_sub_box_inner').length;

				var main_cat_no = true;
				var main_cat_total_no = 0;

				var sub_main_cat_no = true;
			    var sub_main_cat_total_check = true

				var question_sections = true;
				
			    var question_total_check = true;
				var question_in_arr_check = true;

				var addDetailsItem = [];
			    
				var flag = true;
				console.log('Total Main section : ',Total_main_section);
				$.each(main_section_list, function(i){
					if(flag){
						if(main_section_list.eq(i).hasClass('section_sub_box_inner')){
							if(main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-main ').val() !== "" && main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-main ').val() != 0){
								if(main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-text').val() !== ""){
									main_cat_total_no += parseInt(main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-main').val());
									main_cat_no = false;
									

									var cat_type = main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-text').val();
									var cate_percent = parseInt(main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-main').val());

									addDetailsItem.push({'cat_type': cat_type,'cate_percent': cate_percent,'id': null,'cat_subtype': []});

									var sub_main_section_list = main_section_list.eq(i).find('.question-section');
									var Total_sub_main_section = main_section_list.eq(i).find('.question-section').length;
									var sub_main_cat_total_no = 0;

									console.log('Total SUB Main section : ',Total_sub_main_section);
									$.each(sub_main_section_list, function(j){
										if(flag){
											if(sub_main_section_list.eq(j).hasClass('question-section')){
												if(sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-main').val() !== "" && sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-main').val() != 0){
													if(sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-text').val() !== ""){
														sub_main_cat_total_no += parseInt(sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-main').val());
														sub_main_cat_no = false;

														var arr_single_value_list=[];
														var question_total_no = 0;
														var checkMetchingOfSelector = sub_main_section_list.eq(j).find(".question_text_num_cho .switch-field input[type='radio']:checked").val();
														var question_section_list = sub_main_section_list.eq(j).find('.parent-lavel-select .select-input__field');

														var question = sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-text').val();
														var q_percent = parseInt(sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-main').val());
													
														addDetailsItem[i].cat_subtype.push({'question': question,'q_percent': q_percent,'matching':checkMetchingOfSelector,'id': null,'details': []});

														$.each(question_section_list, function(x){
															if(flag){	
																if(question_section_list.eq(x).find('.number_field_box').val() !== "" ){
																	if(question_section_list.eq(x).hasClass('select-input__field')){
																		if(question_section_list.eq(x).find('.option-label').val() !== ""){
																			question_total_no += parseInt(question_section_list.eq(x).find('.number_field_box').val());
																			arr_single_value_list.push(parseInt(question_section_list.eq(x).find('.number_field_box').val())); 
																			question_sections = false;

																			var title_option = question_section_list.eq(x).find('.option-label').val();
																			var percent_option = parseInt(question_section_list.eq(x).find('.number_field_box').val());
																		
																			addDetailsItem[i].cat_subtype[j].details.push({'title': title_option,'percent': percent_option,'id': null});

																		}else{
																			question_sections = true;
																			question_section_list.eq(x).find('.option-label').addClass('ntValidShadow');
																			question_section_list.eq(x).find('.option-label').focus();
																			setTimeout(function(){
																				question_section_list.eq(x).find('.option-label').removeClass('ntValidShadow');
																			},2500)
																			var msg = "You Must Enter Add Option Text and Value"
																			snakBarShow(msg);
																			flag = false;
																			return false;
																		}
																	}
																}else{
																	question_sections = true;
																	question_section_list.eq(x).find('.number_field_box').addClass('ntValidShadow');
																	question_section_list.eq(x).find('.number_field_box').focus();
																	setTimeout(function(){
																		question_section_list.eq(x).find('.number_field_box').removeClass('ntValidShadow');
																	},2500)
																	var msg = "You Must Enter Add Option Text and Value"
																	snakBarShow(msg);
																	flag = false;
																	return false;
																}
															}
														})

														console.log('Check Type >>>>>>>> '+j+'=',checkMetchingOfSelector);
														console.log('Total Option sum >>>>> '+j+'=',question_total_no);
														console.log('Array list >>>>> '+j+'=',arr_single_value_list);
														if(flag){
															if(checkMetchingOfSelector == 'multiple'){
																question_in_arr_check = false;
																if(question_total_no == 100){ 
																	question_total_check = false;
																}else{
																	question_total_check = true;
																	var showMsg = "The total option field not exceed 100% in multi type";
																	snakBarShow(showMsg);	
																	flag = false;
																}
															}else if(checkMetchingOfSelector == 'single'){
																question_total_check = false;
																
																if(find_duplicate_in_array(arr_single_value_list)==true){
																	if(arr_single_value_list.includes(100)) {
																		question_in_arr_check = false;
																	} else {
																		question_in_arr_check = true;
																		var showMsg = "you must any one option field 100% in single type";
																		snakBarShow(showMsg);	
																		flag = false;														
																	}
																}else{
																	question_in_arr_check = true;
																	var showMsg = "100 Allow only one time in single type";
																	snakBarShow(showMsg);
																	flag = false;
																}
															}
														}
														console.log('question total check >>>>> '+j+'=',question_total_check);
														console.log('question total check arrr >>>>> '+j+'=',question_in_arr_check);

													}else{
														sub_main_cat_no = true;
														sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-text').addClass('ntValidShadow');
														sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-text').focus();
														setTimeout(function(){
															sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-text').removeClass('ntValidShadow');
														},2500)
														var msg = "You Must Enter Add New Question and Value"
														snakBarShow(msg);
														flag = false;
														return false;
													}
					
												}else{
													sub_main_cat_no = true;
													sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-main').addClass('ntValidShadow');
													sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-main').focus();
													setTimeout(function(){
														sub_main_section_list.eq(j).find('.question_text_num_cho .q-feild-main').removeClass('ntValidShadow');
													},2500)
													var msg = "You Must Enter Add New Question and Value"
													snakBarShow(msg);
													flag = false;
													return false;
												}
									
											}
										}
									})

									if(flag){
										if(sub_main_cat_total_no == 100){ 
											sub_main_cat_total_check = false;
										}else{
											sub_main_cat_total_check = true;	

											var msg = "Questions Total Jcr Not Exceed 100%"
											snakBarShow(msg);
											flag = false;
											return false;								
										}
									}
									console.log('sub Total check',sub_main_cat_total_no);
									console.log('sub check ',sub_main_cat_total_check);

								}else{
									main_cat_no = true;
									main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-text').addClass('ntValidShadow');
									main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-text').focus();
									setTimeout(function(){
										main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-text').removeClass('ntValidShadow');
									},2500)
									var msg = "You Must Enter Add New Category and Value"
									snakBarShow(msg);
									flag = false;
									return false;
								}
							}else{
								main_cat_no = true;
								main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-main').addClass('ntValidShadow');
								main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-main').focus();
								setTimeout(function(){
									main_section_list.eq(i).find('.sub_box_inner_input .cat-feild-main ').removeClass('ntValidShadow');
								},2500)
								var msg = "You Must Enter Add New Category and Value"
								snakBarShow(msg);
								flag = false;
								return false;
							}
								
						}
					}
				})
				console.log('sub main cat total_no check ',sub_main_cat_total_check);
				if(!main_cat_no && main_cat_total_no == 100 && !sub_main_cat_no && !sub_main_cat_total_check && !question_sections && !question_total_check && !question_in_arr_check){
					console.log('yyyyyyyyyyyyyyyy');
					//alert('all Done');
					updateCategoryList[2].addDetailsItem=addDetailsItem
					console.log(updateCategoryList);
					return true;
				}else{
					console.log('nnnnnnnnnnnnnnnn');
					if(flag){
						if(main_cat_total_no !=100 ){
							var msg = "Category Total Jcr Not Exceed 100%"
							snakBarShow(msg);
						}
					}
					
					return false;
				}
				
			}
			// Always allow step back to the previous step even if the current step is not valid.
		} else {
			return true;
		}

	}

});