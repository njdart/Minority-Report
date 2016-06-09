$(function() {
   $("#purge-users").on("click", function(){
       console.log("Purging Users table");
       socket.emit("purge_users");
   });

   $("#purge-sessions").on("click", function(){
       console.log("Purging Sessions table");
       socket.emit("purge_sessions");
   });

   $("#purge-instance-configurations").on("click", function(){
       console.log("Purging Instance Configurations table");
       socket.emit("purge_instance_configurations");
   });

   $("#purge-images").on("click", function(){
       console.log("Purging Images table");
       socket.emit("purge_images");
   });

   $("#purge-canvases").on("click", function(){
       console.log("Purging Canvases table");
       socket.emit("purge_canvases");
   });

   $("#purge-stickyNotes").on("click", function(){
       console.log("Purging stickyNotes table");
       socket.emit("purge_stickyNotes");
   });

   $("#purge-josh").on("click", function(){
       console.log("Purging connections, canvases and stickyNotes");
       socket.emit("purge_connections");
       socket.emit("purge_canvases");
       socket.emit("purge_stickyNotes");
   });

   $("#purge-josh-inverse").on("click", function(){
       console.log("Purging users, sessions, instance configurations and images");
       socket.emit("purge_sessions");
       socket.emit("purge_users");
       socket.emit("purge_instance_configurations");
       socket.emit("purge_images");
   });

   $("#purge-all").on("click", function(){
       console.log("Nuking DB");
       socket.emit("purge_sessions");
       socket.emit("purge_canvases");
       socket.emit("purge_stickyNotes");
       socket.emit("purge_users");
       socket.emit("purge_instance_configurations");
       socket.emit("purge_images");
   });

    $("#purge-do-not-click").on("click", function(){
       alert("Told you not to");
       location.href = "http://dafk.net/what/";
   });

});