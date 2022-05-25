/*
Simple file manager front-end interface.

Realized features:
  Control panel
  Context menu
  Drag-n-Drop
  
*/

// 1 - Модель файловой системы
/*const root = [
    {
      name: 'css',
      type: 'folder',
      contains: [
        {
          name: 'style.css',
          type: 'file'
        },
        {
          name: 'header.css',
          type: 'file'
        },
        {
          name: 'footer.css',
          type: 'file'
        }
      ]
    },
    {
      name: 'js',
      type: 'folder',
      contains: [
        {
          name: 'slick',
          type: 'folder',
          contains: [
            {
              name: 'slick.min.js',
              type: 'file'
            },
            {
              name: 'slick.js',
              type: 'file'
            },
            {
              name: 'slick.css',
              type: 'file'
            }
          ]
        },
        {
          name: 'jquery',
          type: 'folder',
          contains: [
            {
              name: 'jquery.js',
              type: 'file'
            },
            {
              name: 'jquery.min.js',
              type: 'file'
            }
          ]
        }
      ]
    }
  ];*/

  setInterval(function(){ //sync within 700ms
    storageVisible();
  }, 700);

  function storageVisible(){
    if (localStorage.getItem('fileExplore') !== null) {
       dbConnection = true;
    } else {
        setNewArry = [{"name":"Resume","type":"folder","icon":"folder","permission":"denied","contains":[{"name":"bhavesh-resume-20102021.docx","type":"word","icon":"word"},{"name":"mohan-resume-14092021.docx","type":"file","icon":"word"},{"name":"anmol-03082021.docx","type":"file","icon":"pdf"},{"name":"imran-07072021.pdf","type":"file","icon":"pdf"}]},{"name":"Stages","type":"folder","icon":"folder","permission":"denied","contains":[{"name":"snap53241.png","type":"file","icon":"image"},{"name":"snap95421.jpg","type":"file","icon":"image"},{"name":"audio-2313663.mp3","type":"file","icon":"audio"},{"name":"audio-110024.mp3","type":"file","icon":"audio"},{"name":"new-snap156461.jpeg","type":"file","icon":"image"},{"name":"video-snapchat33214.mp4","type":"file","icon":"video"},{"name":"video-snapchat9311425.mp4","type":"file","icon":"video"},{"name":"video-snapchat39964115.mp4","type":"file","icon":"video"}]},{"name":"Chat","type":"folder","icon":"folder","permission":"denied","contains":[{"name":"chatbackup-2544121.pdf","type":"file","icon":"pdf"},{"name":"chatbackup-9541154.pdf","type":"file","icon":"pdf"},{"name":"chatbackup-0021356.pdf","type":"file","icon":"pdf"},{"name":"chatbackup-606422.docx","type":"file","icon":"word"},{"name":"chatbackup-722415.docx","type":"file","icon":"word"},{"name":"chatbackup-235541.pdf","type":"file","icon":"pdf"}]},{"name":"Requested Docs","type":"folder","icon":"folder","permission":"denied","contains":[{"name":"10th-marksheet-482512.pdf","type":"file","icon":"pdf"},{"name":"12th-marksheet-31514.pdf","type":"file","icon":"pdf"},{"name":"BE2021-degree-774548.pdf","type":"file","icon":"pdf"},{"name":"offerlatter-21102021.docx","type":"file","icon":"word"},{"name":"experienceletter-25092016.docx","type":"file","icon":"word"},{"name":"payslip-letter-235541.pdf","type":"file","icon":"pdf"}]},{"name":"Hiring","type":"folder","icon":"folder","permission":"denied","contains":[{"name":"10th-marksheet-482512.pdf","type":"file","icon":"pdf"},{"name":"12th-marksheet-31514.pdf","type":"file","icon":"pdf"},{"name":"BE2021-degree-774548.pdf","type":"file","icon":"pdf"},{"name":"offerlatter-21102021.docx","type":"file","icon":"word"},{"name":"experienceletter-25092016.docx","type":"file","icon":"word"},{"name":"payslip-letter-235541.pdf","type":"file","icon":"pdf"}]},{"name":"Other","type":"folder","icon":"folder","permission":"denied","contains":[{"name":"angular-appdebug.mp4","type":"file","icon":"video"},{"name":"python-automation.mp4","type":"file","icon":"video"},{"name":"quick-questions-1.mp3","type":"file","icon":"audio"},{"name":"quick-questions-2.mp3","type":"file","icon":"audio"},{"name":"quick-questions-3.mp3","type":"file","icon":"audio"},{"name":"quick-questions-4.mp3","type":"file","icon":"audio"},{"name":"UI-UX-design.mp4","type":"file","icon":"video"},{"name":"photoshop.mp4","type":"file","icon":"video"},{"name":"php.mp4","type":"file","icon":"video"}]}];

        localStorage.setItem("fileExplore",JSON.stringify(setNewArry));
    }
}

