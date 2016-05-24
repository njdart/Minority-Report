$(function() {
    var canvas = $('.hudCanvas');

    var splash = $('.localStorageUnset');

    if (typeof(Storage) !== 'undefined') {

       var userId = localStorage.getItem('user');
       var sessionId = localStorage.getItem('session');
       console.log("user: " + userId);
       console.log("session: " + sessionId);
//     for now let's pretend

	//var user = "test";
	//var session = "test";

        if (!userId || !sessionId) {
            console.error('Either UserId or SessionId was not set:', userId, sessionId);
        } else {
            var socket = io();
            splash.hide();

            socket.on('connect', function() {

                socket.on('get_postits_by_session', function(postits) {
                    console.log(postits)
                });

                socket.emit('get_postits_by_session', sessionId);
            });

        }
    } else {
        console.error('Local Storage Not Available!');
    }
});
