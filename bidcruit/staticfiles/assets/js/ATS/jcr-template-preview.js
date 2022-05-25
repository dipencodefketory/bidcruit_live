$(function () {
    init();
    
});

function init(){
    var newHtml = "";
    // var listItems = [{"cat_name":"primary-list","cat_value":50,"id":308,"addDetailsItem":[{"cat_type":"javascript","id":327,"cate_percent":50,"cat_subtype":[{"question":"client side coding","id":328,"q_percent":100,"matching":"single","details":[{"id":332,"title":"react","percent":100},{"id":331,"title":"jquery","percent":50},{"id":330,"title":"angular","percent":25},{"id":329,"title":"tpescript","percent":25}]}]},{"cat_type":"python","id":311,"cate_percent":50,"cat_subtype":[{"question":"Machine Learning","id":315,"q_percent":50,"matching":"multi","details":[{"id":318,"title":"pytorch","percent":30},{"id":317,"title":"tensorflow","percent":20},{"id":316,"title":"keras","percent":50}]},{"question":"Web Development","id":312,"q_percent":50,"matching":"single","details":[{"id":314,"title":"django","percent":100},{"id":313,"title":"flask","percent":50}]}]}]},{"cat_name":"secondary-list","cat_value":30,"id":309,"addDetailsItem":[{"cat_type":"C","id":319,"cate_percent":100,"cat_subtype":[{"question":"c++","id":322,"q_percent":80,"matching":"multi","details":[{"id":326,"title":"encapsulation","percent":25},{"id":325,"title":"abstraction","percent":25},{"id":324,"title":"polymorphism","percent":25},{"id":323,"title":"inheritance","percent":25}]},{"question":"C progrtammnng","id":320,"q_percent":20,"matching":"single","details":[{"id":321,"title":"FBP","percent":100}]}]}]},{"cat_name":"objective-list","cat_value":20,"id":310,"addDetailsItem":[]}];
    var listItems = get_jcrData();

    

    newHtml += `<ul class="active lavel-1"> <li class="super-parent"> <a href="javascript:void(0);"> <div class="member-view-box"> <div class="member-image"> <p class="percent_view">100&nbsp;%</div><div class="member-details"> <h3 class="main-title h5">JCR</h3> </div></div></div></a> <ul class="active">`;
    $.each(listItems,function(lv1key){
       var splitItem = listItems[lv1key].cat_name;
        splitItem = splitItem.split('-');
        newHtml += `<li class="first-list-view">
                        <a href="javascript:void(0);" title="click here">
                        <div class="member-view-box">
                            <div class="member-image">
                                <p class="percent_view">`+listItems[lv1key].cat_value+`&nbsp;%</div>
                                <div class="member-details">
                                    <h3 class="main-title h5">`+splitItem['0']+`</h3>
                                </div>
                            </div>
                        </div>
                    </a>`;
        console.log(listItems[lv1key]['addDetailsItem'].length)
         if(listItems[lv1key]['addDetailsItem'].length !== 0){
            newHtml += `<ul class="lavel-2">`;
             var newObjectOfCategory = listItems[lv1key]['addDetailsItem'];
             $.each(newObjectOfCategory, function(lvt){
                newHtml += `<li class="sec-list-view">
                            <a href="javascript:void(0);">
                            <div class="member-view-box">
                                <div class="member-image">
                                    <p class="percent_view">`+newObjectOfCategory[lvt].cate_percent+`&nbsp;%</div>
                                    <div class="member-details">
                                        <h3 class="main-title h5">`+newObjectOfCategory[lvt].cat_type+`</h3>
                                    </div>
                                </div>
                            </div>
                        </a>`;
                 if(newObjectOfCategory[lvt]['cat_subtype']){
                    newHtml += `<ul class="lavel-3">`;
                    var lavelThirdObj = newObjectOfCategory[lvt]['cat_subtype'];
                        $.each(lavelThirdObj, function(lvl3k){
                            newHtml += `<li class="third-list-view">
                                            <a href="javascript:void(0);">
                                            <div class="member-view-box">
                                                <div class="member-image">
                                                    <p class="percent_view">`+lavelThirdObj[lvl3k].q_percent+`&nbsp;%</div>
                                                    <div class="member-details">
                                                        <h3 class="main-title h5">`+lavelThirdObj[lvl3k].question+`</h3>
                                                        <span class="badge">`+lavelThirdObj[lvl3k].matching+`</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </a>`;
                                        if(lavelThirdObj[lvl3k]['details']){
                                            newQuestionItems = lavelThirdObj[lvl3k]['details'];
                                            newHtml += `<ul class="active lavel-4">`;
                                            $.each(newQuestionItems, function(qkey){
                                                newHtml += `<li class="forth-list-view">
                                                            <a href="javascript:void(0);">
                                                            <div class="member-view-box">
                                                                <div class="member-image">
                                                                    <p class="percent_view">`+newQuestionItems[qkey].percent+`&nbsp;%</div>
                                                                    <div class="member-details">
                                                                        <h3 class="main-title h5">`+newQuestionItems[qkey].title+`</h3>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </a></li>`;
                                            })
                                            newHtml += `</ul></li>`;
                                        }
                        })
                    newHtml += `</ul></li>`;
                 }
             })
             newHtml += `</ul></li>`;

         }
    })
    newHtml += `</ul></li></ul>`;

    $('.genealogy-tree').append(newHtml);

    $('.genealogy-tree ul').hide();
    $('.genealogy-tree>ul').show();
    $('.genealogy-tree ul.active').show();
    $('.genealogy-tree li').on('click', function (e) {
        var children = $(this).find('> ul');
        if (children.is(":visible")) children.hide('fast').removeClass('active');
        else children.show('fast').addClass('active');
        e.stopPropagation();
    });

}


