function add_email(){
  var user_email = document.getElementById("user_email").value
  var user_password = document.getElementById("user_password").value

  var index = user_email.indexOf('@');
  if(!user_email)
  {
    console.log("Input email address");
  }
  else if (index == -1)
  {
    console.log("No @");
  }
  else if(user_email.indexOf('.') == -1)
  {
    console.log("Input Domain");
  }
  else if(!user_password)
  {
    console.log("Input password");
  }
  else
  {
    var start = user_email.indexOf('@');
    var end = user_email.indexOf('.');
    var host = user_email.substring(start+1,end);
    var email_id = user_email.substring(0,start);

    //dict {"master" : master, "method" : "email_check",
    //       "data" : { "user_email" : user_email, "user_password" : user_password } }
    var email_sub_cover = document.getElementById(host);
    if( email_sub_cover == null)
    {

      var email = {};
      email["email"] = user_email;
      email["password"] = user_password
      var request = { "master": master , "method": "add_email", "data" : email };

      socket.emit("to-worker", request);
    }
    else
    {
      var email_sub_cell_list = email_sub_cover.getElementsByTagName('div');
      var email_sub_cell_id_list = [];

      for(var i=0; i < email_sub_cell_list.length; i++)
        email_sub_cell_id_list.push(email_sub_cell_list[i].id);

      if(email_sub_cell_id_list.indexOf(email_id) == -1)
      {
        var email = {};
        email["email"] = user_email;
        email["password"] = user_password
        var request = { "master": master , "method": "add_email", "data" : email };

        socket.emit("to-worker", request);
      }
      else
      {
        console.log("already exists")
        alert("Already exists");
      }
    }
  }
}

function responses_add_email(master, data, success){
  if (success == true)
  {
    var mid = data.indexOf('@');
    var end = data.indexOf('.');
    var email_id = data.substring(0,mid);
    var host_name = data.substring(mid+1,end);
    var domain = data.substring(end+1, data.length-1);

    var check_div = document.getElementById(host_name);
    if(check_div)
    {
      var email_sub_cover = document.getElementById(host_name+"."+domain);
      var email_sub_cell = document.createElement("div");
      email_sub_cell.id = email_id;
      email_sub_cell.classList.add("email_sub_cell");
      email_sub_cell.innerHTML= email_id;
      email_sub_cover.appendChild(email_sub_cell);
    }
    else
    {
      var email_table = document.getElementsByClassName("email_table")[0];
      var email_main_cell = document.createElement("div");
      email_main_cell.id = host_name;
      email_main_cell.classList.add("email_main_cell");
      email_main_cell.onclick = function(){
        click_host(host_name+"."+domain);
      };
      email_main_cell.innerHTML = host_name;
      email_table.appendChild(email_main_cell);

      var email_sub_cover = document.createElement("div");
      email_sub_cover.id = host_name+"."+domain;
      email_sub_cover.classList.add("email_sub_cover");
      email_table.appendChild(email_sub_cover);

      var email_sub_cell = document.createElement("div");
      email_sub_cell.id = email_id;
      email_sub_cell.classList.add("mail_sub_cell");
      email_sub_cell.innerHTML = email_id;
      email_sub_cover.appendChild(email_sub_cell);
    }
  }
  else
  {
    alert("Can't login. Please check the email or Worker.py");
  }
}

function click_email(email){
  var email_box = document.getElementsByClassName("email_box");
  $('.email_box').css('display', 'block');
  $('.email_account').html(email);

  if($('.email_box_list').length)
  {
    $('.email_box_body').empty();
    $('.page_prev_button').empty();
    $('.page_num_index').empty();
    $('.page_next_button').empty();
  }

  if($('.email_folder_dropdown_content').length)
  {
    $('.email_folder').empty();
  }

  document.getElementsByClassName("email_mailbox_button")[0].onclick = function(){
    get_email_box(email);
  }

  var request = { "master": master , "method": "click_email", "data" : { "email" : email } };
  socket.emit("to-worker", request);
}

