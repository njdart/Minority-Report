$(function() {
    var canvas = $('.hudCanvas');

    var splash = $('.localStorageUnset');

    if (typeof(Storage) !== 'undefined') {

//        var user = localStorage.getItem('user');
//        var session = localStorage.getItem('session');
//        for now let's pretend

	var user = "test";
	var session = "test";

        if (!user || !session) {
            console.error('Either User or Session was not set:', user, session);
        } else {
            var socket = io();
            splash.hide();

            socket.on('connect', function() {

                socket.on('get_postits_by_session', function(postits) {
                    console.log(postits)
                });

                socket.emit('get_postits_by_session', session)
            });

        }
    } else {
        console.error('Local Storage Not Available!');
    }
});
