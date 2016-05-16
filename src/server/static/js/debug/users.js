$(function() {
    var table = $('.usersTable');
    var usersLists = $('.usersList');

    var addUserToTable = function(user) {
        var row = $('<tr></tr>').data(user);

        // User ID
        row.append($('<td class="usersTable-userId"></td>')
            .text(user.id));

        // Username
        row.append($('<td></td>')
            .append($('<input type="text" class="form-control usersTable-userName" placeholder="Username">')
                .val(user.name)));

        // Save + Remove Button
        row.append($('<td></td>')
            .append($('<button type="submit" class="btn btn-primary usersTable-save">Save</button>'))
            .append($('<button type="submit" class="btn btn-danger usersTable-remove">Remove</button>')));

        table.append(row);
        usersLists.append($('<option class="usersList-user"></option>').attr('value', user.id).text(user.name))
    };

    // CREATE
    $('.usersTable-add').click(function() {
        var row = $(this).parent().parent();

        var username = row.find('.usersTable-add_username').val();

        if (username) {
            socket.emit('create_user', username);
        }
    });

    socket.on('create_user', function(user) {
        addUserToTable(user);
        $('.usersTable-add_username').val('');
    });

    // READ
    socket.on('get_users', function (users) {

        table.empty();
        $('.usersList-user').remove();

        users.forEach(addUserToTable);
    });

    // UPDATE
    $(document).on('click', '.usersTable-save', function() {
        var row = $(this).parent().parent();
        var id = row.find('.usersTable-userId').text();
        var name = row.find('.usersTable-userName').val();

        if (name !== row.data().name) {
            socket.emit('update_user', id, name);
            socket.once('update_user', function(user) {
                row.data(user);
                row.find('.usersTable-userName').val(user.name);
                $('option[value="' + user.id + '"').text(user.name);
            });
        } else {
            console.log('No Change to User');
        }
    });

    // DELETE
    $(document).on('click', '.usersTable-remove', function() {
        var row = $(this).parent().parent();
        var id = row.find('.usersTable-userId').text();

        socket.emit('delete_user', id);
        socket.once('delete_user', function(success) {
            if (success) {
                row.remove();
                $('option[value="' + id + '"').remove();
            }
        })
    });

    socket.emit('get_users');

});