var mailbox;
var total_folder_list;
var current_email;
function responses_click_email(master, data, success) {
  if($('.email_folder_dropdown_content').length)
  {
    $('.email_folder').empty();
  }

  current_email = data["email"];
  var email_box_body = document.getElementsByClassName("email_box_body");
  var current_page = 1;
  var added_folder_list = data["added_folder_list"];
  total_folder_list = data["total_folder_list"];

  var email_folder_dropdown = document.createElement("div");
  var email_folder_dropdown_content = document.createElement("div");
  var email_add_folder_dropdown_content = document.createElement("div");
  $(email_folder_dropdown).addClass("email_folder_dropdown");
  $(email_folder_dropdown_content).addClass("email_folder_dropdown_content");
  $(email_add_folder_dropdown_content).addClass("email_add_folder_dropdown_content");
  $(".email_folder").append(email_folder_dropdown);
  $(".email_folder").append(email_folder_dropdown_content);
  $(".email_folder").append(email_add_folder_dropdown_content);

  //email_folder_dropdown_content
  if(added_folder_list)
  {
    for(var i = 0; i < added_folder_list.length; i++)
    {
      added_folder = added_folder_list[i];
      if(added_folder != 'INBOX')
      {
        var div = document.createElement("div");
        $(div).attr('id', added_folder);
        $(div).html(added_folder);
        $(div).addClass("email_folder_list");
        div.onclick = (function()
        {
          var click_folder = added_folder;
          return function(){
            change_folder(click_folder);
          }
        })();
        $(email_folder_dropdown_content).append(div);
      }
    }
    //email_folder_dropdown default => "INBOX"
    $(email_folder_dropdown).attr('id', 'INBOX');
    $(email_folder_dropdown).html('INBOX');
  }
  else
  {
    //email_folder_dropdown default => "Add folder"
    $(email_folder_dropdown).attr('id', 'Add folder');
    $(email_folder_dropdown).html('Add folder');
  }

  //email_folder_dropdown Click event
  email_folder_dropdown.onclick = function()
  {
    if($(email_add_folder_dropdown_content).css("display") == "block")
      $(email_add_folder_dropdown_content).css("display", "none");

    else if($(email_folder_dropdown_content).css("display") == 'none')
      $(email_folder_dropdown_content).css("display", "block");
    else
      $(email_folder_dropdown_content).css("display", "none");
  };

  //always last element in emial_folder_dropdown_content is "Add"
  var div = document.createElement("div");
  $(div).html("Add");
  $(div).addClass("email_folder_list");
  div.onclick = function()
  {
    $(email_folder_dropdown_content).css('display', 'none');
    $(email_add_folder_dropdown_content).css('display', 'block');
  };
  $(email_folder_dropdown_content).append(div);
  ///////////////////////////////////////////////////

  // email_add_folder_dropdown_content
  for (var i= 0; i < total_folder_list.length; i++)
  {
    var folder = total_folder_list[i];
    var div = document.createElement("div");
    $(div).html(folder);
    $(div).addClass("email_folder_list");
    div.onclick = function()
    {
      var add_folder = folder;
      return function(){
        var request = { "master" : master, "method" : "add_email_folder", "data" : { "email" : current_email, "add_folder" : add_folder } };
        socket.emit("to-worker", request);
        $('.email_add_folder_dropdown_content').css("display", "none");
      };
    }();
    $('.email_add_folder_dropdown_content').prepend(div);
  }
  ///////////////////////////////////////////////

  //email_box_list in email_box_body
  if(data["folder"])
  {
    mailbox = typeof mailbox !== 'undefined' ? mailbox : {};
    mailbox[current_email] = typeof mailbox[current_email] !== 'undefined' ? mailbox[current_email] : data["folder"];
    show_mailbox();
  }
}

