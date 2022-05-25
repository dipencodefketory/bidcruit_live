var html_editor
var css_editor
var js_editor


var E = $.noConflict(true);


var fontSize = E('.font-size input');


// load html
function loadTempHTML() {
    var body = E('#preview').contents().find('body');
    html = localStorage.getItem('htmlcode')
    body.html(html);
    loadTempCSS();
}
//load css
function loadTempCSS() {
    var head = E('#preview').contents().find('head'),
        reset = `<link rel="stylesheet" href="/static/assets/front_end_editor/css/reset.css">`;

    css = localStorage.getItem('csscode')
    head.html(reset + '<style>' + css + '</style>');
}
//load js
function loadTempJS() {
    var iframe = document.getElementById('preview'),
        preview;

    if (iframe.contentDocument) {
        preview = iframe.contentDocument;
    } else if (iframe.contentWindow) {
        preview = iframe.contentWindow.document;
    } else {
        preview = iframe.document;
    }

    js = localStorage.getItem('jscode')
    preview.open();
    preview.write(html + '<script>' + js + '<\/script>');
    preview.close();
}



function updateFontSize(editor, size) {
    editor.getWrapperElement().style['font-size'] = size + '%';
    editor.refresh();
}



E(document).ready(function () {

    var all_questions = getQuestionList();

    document.querySelector("#question_description_box").innerHTML = all_questions[0].description
    document.querySelector("#question_title_box").innerHTML = all_questions[0].title

    E('.paginate-btn').on('click',function(){
        E(this).prevAll('.paginate-btn').removeClass('active-que');
        E(this).nextAll('.paginate-btn').removeClass('active-que');
        E(this).addClass('active-que');
    });

    // INITIALIZE CODEMIRROR
    // ------------------------------
    //clean html csss and js code in local storage, if any
    localStorage.removeItem("htmlcode")
    localStorage.removeItem("csscode")
    localStorage.removeItem("jscode")

    // html code
    var editorHTML = document.editor = CodeMirror.fromTextArea(htmlcode, {
        mode: 'htmlmixed',
        readOnly: true,
        profile: 'html',
        keyMap: 'sublime',
        lineNumbers: true,
        lineWrapping: false,
        theme: 'dracula',
        tabSize: 4,
        indentUnit: 4,
        extraKeys: {
            'Tab': 'indentMore'
        },
        foldGutter: true,
        gutters: ['CodeMirror-lint-markers', 'CodeMirror-linenumbers', 'CodeMirror-foldgutter'],
        matchTags: {
            bothTags: true
        },
        matchBrackets: false,
        autoCloseTags: true,
        autoCloseBrackets: true,
        scrollbarStyle: 'overlay',
        styleActiveLine: true,
        showTrailingSpace: true,
        lint: false
    });
    html_editor = editorHTML

    // css code
    var editorCSS = document.editor = CodeMirror.fromTextArea(csscode, {
        mode: 'css',
        readOnly: true,
        profile: 'css',
        keyMap: 'sublime',
        lineNumbers: true,
        lineWrapping: false,
        theme: 'dracula',
        tabSize: 4,
        indentUnit: 4,
        extraKeys: {
            'Tab': 'indentMore'
        },
        foldGutter: true,
        gutters: ['CodeMirror-lint-markers', 'CodeMirror-linenumbers', 'CodeMirror-foldgutter'],
        matchBrackets: true,
        autoCloseBrackets: true,
        scrollbarStyle: 'overlay',
        styleActiveLine: true,
        showTrailingSpace: true,
        lint: false
    });
    css_editor = editorCSS
    // js code
    var editorJS = document.editor = CodeMirror.fromTextArea(jscode, {
        mode: 'javascript',
        readOnly: true,
        keyMap: 'sublime',
        lineNumbers: true,
        lineWrapping: false,
        theme: 'dracula',
        tabSize: 4,
        indentUnit: 4,
        extraKeys: {
            'Tab': 'indentMore'
        },
        foldGutter: true,
        gutters: ['CodeMirror-lint-markers', 'CodeMirror-linenumbers', 'CodeMirror-foldgutter'],
        matchBrackets: true,
        autoCloseBrackets: true,
        scrollbarStyle: 'overlay',
        styleActiveLine: true,
        showTrailingSpace: true,
        lint: false
    });
    js_editor= editorJS
    // font size
    var fontSize = E('.font-size input');
    function updateFontSize(editor, size) {
        editor.getWrapperElement().style['font-size'] = size + '%';
        editor.refresh();
    }


    // CODE LOADING
    // ------------------------------
    // code pane values
    var html, css, js;

    // load html
    function loadHTML() {
        var body = E('#preview').contents().find('body');
        html = editorHTML.getValue();
        body.html(html);
        loadCSS();
    }

    // start html
    function startHTML() {
        var iframe = document.getElementById('preview'),
            preview;

        if (iframe.contentDocument) {
            preview = iframe.contentDocument;
        } else if (iframe.contentWindow) {
            preview = iframe.contentWindow.document;
        } else {
            preview = iframe.document;
        }

        preview.open();
        preview.write(html);
        preview.close();
        loadCSS();
    }

    // load css
    function loadCSS() {
        var head = E('#preview').contents().find('head'),
            reset = `<link rel="stylesheet" href="/static/assets/front_end_editor/css/reset.css">`;

        css = editorCSS.getValue();
        head.html(reset + '<style>' + css + '</style>');
    }

    // load js
    function loadJS() {
        var iframe = document.getElementById('preview'),
            preview;

        if (iframe.contentDocument) {
            preview = iframe.contentDocument;
        } else if (iframe.contentWindow) {
            preview = iframe.contentWindow.document;
        } else {
            preview = iframe.document;
        }

        js = editorJS.getValue();
        preview.open();
        preview.write(html + '<script>' + js + '<\/script>');
        preview.close();
    }

    // run html
    startHTML();


    // DEFAULTS
    // ------------------------------
    defaultFontSize = '100';


//    // LOCAL STORAGE
//    // ------------------------------
//    // set default html value
//    if (localStorage.getItem('htmlcode') === null) {
//        localStorage.setItem('htmlcode', defaultHTML);
//    }
//
//    // set default css value
//    if (localStorage.getItem('csscode') === null) {
//        localStorage.setItem('csscode', defaultCSS);
//    }
//
//    // set default js value
//    if (localStorage.getItem('jscode') === null) {
//        localStorage.setItem('jscode', defaultJS);
//    }
//
    // set default font size
    if (localStorage.getItem('fontsize') === null) {
        localStorage.setItem('fontsize', defaultFontSize);
    }

    var answers = getCodingAnswersList();
    localStorage.setItem('htmlcode',answers[0]['fields']['html_code'])
    localStorage.setItem('csscode',answers[0]['fields']['css_code'])
    localStorage.setItem('jscode',answers[0]['fields']['js_code'])


    console.log('22222222222222',localStorage.getItem('htmlcode'))
    // load code values
    editorHTML.setValue(localStorage.getItem('htmlcode'));
    editorCSS.setValue(localStorage.getItem('csscode'));
    editorJS.setValue(localStorage.getItem('jscode'));

    // load font size
    fontSize.val(localStorage.getItem('fontsize'));


    // EDITOR UPDATES
    // ------------------------------
    // editor update (html)
    var delayHTML;
    editorHTML.on('change', function () {
        clearTimeout(delayHTML);
        delayHTML = setTimeout(loadHTML, 300);
        localStorage.setItem('htmlcode', editorHTML.getValue());
    });

    // editor update (css)
    editorCSS.on('change', function () {
        loadCSS();
        localStorage.setItem('csscode', editorCSS.getValue());
    });

    // editor update (js)
    editorJS.on('change', function () {
        localStorage.setItem('jscode', editorJS.getValue());
    });

    // run font size update
    updateFontSize(editorHTML, fontSize.val());
    updateFontSize(editorCSS, fontSize.val());
    updateFontSize(editorJS, fontSize.val());

    // run editor update (html)
    loadHTML();


    // DEPENDENCY INJECTION
    // ------------------------------
    // cdnjs typeahead search
    var query = E('.cdnjs-search .query');
    E.get('https://api.cdnjs.com/libraries?fields=version,description').done(function (data) {
        var searchData = data.results,
            search = new Bloodhound({
                datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
                queryTokenizer: Bloodhound.tokenizers.whitespace,
                local: searchData
            });

        query.typeahead(null, {
            display: 'name',
            name: 'search',
            source: search,
            limit: Infinity,
            templates: {
                empty: function () {
                    return '<p class="no-match">unable to match query!</p>';
                },
                suggestion: function (data) {
                    return '<p class="lib"><span class="name">' + data.name + '</span> <span class="version">' + data.version + '</span><br><span class="description">' + data.description + '</span></p>';
                }
            }
        }).on('typeahead:select', function (e, datum) {
            var latest = datum.latest;
            loadDep(latest);
            clearSearch();
        }).on('typeahead:change', function () {
            clearSearch();
        });
    }).fail(function () {
        alert('error getting cdnjs libraries!');
    });

    // clear typeahead search and close results list
    function clearSearch() {
        query.typeahead('val', '');
        query.typeahead('close');
    }

    // load dependency
    function loadDep(url) {
        var dep;
        if (url.indexOf('<') !== -1) {
            dep = url;
        } else {
            if (url.endsWith('.js')) {
                dep = '<script src="' + url + '"><\/script>';
            } else if (url.endsWith('.css')) {
                dep = '@import url("' + url + '");';
            }
        }

        function insertDep(elem, line) {
            elem.replaceRange(dep + '\n', {
                line: line,
                ch: 0
            });
        }

        if (html.indexOf(dep) !== -1 || css.indexOf(dep) !== -1) {
            alert('dependency already included!');
        } else {
            var line;
            if (url.endsWith('.js')) {
                line = html.split('<\/script>').length - 1;
                insertDep(editorHTML, line);
                E('.code-swap-html').click();
            } else if (url.endsWith('.css')) {
                line = css.split('@import').length - 1;
                insertDep(editorCSS, line);
                E('.code-swap-css').click();
            }

            alert('dependency added successfully!');
        }
    }


    // RESIZE FUNCTIONS
    // ------------------------------
    // drag handle to resize code pane
    var resizeHandle = E('.code-pane'),
        widthBox = E('.preview-width'),
        windowWidth = E(window).width();

    resizeHandle.resizable({
        handles: 'e',
        minWidth: 0,
        maxWidth: windowWidth - 16,
        create: function () {
            var currentWidth = resizeHandle.width(),
                previewWidth = windowWidth - currentWidth - 16;
            widthBox.text(previewWidth + 'px');
        },
        resize: function (e, ui) {
            var currentWidth = ui.size.width,
                previewWidth = windowWidth - currentWidth - 16;
            ui.element.next().css('width', windowWidth - currentWidth + 'px');
            ui.element.next().find('iframe').css('pointer-events', 'none');
            widthBox.show();
            if (currentWidth <= 0) {
                widthBox.text(windowWidth - 16 + 'px');
            } else {
                widthBox.text(previewWidth + 'px');
            }
        },
        stop: function (e, ui) {
            ui.element.next().find('iframe').css('pointer-events', 'inherit');
            widthBox.hide();
            editorHTML.refresh();
            editorCSS.refresh();
            editorJS.refresh();
        }
    });


    // GENERAL FUNCTIONS
    // ------------------------------
    // code pane and wrap button swapping
    function swapOn(elem) {
        elem.css({
            'position': 'relative',
            'visibility': 'visible'
        });
    }

    function swapOff(elem) {
        elem.css({
            'position': 'absolute',
            'visibility': 'hidden'
        });
    }

    E('.code-swap span').not('.toggle-view').on('click', function () {
        var codeHTML = E('.code-pane-html'),
            codeCSS = E('.code-pane-css'),
            codeJS = E('.code-pane-js'),
            wrapHTML = E('.toggle-lineWrapping.html'),
            wrapCSS = E('.toggle-lineWrapping.css'),
            wrapJS = E('.toggle-lineWrapping.js'),
            preview = E('.preview-pane');
            E('.code-swap-next-question').removeClass('active');
            E('.code-swap-previous-question').removeClass('active');

        E(this).addClass('active').siblings().removeClass('active');

        if (E(this).is(':contains("HTML")')) {
            swapOn(codeHTML);
            swapOn(wrapHTML);
            swapOff(codeCSS);
            swapOff(wrapCSS);
            swapOff(codeJS);
            swapOff(wrapJS);
            if (E(window).width() <= 800) {
                swapOff(preview);
            } else {
                swapOn(preview);
            }
        } else if (E(this).is(':contains("CSS")')) {
            swapOn(codeCSS);
            swapOn(wrapCSS);
            swapOff(codeHTML);
            swapOff(wrapHTML);
            swapOff(codeJS);
            swapOff(wrapJS);
            if (E(window).width() <= 800) {
                swapOff(preview);
            } else {
                swapOn(preview);
            }
        } else if (E(this).is(':contains("JS")')) {
            swapOn(codeJS);
            swapOn(wrapJS);
            swapOff(codeHTML);
            swapOff(wrapHTML);
            swapOff(codeCSS);
            swapOff(wrapCSS);
            if (E(window).width() <= 800) {
                swapOff(preview);
            } else {
                swapOn(preview);
            }
        } else if (E(this).is(':contains("preview")')) {
            swapOn(preview);
            swapOff(codeHTML);
            swapOff(wrapHTML);
            swapOff(codeCSS);
            swapOff(wrapCSS);
            swapOff(codeJS);
            swapOff(wrapJS);
        }
    });

    // expanding scrollbars
    var vScroll = E('.CodeMirror-overlayscroll-vertical'),
        hScroll = E('.CodeMirror-overlayscroll-horizontal');

    vScroll.on('mousedown', function () {
        E(this).addClass('hold');
    });

    hScroll.on('mousedown', function () {
        E(this).addClass('hold');
    });

    E(document).on('mouseup', function () {
        vScroll.removeClass('hold');
        hScroll.removeClass('hold');
    });

    // indent wrapped lines
    function indentWrappedLines(editor) {
        var charWidth = editor.defaultCharWidth(),
            basePadding = 4;
        editor.on('renderLine', function (cm, line, elt) {
            var off = CodeMirror.countColumn(line.text, null, cm.getOption('tabSize')) * charWidth;
            elt.style.textIndent = '-' + off + 'px';
            elt.style.paddingLeft = (basePadding + off) + 'px';
        });
    }

    // run indent wrapped lines
    indentWrappedLines(editorHTML);
    indentWrappedLines(editorCSS);
    indentWrappedLines(editorJS);


    // UTILITY FUNCTIONS
    // ------------------------------
    // font size
    fontSize.on('change keyup', function () {
        var size = E(this).val();
        updateFontSize(editorHTML, size);
        updateFontSize(editorCSS, size);
        updateFontSize(editorJS, size);
        localStorage.setItem('fontsize', size);
    });

    // toggle view
    E('.toggle-view').on('click', function () {
        E(this).toggleClass('enabled');
        if (E(this).hasClass('enabled')) {
            E(this).html('view<span class="fas fa-fw fa-chevron-up"></span>');
        } else {
            E(this).html('view<span class="fas fa-fw fa-chevron-down"></span>');
        }
    });

    // toggle tools
    E('.toggle-tools').on('click', function () {
        E(this).toggleClass('active');
        if (E(this).hasClass('active')) {
            E(this).html('tools<span class="fas fa-fw fa-chevron-up"></span>');
        } else {
            E(this).html('tools<span class="fas fa-fw fa-chevron-down"></span>');
        }
    });

    // toggle line wrapping (html)
    E('.toggle-lineWrapping.html').on('click', function () {
        E(this).toggleClass('active');
        if (E(this).hasClass('active')) {
            editorHTML.setOption('lineWrapping', true);
            E(this).html('wrap<span class="fas fa-fw fa-toggle-on"></span>');
        } else {
            editorHTML.setOption('lineWrapping', false);
            E(this).html('wrap<span class="fas fa-fw fa-toggle-off"></span>');
        }
    });

    // toggle line wrapping (css)
    E('.toggle-lineWrapping.css').on('click', function () {
        E(this).toggleClass('active');
        if (E(this).hasClass('active')) {
            editorCSS.setOption('lineWrapping', true);
            E(this).html('wrap<span class="fas fa-fw fa-toggle-on"></span>');
        } else {
            editorCSS.setOption('lineWrapping', false);
            E(this).html('wrap<span class="fas fa-fw fa-toggle-off"></span>');
        }
    });

    // toggle line wrapping (js)
    E('.toggle-lineWrapping.js').on('click', function () {
        E(this).toggleClass('active');
        if (E(this).hasClass('active')) {
            editorJS.setOption('lineWrapping', true);
            E(this).html('wrap<span class="fas fa-fw fa-toggle-on"></span>');
        } else {
            editorJS.setOption('lineWrapping', false);
            E(this).html('wrap<span class="fas fa-fw fa-toggle-off"></span>');
        }
    });

    // emmet
    E('.toggle-emmet').on('click', function () {
        E(this).toggleClass('active');
        if (E(this).hasClass('active')) {
            emmetCodeMirror(editorHTML);
            emmetCodeMirror(editorCSS);
            E(this).html('emmet<span class="fas fa-fw fa-toggle-on"></span>');
        } else {
            emmetCodeMirror.dispose(editorHTML);
            emmetCodeMirror.dispose(editorCSS);
            E(this).html('emmet<span class="fas fa-fw fa-toggle-off"></span>');
        }
    });

    // linting
    E('.toggle-lint').on('click', function () {
        E(this).toggleClass('active');
        if (E(this).hasClass('active')) {
            editorHTML.setOption('lint', true);
            editorCSS.setOption('lint', true);
            editorJS.setOption('lint', true);
            E(this).html('lint<span class="fas fa-fw fa-toggle-on"></span>');
        } else {
            editorHTML.setOption('lint', false);
            editorCSS.setOption('lint', false);
            editorJS.setOption('lint', false);
            E(this).html('lint<span class="fas fa-fw fa-toggle-off"></span>');
        }
    });

    // refresh editor
    E('.refresh-editor').on('click', function () {
        location.reload();
    });


    // run script
    E('.run-script').on('click', function () {
        loadJS();
        loadCSS();
        loadHTML();

        if (E(window).width() <= 800) {
            E('.toggle-preview').click();
        }
    });

    // save as html file
    E('.save').on('click', function () {
        var text = '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<link rel="stylesheet" href="https://rawgit.com/markhillard/Editor/gh-pages/css/reset.css">\n<style>\n' + editorCSS.getValue() + '\n</style>\n</head>\n<body>\n' + editorHTML.getValue() + '\n<script>\n' + editorJS.getValue() + '\n</script>\n</body>\n</html>\n',
            blob = new Blob([text], {
                type: 'text/html; charset=utf-8'
            });

        saveAs(blob, 'editor.html');
    });


    // REFRESH EDITOR
    // ------------------------------
    editorHTML.refresh();
    editorCSS.refresh();
    editorJS.refresh();

});