var root = JSON.parse(localStorage.getItem("fileExplore"))
  
  // 2 - функции имитации работы файловой системы
  
  let dir = root; // просматриваемая директория
  let path = [root]; // ссылочный путь к директории
  let pathString = ['..']; // строковый путь к директории
  
  let buffer = null, // буфер обмена
      cutPath = ''; // путь к вырезаемому файлу
  
  // Отображает содержимое директории
  function showDir() {
    let result = []
    dir.forEach((item)=>{
      result.push(item.name);
    });
    result.sort();
    return result.join(', ');
  }
  
  // Создает директорию
  function makeDir(name) {
  
   if (!!dir.find((i)=>i.name === name)) return false; // ничего не делаем, если такая папка уже есть
   /*let folder = { // болванка новой папки
    name: name,
    type: 'folder',
    contains: []
  };*/
    let folder = { // болванка новой папки
      name: name,
      type: 'folder',
      icon: 'folder',
      permission: "accepted",
      contains: []
    };
    
    dir.push(folder); 
    return true;
  }
  
  // Создает файл
  function makeFile(name) {
    if (!!dir.find((i)=>i.name === name)) return false;
    
    let file = {
      name: name,
      type: 'file'
    };
    
    dir.push(file);
    return true;
  }
  
  // Перемещение по директории (1 шаг)
  function changeDir(name) {
    // 1 - перемещение в корневую директорию
    if (name === '..') {
      dir = root;
      path = [root];
      pathString = ['..'];
      return true;
    }
    
    // 2 - перемещение в родительскую директорию
    if (name === '.') {
      if (path.length == 1) {
        dir = root;
        path = [root];
        pathString = ['..'];
      } else {
        dir = path[path.length - 1];
        path.pop();
        pathString.pop();
      }
      return true;
    }
    
    // 3 - перемещение в дочернюю директорию
    let newDir = dir.find((i)=>i.name === name);
    if (!!newDir && newDir.type === 'folder') {
      path.push(dir);
      pathString.push(name);
      dir = newDir.contains;
      return true;
    } 
    return false;
  }
  
  // Перемещение по пути, пошаговое выполнение функции changeDir
  function movePath(path) {
    let arr = path.split('/');
    
    arr.forEach((name)=>{
      changeDir(name);
    });
    
    return getPath();
  }
  
  // Получение строки текущего пути
  function getPath() {
    return pathString.join('/');
  }
  
  // Переименование файла/папки
  function rename(oldname, newname) {
    let item = dir.find((i)=>i.name === oldname);
    let isExist = dir.find((i)=>i.name === newname);
    if (!!item && !isExist) {
      item.name = newname;
      return true;
    } else return false;
  }
  
  //Удаление файла/папки
  function del(name) {
    let file = dir.findIndex((i)=>i.name === name);
    if (file >= 0) dir.splice(file, 1);
  }
  
  // Копирование файла/папки в буфер
  function copy(name) {
    let selected = dir.find((i)=>i.name === name);
    
    let copied = JSON.parse(JSON.stringify(selected)); // самый простой из обнаруженных мной способов глубокого клонирования 8)
    buffer = copied;
  }
  
  // Вставляет файл из буфера
  function paste() {
    if (!buffer) return false; // курим бамбук, если буфер пуст
    
    let file = buffer,
        fileName = file.name;
    
    let hasFile = !!(dir.find((i)=>i.name === fileName)); 
    // проверка на наличие файла с тем же именем. 
    // Если файл с таким именем в директории есть, добавляем в конец "copy"
    if (hasFile) {
      if (file.type == 'folder') {
        file.name = file.name + ' copy';
      } else {
        let splitted = file.name.split('.');
        if (splitted.length > 1) {
          file.name = splitted.slice(0, -1).join('.') + ' copy' + '.' + splitted[splitted.length - 1];
        } else {
          file.name = file.name + ' copy';
        }
      }
    }
    
    if (!!cutPath) { // удаляем старую копию, если файл вырезан
      let currentPath = getPath();
      
      let pathToCut = cutPath.split('/').slice(0,-1).join('/'),
          fileName = cutPath.split('/')[cutPath.split('/').length - 1];
      
      movePath(pathToCut);
      del(fileName);
      movePath(currentPath);
    }
    
    dir.push(file);
    buffer = null;
    return true;
  }
  
  // Вырезает файл в буфер
  function cut(name) {
    let file = dir.find((i)=>i.name === name);
    if (!!file) {
      copy(name);
      cutPath = getPath() + '/' + name;
    }
  }
  
  // Перемещение файла
  function move(file, to) {
    let currentDir = getPath();
    cut(file);
    movePath(to);
    paste();
    movePath(currentDir);
  }
  
  // 2 - Визуализация с применением jQuery
  
  function render() {
   
    $('#path-input').val(getPath());
    let explorer = $('.explorer');
    explorer.html(' ');
    let folders = dir.filter((i)=>i.type == 'folder').sort();

    let files = dir.filter((i)=>i.type == 'file').sort();

    // dir.filter(function(k,val) {
    //   console.log(k.type+'--'+val)
    // })

    folders.concat(files).forEach((item)=>{
      var customHtml = '';
      let premission =  item.permission == "denied" ? "false" : "true"
      let type = item.type == "file" ? "file" : "folder", name = item.name;
      let icon = item.icon;

      customHtml += `<div class="file" data-premission="`+premission+`">`;
      if(premission == 'true'){
        customHtml +=`<div class="btn-group">
          <a href="javascript:void(0);" class="option-dots" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
            <i class="bx bx-dots-vertical-rounded"></i>
          </a>
          <div class="dropdown-menu">
            <a class="dropdown-item editFile">
              <i class="fe fe-edit mr-2"></i> Edit
            </a>
            <a class="dropdown-item downloadFile" href="javascript:void(0);">
              <i class="fe fe-download mr-2"></i> Download
            </a>
            <a class="dropdown-item deleteFile">
              <i class="fe fe-trash mr-2"></i> Delete
            </a>
          </div>
        </div>`;
      }

      if(icon == 'pdf'){ customHtml += `<i class="far fa-file-${icon}"></i>`; } /*<i class="far fa-file-circle"></i>*/
      if(icon == 'word'){ customHtml += `<i class="far fa-file-${icon}"></i>`; } /*<i class="far fa-file-circle"></i>*/
      if(icon == 'image'){ customHtml += `<i class="far fa-file-${icon}"></i>`; } /*<i class="far fa-file-circle"></i>*/
      if(icon == 'video'){ customHtml += `<i class="far fa-file-${icon}"></i>`; } /*<i class="far fa-file-video"></i>*/
      if(icon == 'audio'){ customHtml += `<i class="far fa-file-${icon}"></i>`; } /*<i class="far fa-file-audio"></i>*/
      if(icon == 'folder'){ customHtml += `<i class="fas fa-${icon}"></i>`; }
      customHtml += `<div class="name `+type+`-type">${name}</name></div>`;

      //let block = // болванка иконки
         //$(`<div class="file"><i class="fas fa-${icon}"></i><div class="name">${name}</name></div>`);

      let block = $(customHtml);

      block.name = name;

      // тут же добавляем обработчики событий
    block.click(function(){ //single click event
        select($(this));
    });
    
    block.dblclick(function(){ //duble click event)
        unselect();
        let name = $(this).find('.name').html();
        movePath(name);
        render();
    });
      explorer.append(block);
      
    });
    
    // добавляем drag-n-drop
    
   /* $('.file').draggable({
      stop: function(){
        render();
        unselect();
      },
      start: function() {
      $(this).addClass('draggable');
        select($(this));
      }
    }).droppable({
      drop: function() {
        if ($(this).find('.ico-file')[0]) return;
        let dirname = $(this).find('.name').html();
        move(selected, dirname);
      }
    });*/
  }
  
  render();
  
  // Выделение файлов
  let selected = null;
  
  function select(elem) {
    $('.selected').removeClass('selected');
    elem.addClass('selected');
    
    let name = elem.find('.name').html();
    selected = name;
    $('#btn-del, #btn-rename, #btn-copy, #btn-cut').prop('disabled', false);
  }
  
  function unselect() {
    selected = null;
    $('.selected').removeClass('selected');
    $('#btn-del, #btn-rename, #btn-copy, #btn-cut').prop('disabled', true);
    hideContext();
  }
  
  // Кнопки панели управления и контекстного меню
  $('#path-btn').click(()=>{ // кнопка перемещения в адресной строке
    let path = $('#path-input').val();
    movePath(path);
    render();
  });
  
  $('#btn-home').click(()=>{ // возврат в корневую директорию
    movePath('..');
    render();
  });
  
  $('#btn-up').click(()=>{ // возврат в родительскую директорию
    movePath('.');
    render();
  });
  
  $('#btn-newdir, #btn-modal-mkdir').click(()=>{ // Новая папка
    let dirname = prompt('Directory name:', 'New Folder');
    if (dirname) {
      makeDir(dirname);
      render();
    }
  });
  
  $('#btn-newfile, #btn-modal-mkfile').click(()=>{ // Новый файл
    let filename = prompt('File name:', 'New File.txt');
    if (filename) {
      makeFile(filename);
      render();
    }
  });
  
  $('#btn-del, #btn-modal-del').click(()=>{ // Удаление
    //var selectorPermission = '';
    var activeDirList = $(document).find('.explorer .file')
    $(activeDirList).each(function(){
     if($(this).data('premission') == true){
        //selectorPermission = $(this).data('premission');
        //console.log("delete permission",selectorPermission)
        del(selected);
        render();
        unselect();
     }
    })

  });
  
  $('#btn-copy, #btn-modal-copy').click(()=>{ // Копировать
    copy(selected);
    $('#btn-paste, #btn-modal-paste').prop('disabled', false);
  });
  
  $('#btn-cut, #btn-modal-cut').click(()=>{ // вырезать
    cut(selected);
    $('#btn-paste, #btn-modal-paste').prop('disabled', false);
  });
  
  $('#btn-paste, #btn-modal-paste').click(()=>{ // вставить
    paste();
    render();
    unselect();
    $('#btn-paste, #btn-modal-paste').prop('disabled', true);
  });
  
  $('#btn-rename, #btn-modal-rename').click(()=>{ // переименовать
    let newName = prompt('New name:', selected);
    if (newName) {
      rename(selected, newName);
      unselect();
      render();
    }
  });
  
  $('.explorer').click((e)=>{ // Снятие выделения при клике на фон
     if (!e.target.closest('.file')) {
       unselect();
     }
  });

  
  // Контекстное меню
  let contextOpened = 0;
  
  $('.explorer').contextmenu(function(e){
    e.preventDefault();
    unselect();
    let menu;
    
    if (!e.target.closest('.file')) {
      menu = $('.contextmenu-dir');
    } else {
      menu = $('.contextmenu-files');
      e.target.click();
    }
    
    let x = e.pageX;
    let y = e.pageY;
    
    showContext(menu, x, y);
    
  });
  
  function showContext(elem, x, y) {
    if (contextOpened) {
      hideContext(show);
    } else {
      show();
    }
    
    function show() {
      elem.css({
          'top': y,
          'left': x
        }).slideDown("fast");
      contextOpened = 1;
    }
  }
  
  function hideContext(cb) {
    if (!cb) cb = function(){};
    
    $('.contextmenu').each(function(){
      $(this).slideUp("fast", cb);
    });
    contextOpened = 0;
  }

  $('.contextmenu').click(()=>{
    hideContext();
  })