function show_mailbox(page_num){
  $('.email_box_body').empty();
  var current_folder = $('.email_folder_dropdown').html();
  var current_mailbox = mailbox[current_email][current_folder]["mailbox"];
  var mailbox_len = mailbox[current_email][current_folder]["mailbox_index"].length;

  var page_num = typeof page_num !== 'undefined' ? page_num : 1; //default
  var total_page_num = ((mailbox_len % 50) == 0) ? parseInt(mailbox_len / 50) : parseInt(mailbox_len / 50) + 1;

  var start = 50*(page_num-1);
  var end = ((50*page_num) > mailbox_len) ? mailbox_len : 50*page_num;
  for(var i = start; i < end; i++)
  {
    var index = current_mailbox[i]["index"];
    var from = current_mailbox[i]["from"];//.replace(/</g,'(').replace(/>/g,')');
    var subject = current_mailbox[i]["subject"];
    var date = current_mailbox[i]["date"];
    var email_box_list = document.createElement("div");

    $(email_box_list).addClass("email_box_list");
    $(email_box_list).attr('id', index);
    $(email_box_list).off('click').on('click',function(index, from, subject, date){
      return function(){
        get_email_content(index, from, subject, date);
      };
    }(index, from, subject, date));
    var email_box_list_FROM = document.createElement("div");
    $(email_box_list_FROM).html(from);
    $(email_box_list_FROM).addClass("email_box_list_FROM");

    var email_box_list_SUBJECT = document.createElement("div");
    $(email_box_list_SUBJECT).html(subject);
    $(email_box_list_SUBJECT).addClass("email_box_list_SUBJECT");

    if(current_mailbox[i]["state"] == "unseen")
    {
      $(email_box_list_FROM).css("color", "rgb(4 ,89, 193)");
      $(email_box_list_SUBJECT).css("color", "rgb(4 ,89, 193)");
    }

    var email_box_list_DATE = document.createElement("div");
    $(email_box_list_DATE).html(date);
    $(email_box_list_DATE).addClass("email_box_list_DATE");

    $(email_box_list).append(email_box_list_FROM);
    $(email_box_list).append(email_box_list_SUBJECT);
    $(email_box_list).append(email_box_list_DATE);
    $('.email_box_body').append(email_box_list);
  }

  $('.page_num_index').html(start+'~'+end+'/'+mailbox_len);
  $('.page_prev_button').html('<');
  $('.page_prev_button').off('click').on('click', function(){
    if(page_num != 1)
      show_mailbox(page_num - 1);
  });
  $('.page_next_button').html('>');
  $('.page_next_button').off('click').on('click', function(){
    if(page_num != total_page_num)
      show_mailbox(page_num + 1);
  });
}

function responses_add_email_folder(master, data ,success){
  var added_folder = data["added_folder"];
  if(success == true)
  {
    if(document.getElementById("Add folder"))
    {
      $('.email_folder_dropdown').attr('id', added_folder);
      $('.email_folder_dropdown').html(added_folder);
    }
    else
    {
      change_folder(added_folder);
    }
  }
}

function get_email_box(){
  var folder = $('.email_folder_dropdown').html()
  var request = {"master" : master, "method" : "get_email_box",
             "data" : { "email" : current_email, "folder" : folder } };
  socket.emit("to-worker", request);
}

function responses_get_email_box(master, data, success){
  var email = data["email"];
  mailbox = typeof mailbox !== 'undefined' ? mailbox : {};
  mailbox[email] = typeof mailbox[email] !== 'undefined' ? mailbox[email] : {};
  if(success)
  {
    var email = data["email"];
    var current_folder = $('.email_folder_dropdown').html();
    mailbox[email][current_folder] = data["folder"][current_folder];
    show_mailbox();
  }
}

function get_email_content(index, from, subject, date){
  $('#email_main').css('display', 'none');
  $('#email_content').css('display', 'block');
  $('.email_content_main').css('height', '100%').css('height', '-=' + (42 + $('.email_content_header').height()));

  $('.email_content_SUBJECT').html(subject);
  $('.email_content_DATE').html(date);
  $('.email_content_FROM').html(from);

  var folder = $('.email_folder_dropdown').html();
  var request = { "master" : master, "method" : "get_email_content",
                  "data" : { "email" : current_email, "folder" : folder, "index" : index } };
  socket.emit("to-worker", request);
}

function responses_get_email_content(master, data, success){
  if(success)
  {
    var email_content = data["email_content"];
    $('.email_content_BODY').html(email_content);
  }
}

function click_host(host){
  var email_sub_cover = document.getElementById(host);
  email_sub_cover.classList.toggle("show");
}

function change_folder(folder){
  var email_folder_dropdown = document.getElementsByClassName("email_folder_dropdown")[0];
  var current_folder = email_folder_dropdown.innerHTML;

  // exclude clicked folder in email_folder_dropdown_content
  // change email_folder_dropdown with clicked folder
  if($('.email_box_list').length)
  {
    $('.email_box_body').empty();
    $('.page_prev_button').empty();
    $('.page_num_index').empty();
    $('.page_next_button').empty();
  }
  if(document.getElementById(folder))
    document.getElementById(folder).remove();
  $(email_folder_dropdown).attr('id', folder);
  $(email_folder_dropdown).html(folder);

  var div = document.createElement("div");
  $(div).attr('id', current_folder);
  $(div).html(current_folder);
  $(div).addClass("email_folder_list");
  div.onclick = function(current_folder){
    return function(){
      change_folder(current_folder);
    };
  }(current_folder);
  $('.email_folder_dropdown_content').prepend(div);
  $('.email_folder_dropdown_content').css('display', 'none');
  if(mailbox && mailbox[current_email][folder])
  {
    show_mailbox();
  }
}
