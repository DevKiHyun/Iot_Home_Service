var socket = io('192.168.100.131:8080/');
socket.on("mqtt", function(data){
  console.log(data);

  var value = data["value"]
  var check_div = document.getElementById(data["place"])

  if(check_div)
  {
    for(var key in value)
    {
      console.log(key + " " + value[key]);
      document.getElementById("sensor" + "_" + key).innerHTML = key ;
      document.getElementById("sensor" + "_" + key + "_value").innerHTML = value[key]
    }
  }
  else
  {
    console.log("Create New Div");

    var div = document.createElement("div");
    div.classList.add("card");
    div.classList.add("sensor");
    div.id = data["place"];

    var title_div = document.createElement("div");
    title_div.id = "sensor_title";

    div.appendChild(title_div);
    document.getElementById("sensor_card1").appendChild(div);
    document.getElementById("sensor_title").innerHTML = data["place"];

    for(var key in value)
    {
      console.log(key + " " + value[key]);
      var id = "sensor" + "_" + key;
      var data_div = document.createElement("div");
      data_div.id = id;

      div.appendChild(data_div);
      document.getElementById("sensor" + "_" + key).innerHTML = key ;
      document.getElementById("sensor" + "_" + key + "_value").innerHTML = value[key]
    }
  }
});
