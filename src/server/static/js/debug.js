var socket = io();

var body = $('body');
var usernamesTable = $('.usernames-tableBody');
var imagesTable = $('.images-tableBody');

var users = [];
var images = [];

function updateUsers() {
    console.log('Updating Users');
    $('.usernames-userRow').remove();
    var template = $('.usernames-tableBody > .table-row_template');

    users.forEach(function(user) {
        var tr = template.clone();
        tr.removeClass('table-row_template');
        tr.addClass('usernames-userRow');
        $(tr).insertBefore(usernamesTable.children().last());

        tr.find('.usernames-id').text(user.id);
        tr.find('.usernames-username').val(user.username);
        tr.find('.usernames-delete').val('x');

        $('.user-select').append($('<option></option>')
            .attr('value', user.id)
            .text(user.username));
    })
}

function updateImages() {
    console.log('Updating Images');
    $('.images-imageRow').remove();
    var template = $('.images-tableBody > .table-row_template');

    images.forEach(function(image) {
        var tr = template.clone();
        tr.removeClass('table-row_template');
        tr.addClass('images-imageRow');

        $(tr).insertBefore(imagesTable.children().last());
        tr.find('.images-id').text(image.id);
        tr.find('.images-image').attr('src', 'api/images/' + image.id);
        tr.find('.images-user').val(image.user);
        tr.find('.images-timestamp').val(new Date(image.timestamp).toISOString());
    })
}

body.on("click", ".force-canvas-send", function()
{
    socket.emit("updateCanvas", {});
});

// On add user button
body.on('click', '.usernames-add', function() {

    var properties = {
        username: $('.usernames-username_new').val()
    };

    console.log('Creating User', properties);
    if (properties.username) {
        socket.emit('addUser', properties);
    }
});

// On username loose focus
body.on('focusout', '.usernames-username', function(){
    var children = $(this).parent().parent();

    var properties = {
        id: children.find('.usernames-id').text(),
        username: children.find('.usernames-username').val()
    };

    console.log(properties);

    socket.emit('updateUser', properties)
});

// On username loose focus
body.on('focusout', '.images-timestamp', function(){
    var children = $(this).parent().parent();

    var properties = {
        id: children.find('.images-id').text(),
        timestamp: children.find('.images-timestamp').val()
    };

    console.log(properties);

    socket.emit('updateImage', properties)
});

// on user delete button
body.on('click', '.usernames-remove', function() {
    var row = $(this).parent().parent();
    var properties = {
        id: row.find('.usernames-id').text(),
        username: row.find('.usernames-username').val()
    };
    console.log('Deleting User', properties);
    socket.emit('deleteUser', properties);
});

body.on('click', '.images-add', function() {
    var row = $(this).parent().parent();
    var files = row.find('.images-file').prop('files');

    var properties = {
        user: parseInt(row.find('.images-user').val()),
        timestamp: new Date(row.find('.images-timestamp').val()).toISOString()
    };

    if (properties.timestamp && properties.user > 0 && files.length > 0) {
        properties.timestamp = new Date(properties.timestamp);
        var file = files[0];
        properties.name = file.name;

        var fr = new FileReader();
        fr.addEventListener('loadend', function() {
            console.log('fr loaded, file is', fr.result.byteLength, 'bytes long');
            properties.file = fr.result;
            socket.emit('addImage', properties);
        });
        fr.addEventListener('progress', function(event) {
            console.log('fr progress', (100 * (event.loaded/event.total)), '%');
        });

        fr.readAsArrayBuffer(file);
    } else {
        console.log('Not uploading, missing details');
        return
    }

    console.log(properties);
});

// on user delete button
body.on('click', '.images-remove', function() {
    var row = $(this).parent().parent();
    var properties = {
        id: row.find('.images-id').text()
    };
    console.log('Deleting image', properties);
    socket.emit('deleteImage', properties);
});

// Show image
body.on('click', '.images-id', function() {
    $(this).parent().find('.images-image').toggle()
});

// on getUsers response
socket.on('getUsers', function(data) {
    console.log('getUsers', arguments);
    users = data;
    updateUsers()
});

// on addUser response, get fresh users list
socket.on('addUser', function() {
    console.log('addUser', arguments);
    $('.usernames-username_new').val('');
    socket.emit('getUsers');
});

// on updateUser response, get fresh users list
socket.on('updateUser', function() {
    console.log('updateUser', arguments);
    socket.emit('getUsers');
});

// on deleteUser response, get fresh users list
socket.on('deleteUser', function() {
    console.log('deleteUser', arguments);
    socket.emit('getUsers');
});

socket.on('addImage', function() {
    console.log('addImage', arguments);
    $('.images-image_new').val('');
    socket.emit('getImages');
});

socket.on('getImages', function(data) {
    console.log('getImages', arguments);
    images = data;
    updateImages();
});

socket.on('updateImage', function(data) {
    console.log('updateTimestamp', arguments);
    socket.emit('getImages');
});

socket.on('deleteImage', function(data) {
    console.log('deleteImage', arguments);
    socket.emit('getImages');
});

socket.emit('getUsers');
socket.emit('getImages');