
$(document).ready(function() {
    initDomElement(); //init function
    var templates_table = $('.candidate_table').DataTable({
        language: {
            searchPlaceholder: 'Search...',
            sSearch: '',
            lengthMenu: '_MENU_'
        }
    });

    console.log("from js fiiiiiile", $(".tab-pane#basic"))
    $(".tab-pane#basic").addClass("active");
    $(document).on('click', '.collapse_title', function() { //collapse toggle event
        var getChildList = $(this).next('.categoryListOftab');
        var currentEle = $(this);
        var parentSibling = $(this).closest('.collapse_parent_tab');
        parentSibling.prevAll('.collapse_parent_tab').find('.categoryListOftab').slideUp();
        parentSibling.nextAll('.collapse_parent_tab ').find('.categoryListOftab').slideUp();
        /** siblings list activeClass remove**/
        parentSibling.prevAll('.collapse_parent_tab').find('.collapse_title label').removeClass('actTab')
        parentSibling.prevAll('.collapse_parent_tab').find('.collapse_title .toggle-arrows').removeClass('active')
        parentSibling.nextAll('.collapse_parent_tab').find('.collapse_title label').removeClass('actTab')
        parentSibling.nextAll('.collapse_parent_tab').find('.collapse_title .toggle-arrows').removeClass('active')
        parentSibling.prevAll('.collapse_parent_tab').find('.categoryListOftab li a').removeClass('active')
        parentSibling.nextAll('.collapse_parent_tab').find('.categoryListOftab li a').removeClass('active')
        parentSibling.prevAll('.collapse_parent_tab').find('.catActionBtns').removeClass('bg-act')
        parentSibling.nextAll('.collapse_parent_tab').find('.catActionBtns').removeClass('bg-act')
        if (getChildList.is(":visible")) {
            currentEle.find('label').removeClass('actTab')
            getChildList.slideUp();
            currentEle.find('.toggle-arrows').removeClass('active');
        } else {
            currentEle.find('label').addClass('actTab')
            getChildList.slideDown();
            currentEle.find('.toggle-arrows').addClass('active');
        }
    })

    $(document).on('click', '.categoryListOftab li a', function() { //reset main categories active tab
        $('#header').hide();
        $(document).find('.catActionBtns').removeClass('bg-act')
        $(this).closest('li').find('.catActionBtns').addClass('bg-act');
    })

    $(".tab-title__list li a").on('click', function() { //reset child categories active tab
        $(".categoryListOftab li").each(function() {
            if ($(this).find('a').hasClass('active')) {
                $(this).find('a').removeClass('active')
            }
        })
    })

    $(document).on('click', '.edit-tab', function() { //edit category event
        $('.es-subtitle').attr('readonly', '').removeClass('changeTitle')
        $(this).closest('li').find('.es-subtitle').removeAttr('readonly').addClass('changeTitle');


    })

    $(document).on('change', '.es-subtitle', function() { //edit category event
        var updatecategory = {
            'cat_id': $(this).attr('id'),
            'cat_name': $(this).val(),
            'stage_id': $(this).closest('ul').find("input[name='stage_id']").val()
        }
        if ($(this).val() !== '') {
            $.ajax({
                url: "/agency/update_category/",
                headers: {
                    'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val()
                },
                type: 'POST',
                contentType: 'application/json; charset=UTF-8',
                data: JSON.stringify(updatecategory),
                error: function(request, status, error) {
                    alert(error);
                }
            }).done(function(response) {
                if (response == "True") {
                    swal("Updated!", "Your category has been updated.", "success");
                } else {
                    swal("Updated!", "Your category is safe.", "error");
                }
            });
        } else {
            swal("Enter Category Name!", "Please enter category name.", "error");
        }
        if ($(this).val() == '') {
            setTimeout(function() {
                $(this).removeAttr('readonly')
                console.log('external>>' + $(this).val())
            }, 2500)

        }
    })
    $(document).on('click', '.delete-tab', function() { //delete category list
        var remvoeEle = $(this).closest('li');
        var deletecategory = {
            'cat_id': $(this).closest('li').find("input[name='cat_id']").val(),
            'stage_id': $(this).closest('ul').find("input[name='stage_id']").val()
        }
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
            },
            function(isConfirm) { //send ajax request for detele category action
                if (isConfirm) {
                    $.ajax({
                        url: "/agency/delete_category/",
                        headers: {
                            'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val()
                        },
                        type: 'POST',
                        contentType: 'application/json; charset=UTF-8',
                        data: JSON.stringify(deletecategory),
                        error: function(request, status, error) {
                            alert(error);
                        }
                    }).done(function(response) {

                        swal("Deleted!", "Your category has been deleted.", "success");
                        remvoeEle.remove();
                    });
                } else {
                    swal("Cancelled", "Your category is safe :)", "error");
                }
            });
    });

    $("#tem_name_cre").keyup(function(event) {
        if (event.keyCode === 13) {
            $("#saveJobCreateItem").click();
        }
    });
    $("#saveJobCreateItem").on("click", async function() {
        let tempTitle = $(".jc-tempname").val();
        let tempFormId = $("#jcModel").data('id');
        var add_data = {
            'stage_id': tempFormId,
            'add_category': tempTitle
        };
        var classcreate = '.cat-sub-' + tempFormId;
        var createCatId = '';

        console.log('uyfgfhjhgg', add_data)
        if (tempTitle != "") {
            createCatId = JSON.parse(await add_cat(add_data))
            if (createCatId['status'] == false) {
                $(this).closest(li).remove()
            } else {
                console.log('================', createCatId['cat_id'])
                var addCloneList = `<li>
                <a href="#prereq-2" data-toggle="tab"><i class="fe fe-airplay mr-1"></i>
                    <input type="text" id=` + createCatId['cat_id'] + ` hidden value=` + createCatId['cat_id'] + ` name="cat_id" readonly>
                    <input type="text" id=` + createCatId['cat_id'] + ` class="es-subtitle" value="` + tempTitle + `" readonly>
                </a>
                <div class="catActionBtns">
                    <div class="edit-tab"><i class="fas fa-edit"></i></div>
                    <div class="delete-tab"><i class="fas fa-trash-alt "></i></div>
                </div>
            </li>`;

                $(classcreate).closest('li').before(addCloneList)
                $('#jcModel input[type=text]').val('');
                $('#jcModel #closetempModal').trigger('click');
                $('#error').remove();
            }
        } else {
            $("#error").remove();
            $('#jcModel input[type=text]').after('<div id="error" style="color:red;">Name is Required</div>');
        }

    });
    $(".addmore-tab").on('click', function() {
        $('#error').remove();
        var getId = $(this).attr('data-id');
        console.log('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>', getId)
        $('#jcModel').removeData('id')
        $("#jcModel").attr("data-id", getId);
    })

    async function add_cat(add_data) {
        var newKeyId = "";
        var return_data = await $.ajax({
            url: "/agency/add_category/",
            headers: {
                'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val()
            },
            type: 'POST',
            contentType: 'application/json; charset=UTF-8',
            data: JSON.stringify(add_data),
            error: function(request, status, error) {
                console.log(error);
            }
        }).done(function(response) {});
        return return_data
    };

    $(document).on('click', '.delete-row', function() { //remove template row to the table
       // var getCurrentRow = $(this).closest('tr');
       var rowDomEle = $(this).parent().parent();
       var currentTable = templates_table;
        var deletetemplate = {
            'template_id': $(this).attr('data-template'),
            'cat_id': $(this).attr('data-subcat'),
            'stage_id': $(this).attr('data-maincat')
        }
        console.log('deletetemplate', deletetemplate)
       // console.log('========', deletetemplate)
        swal({
                title: "Are you sure?",
                text: "You will not be able to recover deleted template!",
                type: "warning",
                showCancelButton: true,
                confirmButtonClass: "btn-danger",
                confirmButtonText: "Yes, delete it!",
                cancelButtonText: "Cancel",
                closeOnConfirm: false,
                closeOnCancel: false
            },
            function(isConfirm) {
                //send ajax request for detele category action
                if (isConfirm) {
                    swal("Deleted!", "Your template has been deleted.", "success");
                    $.ajax({
                        url: "/agency/delete_template/",
                        headers: {
                            'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val()
                        },
                        type: 'POST',
                        contentType: 'application/json; charset=UTF-8',
                        data: JSON.stringify(deletetemplate),
                        error: function(request, status, error) {
                            alert(error);
                        }
                    }).done(function(response) {
                        if (response.status == true) {
                            swal("Deleted!", "Your category has been deleted.", "success");
                            removeAndUpdateTable(currentTable,rowDomEle);
                            //rowDomEle.remove();
                            //currentTable.dataTable();
                        } else if (response.status == 'replica') {
                            swal("Replica!", "Your Template dose not delete.", "warning");
                        }
                    });

                } else {
                    swal("Cancelled", "Your template is safe :)", "error");
                }
            });
    })

    $('.print-action').on('click', function() { //print preview action
        console.log('print preview action')
    })
    $('.print-action').on('click', function() { //toggle table nav-list
        console.log('toggle table nav-list')
    })
    $('.print-action').on('click', function() { //toggle table nav-list
        console.log('toggle table nav-list')
    })

    /***
     * Filter List Functionality
     */
    $(".top-search-box").on('keyup',function() {
        var searchTerm = $(this).val();
        var listItem = $('.candidate_table tbody').children('tr');
        var searchSplit = searchTerm.replace(/ /g, "'):containsi('")

        $.extend($.expr[':'], {
        'containsi': function(elem, i, match, array) {
            return (elem.textContent || elem.innerText || '').toLowerCase().indexOf((match[3] || "").toLowerCase()) >= 0;
        }
        });

        $(".candidate_table tbody tr").not(":containsi('" + searchSplit + "')").each(function(e) {
        $(this).attr('visible', 'false');
        });

        $(".candidate_table tbody tr:containsi('" + searchSplit + "')").each(function(e) {
        $(this).attr('visible', 'true');
        });

        var jobCount = $('.candidate_table tbody tr[visible="true"]').length;
        // $('.counter').text(jobCount + ' item');

        if (jobCount == '0') {
        $('.no-result').show();
        } else {
        $('.no-result').hide();
        }
    });

    $('#newTemplateModal').on('hidden.bs.modal', function () {
        console.log('Popup Modal Closed..');
        $("#newTemplateModal")
                .find("input[name=template-name],input[name=template-description],textarea,select")
                    .val('')
                    .end()
                .find("input[type=checkbox], input[type=radio]")
                    .prop("checked", "")
                    .end();
    });

});

