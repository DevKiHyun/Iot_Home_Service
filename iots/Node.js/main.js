var server = require('http').createServer().listen(8080);
var mqtt = require('mqtt');

var io = require("socket.io").listen(server);
var mqtt_client = mqtt.connect('mqtt://192.168.0.13');

mqtt_client.on('connect', function(){
  mqtt_client.subscribe('#');
});

io.sockets.on("connection", function(socket_client){
    console.log("connected");
    mqtt_client.on("message", function (topic, message){
      var sensor_data = JSON.parse(message.toString());
      console.log(sensor_data);
      socket_client.emit("message", sensor_data);
    });

    socket_client.on("message", function(data){
        console.log(data);
    });
});
