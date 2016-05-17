$(function() {
    var table = $('.sessionsTable');
    var sessionsLists = $('.sessionsList');

    var addSessionToTable = function(session) {
        var row = $('<tr></tr>').data(session);

        // Session ID
        row.append($('<td class="sessionsTable-sessionId"></td>')
            .text(session.id));

        // Session Name
        row.append($('<td></td>')
            .append($('<input type="text" class="form-control sessionsTable-sessionName" placeholder="Name">')
                .val(session.name)));

        // Session Description
        row.append($('<td></td>')
            .append($('<input type="text" class="form-control sessionsTable-sessionDescription" placeholder="Description">')
                .val(session.description)));

        // Save + Remove Button
        row.append($('<td></td>')
            .append($('<button type="submit" class="btn btn-primary sessionsTable-save">Save</button>'))
            .append($('<button type="submit" class="btn btn-danger sessionsTable-remove">Remove</button>')));

        table.append(row);
        sessionsLists.append($('<option class="sessionsList-session"></option>')
            .attr('value', session.id)
            .text(session.name))
    };

    // CREATE
    $('.sessionsTable-add').click(function() {
        var row = $(this).parent().parent();

        var name = row.find('.sessionsTable-add_name').val();
        var description = row.find('.sessionsTable-add_description').val();

        if (name && description) {
            socket.emit('create_session', name, description);
        }
    });

    socket.on('create_session', function(session) {
        addSessionToTable(session);
        $('.sessionsTable-add_name').val('');
        $('.sessionsTable-add_description').val('');
    });

    // READ
    socket.on('get_sessions', function (sessions) {

        table.empty();
        $('.sessionsList-session').remove();

        sessions.forEach(addSessionToTable);
    });

    // UPDATE
    $(document).on('click', '.sessionsTable-save', function() {
        var row = $(this).parent().parent();
        var id = row.find('.sessionsTable-sessionId').text();
        var name = row.find('.sessionsTable-sessionName').val();
        var description = row.find('.sessionsTable-sessionDescription').val();

        var oldValue = row.data();

        if (name !== oldValue.name || description !== oldValue.description) {
            socket.emit('update_session', id, name, description);
            socket.once('update_session', function(session) {
                row.data(session);
                row.find('.sessionsTable-sessionName').val(session.name);
                row.find('.sessionsTable-sessionDescription').val(session.description);
                $('option[value="' + session.id + '"').text(session.name);
            });
        } else {
            console.log('No Change to User');
        }
    });

    // DELETE
    $(document).on('click', '.sessionsTable-remove', function() {
        var row = $(this).parent().parent();
        var id = row.find('.sessionsTable-sessionId').text();

        socket.emit('delete_session', id);
        socket.once('delete_session', function(success) {
            if (success) {
                row.remove();
                $('option[value="' + id + '"').remove();
            }
        })
    });

    socket.emit('get_sessions');

});
