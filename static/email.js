function email_check(){
  var user_email = document.getElementsByName("user_email")[0].value
  var user_password = document.getElementsByName("user_password")[0].value

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
    var mail_id = user_email.substring(0,start);

    var mail_sub_cover = document.getElementById(host);
    if( mail_sub_cover == null)
    {
      var email = {};
      email[user_email] = user_password;
      var request = { "master": master , "request": {"email_check" : email} };

      socket.emit("to-worker", request);
    }
    else
    {
      var mail_sub_cell_list = mail_sub_cover.getElementsByTagName('div');
      var mail_sub_cell_id_list = [];

      for(var i=0; i < mail_sub_cell_list.length; i++)
        mail_sub_cell_id_list.push(mail_sub_cell_list[i].id);

      if(mail_sub_cell_id_list.indexOf(mail_id) == -1)
      {
        var email = {};
        email[user_email] = user_password;
        var request = { "master": master , "request": {"email_check" : email} };

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

function responses_email_check(master, data, success){
  if (success == true)
  {
    console.log(data);

    var mid = data.indexOf('@');
    var end = data.indexOf('.');
    var mail_id = data.substring(0,mid);
    var host_name = data.substring(mid+1,end);
    var domain = data.substring(end+1, data.length-1);

    var check_div = document.getElementById(host_name);
    if(check_div)
    {
      var mail_sub_cover = document.getElementById(host_name+"."+domain);
      var mail_sub_cell = document.createElement("div");
      mail_sub_cell.id = mail_id;
      mail_sub_cell.classList.add("mail_sub_cell");
      mail_sub_cell.innerHTML= mail_id;
      mail_sub_cover.appendChild(mail_sub_cell);
    }
    else
    {
      var mail_table = document.getElementsByClassName("mail_table")[0];
      var mail_main_cell = document.createElement("div");
      mail_main_cell.id = host_name;
      mail_main_cell.classList.add("mail_main_cell");
      mail_main_cell.onclick = function(){
        mail_click(host_name+"."+domain);
      };
      mail_main_cell.innerHTML = host;
      mail_table.appendChild(mail_main_cell);

      var mail_sub_cover = document.createElement("div");
      mail_sub_cover.id = host_name+"."+domain;
      mail_sub_cover.classList.add("mail_sub_cover");
      mail_table.appendChild(mail_sub_cover);

      var mail_sub_cell = document.createElement("div");
      mail_sub_cell.id = mail_id;
      mail_sub_cell.classList.add("mail_sub_cell");
      mail_sub_cell.innerHTML = mail_id;
      mail_sub_cover.appendChild(mail_sub_cell);
    }
  }
  else
  {
    alert("Can't login. Please check the email or Worker.py");
  }
}

function mail_click(host){
  var mail_sub_cover = document.getElementById(host);
  mail_sub_cover.classList.toggle("show");
}
