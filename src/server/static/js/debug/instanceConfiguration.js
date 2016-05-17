$(function() {
    var table = $('.instanceConfigsTable');
    var instanceConfigurationsLists = $('.instanceConfigsList');

    var addInstanceConfigToTable = function(instanceConfiguration) {
        var row = $('<tr></tr>').data(instanceConfiguration);

        // Instance Config ID
        row.append($('<td class="instanceConfigsTable-configId"></td>')
            .text(instanceConfiguration.id));

        // Session Id
        row.append($('<td></td>')
            .append($('<input type="text" class="form-control instanceConfigsTable-sessionId" placeholder="Session ID">')
                .val(instanceConfiguration.sessionId)));

        // User Id
        row.append($('<td></td>')
             .append($('<input type="text" class="form-control instanceConfigsTable-userId" placeholder="User ID">')
                 .val(instanceConfiguration.userId)));

        // kinect Host
        row.append($('<td></td>')
             .append($('<input type="text" class="form-control instanceConfigsTable-kinectHost" placeholder="Kinect Host">')
                 .val(instanceConfiguration.kinectHost)));

        // Save + Remove Button
        row.append($('<td></td>')
            .append($('<button type="submit" class="btn btn-primary instanceConfigsTable-save">Save</button>'))
            .append($('<button type="submit" class="btn btn-danger instanceConfigsTable-remove">Remove</button>')));

        table.append(row);
        instanceConfigurationsLists.append($('<option class="instanceConfigsTable-config"></option>')
            .attr('value', instanceConfiguration.id)
            .text(instanceConfiguration.id));
    };

    // CREATE
    $('.instanceConfigsTable-add').click(function() {
        var row = $(this).parent().parent();

        var sessionId = row.find('.instanceConfigsTable-add_sessionId').val();
        var userId = row.find('.instanceConfigsTable-add_userId').val();
        var kinectHost = row.find('.instanceConfigsTable-add_kinectHost').val();

        if (sessionId && userId && kinectHost) {
            socket.emit('create_instanceConfig', sessionId, userId, kinectHost);
        }
    });

    socket.on('create_instanceConfig', function(instanceConfig) {
        addInstanceConfigToTable(instanceConfig);
        $('.instanceConfigsTable-add_sessionId').val('');
        $('.instanceConfigsTable-add_userId').val('');
        $('.instanceConfigsTable-add_kinectHost').val('');
    });

    // READ
    socket.on('get_instanceConfigs', function (instanceConfigs) {

        table.empty();
        $('.instanceConfigsList-instanceConfig').remove();

        instanceConfigs.forEach(addInstanceConfigToTable);
    });

    // UPDATE
    $(document).on('click', '.instanceConfigsTable-save', function() {
        var row = $(this).parent().parent();
        var id = row.find('.instanceConfigsTable-configId').text();
        var sessionId = row.find('.instanceConfigsTable-sessionId').val();
        var userId = row.find('.instanceConfigsTable-userId').val();
        var kinectHost = row.find('.instanceConfigsTable-kinectHost').val();

        var oldValue = row.data();

        if (sessionId !== oldValue.sessionId || userId !== oldValue.userId || kinectHost !== oldValue.kinectHost) {
            socket.emit('update_instanceConfig', id, sessionId, userId, kinectHost);
            socket.once('update_session', function(instanceConfig) {
                row.data(instanceConfig);
                row.find('.sessionsTable-sessionId').val(instanceConfig.sessionId);
                row.find('.sessionsTable-userId').val(instanceConfig.userId);
                row.find('.sessionsTable-kinectHost').val(instanceConfig.kinectHost);
                $('option[value="' + instanceConfig.id + '"').text(instanceConfig.sessionId);
//            });
//        } else {
//            console.log('No Change to User');
//        }
//    });
//
//    // DELETE
//    $(document).on('click', '.sessionsTable-remove', function() {
//        var row = $(this).parent().parent();
//        var id = row.find('.sessionsTable-sessionId').text();
//
//        socket.emit('delete_session', id);
//        socket.once('delete_session', function(success) {
//            if (success) {
//                row.remove();
//                $('option[value="' + id + '"').remove();
//            }
//        })
//    });

    socket.emit('get_instanceConfigs');

});