$(window).ready(function(){
    console.log('onload')
   $("#newTemplateModal")
            .find("input[name=template-name],input[name=template-description],textarea,select")
                .val('')
                .end()
            .find("input[type=checkbox], input[type=radio]")
                .prop("checked", "")
                .end(); 
})

function removeAndUpdateTable(tabl,rEle){
    tabl.row(rEle).remove().draw(); //table row deleted on delete button
}

function initDomElement() {
    defaultActiveTab();
}

function defaultActiveTab() {
    var activeFirstTab = $(".collapes_wrapper .collapse_parent_tab:first-child");
    activeFirstTab.find('.collapse_title').trigger('click');
    activeFirstTab.find('.categoryListOftab li:first-child a').trigger('click')
    activeFirstTab.find('.categoryListOftab li:first-child .catActionBtns').addClass('bg-act'); 
}

function searchFilterBox() { //search filter 
    var getListSearchBox = $(document).find('#example1_filter');
    $(document).find('.fx-search-view').append(getListSearchBox);
}

function siblingTabClose() {
    // if(showFlag){
    $(".categoryListOftab li").each(function() {
        if ($(this).find('a').hasClass('active')) {
            $(this).find('a').removeClass('active')
        }
    })
}



$('.select-new-stage-list').on('change', function() {
    var selectVal = this.selectedOptions[0].value;
    console.log('selectVal', selectVal)
    $('.select-new-category-list').children().remove().end().append('<option label="select category" selected disabled></option>');
    $.ajax({
        url: "/agency/get_category/",
        headers: {
            'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val()
        },
        type: 'POST',
        contentType: 'application/json; charset=UTF-8',
        data: JSON.stringify({
            'stage_id': selectVal
        }),
        error: function(request, status, error) {
            alert(error);
        }
    }).done(function(response) {
        response = JSON.parse(response)
        if (response['status'] == true) {
            category = JSON.parse(response['category_get'])
            category.forEach(element => {
                console.log(element['pk'], element['fields']['name'])
                $('.select-new-category-list').append($("<option></option>").attr("value", element['pk']).text(element['fields']['name']));
            });
        } else {
            swal("Get!", "Your category is safe.", "error");
        }
    });

});

$(window).on('load',function() {
 // setTimeout(function(){
    var sesIdOfStage =  $("#stageItemId").text();
    var sesIdOfCat = $("#categoryItemId").text();
    if(sesIdOfStage != ""){
        $(".collapes_wrapper .collapse_parent_tab").each(function(idx){
            var collapseId = $(this).find('.collapse_title').attr('data-id');
            //console.log('list id',collapseId)
            if(sesIdOfStage == collapseId){
                $(document).find(".collapes_wrapper .collapse_parent_tab").eq(idx).find('.collapse_title')[0].click();
                $("a[href='#category"+sesIdOfCat+"']")[0].click();
            }
        })
    }
//  })
  
});
