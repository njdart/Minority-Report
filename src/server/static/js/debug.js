var socket = io();

// ==== Users ====
var usernamesTable = $('.usernames-tableBody');

// On add user button
$('body').on('click', '.usernames-add', function() {

    var row = $(this).parent().parent();
    var properties = {
        username: row.find('.usernames-username').val()
    };

    if (properties.username) {
        socket.emit('addUser', properties);
    }
});

// On username loose focus
$('body').on('focusout', '.usernames-username', function(){
    var children = $(this).parent().parent();

    var properties = {
        id: children.find('.usernames-id').val(),
        username: children.find('.usernames-username').val()
    };

    socket.emit('updateUser', properties)
});

// on user delete button
$('body').on('click', '.usernames-delete', function() {
    var row = $(this).parent().parent();
    var properties = {
        id: row.find('.usernames-id').val(),
        username: row.find('.usernames-username').val()
    };

    socket.emit('deleteUser', properties);
});

// on getUsers response
socket.on('getUsers', function(users) {

    $('usernames-userRow').remove();

    users.forEach(function(user) {
        var tr = $("<tr class='usernames-userRow'></tr>").insertBefore(usernamesTable.children().last());

        tr.append("<td><input class='usernames-id' type='number' disabled='disabled' value='" + user.id + "'/></td>");
        tr.append("<td><input class='usernames-username' type='text' value='" + user.username + "'/></td>");
        tr.append("<td><input class='usernames-delete' type='button' value='x'/></td>");
    })

});

// on addUser response
socket.on('addUser', function(user) {
    $('.usernames-userRow_new').find('.usernames-username').val('');

    var tr = $("<tr class='usernames-userRow'></tr>").insertBefore(usernamesTable.children().last());

    tr.append("<td><input class='usernames-id' type='number' disabled='disabled' value='" + user.id + "'/></td>");
    tr.append("<td><input class='usernames-username' type='text' value='" + user.username + "'/></td>");
    tr.append("<td><input class='usernames-delete' type='button' value='x'/></td>");
});

// on updateUser response
socket.on('updateUser', function(user) {
    $('.usernames-id').filter(function() { return this.value == user.id })
        .parent().parent()
        .find('.usernames-username').val(user.username);
});

// on deleteUser response
socket.on('deleteUser', function(user) {
    $('.usernames-id').filter(function() { return this.value == user.id })
        .parent().parent().remove();
});

socket.emit('getUsers');