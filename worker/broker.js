var server = require('http').createServer().listen(8080);
var io = require("socket.io").listen(server);

io.sockets.on("connection", function(socket_client){
    socket_client.on("connected", function(data){
      console.log(data + " connected");
    });

    socket_client.on("message", function(data){
      console.log(data);
    });

    socket_client.on("to-worker", function(data){
      var request_method = data["method"];

      console.log("'%s': Worker! please do '%s' method", data["master"], request_method);
      io.emit("Worker", data);
    });

    socket_client.on("to-master", function(data){
      var responses_method = data["method"];

      console.log("Worker: '%s'! here '%s' result", data["master"], responses_method);
      io.emit(data["master"], data);
    });
});
