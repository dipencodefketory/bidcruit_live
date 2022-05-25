$(document).ready( async function(){

    async function getWorkflowData(){
            var return_data = await $.ajax({
                url:"/company/get_workflow_data/",
                headers: {'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val() },
                type:'POST',
                contentType: 'application/json; charset=UTF-8',
                error: function (request, status, error) {
                }
            }).done(function(response){
                console.log('response>>>>>',response)
            });
            return return_data
        }
    var data = await getWorkflowData();

    var stageList = data['stages_data'];
    var categoryList = data['category_data'];
    var tempList = data['template_data'];

    stageListPopulate(stageList);

    $('#stageSelectorList').on('change',function(){ //stage selector event
        var getStageId = $(this).find('option:selected').val();
        if(getStageId !== ''){
            var cateListData = {'id':getStageId,'data':categoryList};
            cateListPopulate(cateListData);
            $('#templateSelectorList option').remove();
            $('#templateSelectorList').append(`<option label="Select Template"></option>`);
            $('#templateSelectorList').attr('disabled','');
        }else{
            $('#categorySelectorList option,#templateSelectorList option').remove();
            $('#categorySelectorList,#templateSelectorList').attr('disabled','');
            $('#categorySelectorList').append(`<option label="Select Category"></option>`);
            $('#templateSelectorList').append(`<option label="Select Template"></option>`);
        }
    })

    $('#categorySelectorList').on('change',function(){ //category selector event
        var getCatId = $(this).find('option:selected').val();
        if(getCatId !== ''){
            var templistData = {'id':getCatId,'data':tempList}
            tempListPopulate(templistData);
        }else{
            $('#templateSelectorList option').remove();
            $('#templateSelectorList').append(`<option label="Select Template"></option>`);
            $('#templateSelectorList').attr('disabled','')
        }
    })

    $('.expectSalarySlider').ionRangeSlider({ //salary range slider
		type: 'double',
		grid: true,
		min: 0,
		max: 1000,
		from: 200,
		to: 800,
		prefix: '$'
	});

	$(".toggle-tab").on('click',function(){
		$('.toggle-tab').removeClass('active');
		$(this).addClass('active');
		var getActiveTabId = $(this).data('item');
		$(".tab-container").hide();
		$('#'+getActiveTabId).show();
	})

	$(document).on('click','.tab-listing',function(){
	    var getUserId = $(this).data('userid');
        $('.drawer-list .sidebar-preview').each(function(){
            if(getUserId == $(this).data('item')){
                $(this).css({'width':'100%','visibility':'visible'});
                $('body').addClass('body_overflow');
            }
        })
	})

	$(document).on('click','.slideClose',function(){
        $('.sidebar-preview').css({'width':'0%','visibility':'hidden'});
        $('.slideClose').addClass('inside');
        $('body').removeClass('body_overflow');
    })

	$(document).on('click','.sidebar-preview',function(e){
		var container = $(".side-barContainer");
		if (!container.is(e.target) && container.has(e.target).length === 0)
		{
			$('.sidebar-preview').css({'width':'0%','visibility':'hidden'});
        	$('.slideClose').addClass('inside');
        	$('body').removeClass('body_overflow');
		}
	});
})

// functions

function stageListPopulate(getStageList){
    optHtml = '';
    if(getStageList.length){
        $.each(getStageList, function(i){
            optHtml += `<option class="text-capitalize" value="`+getStageList[i].key+`">`+getStageList[i].stage_name+`</option>`;
        })
        $('#stageSelectorList').append(optHtml);
    }
}


function cateListPopulate(getListingItems){
    var optCateHtml = '';
    var getSelectedStageId = getListingItems.id;
    var getCateItemList = getListingItems.data;
    if(getCateItemList.length){
        $('#categorySelectorList option').remove()
        $.each(getCateItemList,function(cKey){
            if(getCateItemList[cKey].stageKey == getSelectedStageId){
                var cateDataItems  = getCateItemList[cKey].cate_list;
                if(cateDataItems.length){
                    optCateHtml +=`<option label="Select Category"></option>`;
                    $.each(cateDataItems,function(keyId){
                        optCateHtml += `<option value="`+cateDataItems[keyId].key+`">`+cateDataItems[keyId].cate_name+`</option>`;
                    })
                }
                $('#categorySelectorList').append(optCateHtml);
            }
        })
        $('#categorySelectorList').removeAttr('disabled')
    }
}

function tempListPopulate(getTempListItems){
    var optCateHtml = '';
    var getSelectedCateId = getTempListItems.id;
    var getTempItemList = getTempListItems.data;
    //console.log(getSelectedCateId)
    //console.log(getTempItemList)
    if(getTempItemList.length){
        $('#templateSelectorList option').remove()
        $.each(getTempItemList,function(cKey){
            if(getTempItemList[cKey].cateKey == getSelectedCateId){
                var tempDataItems  = getTempItemList[cKey].temp_list;
                if(tempDataItems.length){
                    optCateHtml +=`<option label="Select Template"></option>`;
                    $.each(tempDataItems,function(keyId){
                        optCateHtml += `<option value="`+tempDataItems[keyId].key+`">`+tempDataItems[keyId].temp_name+`</option>`;
                    })
                }
                $('#templateSelectorList').append(optCateHtml);
            }
        })
        $('#templateSelectorList').removeAttr('disabled')
    }
}