$(function() {
    var table = $('.instanceConfigsTable');
    var instanceConfigurationsLists = $('.instanceConfigsList');
    var coordUnpackRegexp = /^\(?\s*([0-9]{1,5})[,.:\- ]+([0-9]{1,5})\s*\)?$/g;

    var addInstanceConfigToTable = function(instanceConfiguration) {
        var row = $('<tr></tr>').data(instanceConfiguration);

        // Instance Config ID
        row.append($('<td class="instanceConfigsTable-configId"></td>')
            .text(instanceConfiguration.id));

        // details
        var form = $('<form></form>');
        form.append($('<div class="form-group"></div>')
            .append($('<label>Session</label>'))
            .append($('<input type="text" class="form-control instanceConfigsTable-sessionId" placeholder="Session ID">')
                .val(instanceConfiguration.sessionId)));

        form.append($('<div class="form-group"></div>')
            .append($('<label>User</label>'))
            .append($('<input type="text" class="form-control instanceConfigsTable-userId" placeholder="User ID">')
                .val(instanceConfiguration.userId)));

        var leftColumn = $('<div class="col-md-6"></div>');

        leftColumn.append($('<div class="form-group"></div>')
            .append($('<label>TopLeft as (x,y)</label>'))
            .append($('<input type="text" class="form-control instanceConfigsTable-topLeft" placeholder="(x, y)">')
                .val((instanceConfiguration.topLeft.x) ?
                        '(' + instanceConfiguration.topLeft.x + ',' + instanceConfiguration.topLeft.y + ')' :
                        '')));

        leftColumn.append($('<div class="form-group"></div>')
            .append($('<label>BottomLeft as (x,y)</label>'))
            .append($('<input type="text" class="form-control instanceConfigsTable-bottomLeft" placeholder="(x, y)">')
                .val((instanceConfiguration.bottomLeft.x) ?
                        '(' + instanceConfiguration.bottomLeft.x + ',' + instanceConfiguration.bottomLeft.y + ')' :
                        '')));

        leftColumn.append($('<div class="form-group"></div>')
            .append($('<label>Camera Host</label>'))
            .append($('<input type="text" class="form-control instanceConfigsTable-cameraHost">')
                .val(instanceConfiguration.camera.host)));

        leftColumn.append($('<div class="form-group"></div>')
            .append($('<label>Kinect Host</label>'))
            .append($('<input type="text" class="form-control instanceConfigsTable-kinectHost">')
                .val(instanceConfiguration.kinect.host)));

        var rightColumn = $('<div class="col-md-6"></div>');

        rightColumn.append($('<div class="form-group"></div>')
            .append($('<label>TopRight as (x,y)</label>'))
            .append($('<input type="text" class="form-control instanceConfigsTable-topRight" placeholder="(x, y)">')
                .val((instanceConfiguration.topRight.x) ?
                        '(' + instanceConfiguration.topRight.x + ',' + instanceConfiguration.topRight.y + ')' :
                        '')));

        rightColumn.append($('<div class="form-group"></div>')
            .append($('<label>BottomRight as (x,y)</label>'))
            .append($('<input type="text" class="form-control instanceConfigsTable-bottomRight" placeholder="(x, y)">')
                .val((instanceConfiguration.bottomRight.x) ?
                        '(' + instanceConfiguration.bottomRight.x + ',' + instanceConfiguration.bottomRight.y + ')' :
                        '')));

        rightColumn.append($('<div class="form-group"></div>')
            .append($('<label>Camera Port</label>'))
            .append($('<input type="text" class="form-control instanceConfigsTable-cameraPort">')
                .val(instanceConfiguration.camera.port)));

        rightColumn.append($('<div class="form-group"></div>')
            .append($('<label>Kinect Port</label>'))
            .append($('<input type="text" class="form-control instanceConfigsTable-kinectPort">')
                .val(instanceConfiguration.kinect.port)));

        form.append($('<div class="row"></div>')
            .append(leftColumn).append(rightColumn));

        row.append($('<td></td>').append(form));

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

        var topLeft = row.find('.instanceConfigsTable-add_topLeft').val().match(coordUnpackRegexp);
        var topRight = row.find('.instanceConfigsTable-add_topRight').val().match(coordUnpackRegexp);
        var bottomRight = row.find('.instanceConfigsTable-add_bottomRight').val().match(coordUnpackRegexp);
        var bottomLeft = row.find('.instanceConfigsTable-add_bottomLeft').val().match(coordUnpackRegexp);

        var data = {
            sessionId: row.find('.instanceConfigsTable-add_sessionId').val(),
            userId: row.find('.instanceConfigsTable-add_userId').val(),
            topLeft: {
                x: (topLeft) ? topLeft[1] : null,
                y: (topLeft) ? topLeft[2] : null
            },
            topRight: {
                x: (topRight) ? topRight[1] : null,
                y: (topRight) ? topRight[2] : null
            },
            bottomRight: {
                x: (bottomRight) ? bottomRight[1] : null,
                y: (bottomRight) ? bottomRight[2] : null
            },
            bottomLeft: {
                x: (bottomLeft) ? bottomLeft[1] : null,
                y: (bottomLeft) ? bottomLeft[2] : null
            },
            camera: {
                host: row.find('.instanceConfigsTable-add_cameraHost').val() || 'localhost',
                port: row.find('.instanceConfigsTable-add_cameraPort').val() || 8080
            },
            kinect: {
                host: row.find('.instanceConfigsTable-add_kinectHost').val() || 'localhost',
                port: row.find('.instanceConfigsTable-add_kinectPort').val() || 8081
            }
        };

        console.log(data);

        if (data.sessionId &&
            data.userId &&
            data.camera.host &&
            data.camera.port &&
            data.kinect.host &&
            data.kinect.port) {

            socket.emit('create_instance_configuration', data);
        }
    });

    socket.on('create_instance_configuration', function(instanceConfig) {
        addInstanceConfigToTable(instanceConfig);
        $('.instanceConfigsTable-add_sessionId').val('');
        $('.instanceConfigsTable-add_userId').val('');
        $('.instanceConfigsTable-add_kinectHost').val('');
    });

    // READ
    socket.on('get_instance_configurations', function (instanceConfigs) {
        console.log(instanceConfigs);
        table.empty();
        $('.instanceConfigsList-instanceConfig').remove();

        instanceConfigs.forEach(addInstanceConfigToTable);
    });

    // UPDATE
    $(document).on('click', '.instanceConfigsTable-save', function() {
        var row = $(this).parent().parent();

        var topLeft = row.find('.instanceConfigsTable-add_topLeft').val().match(coordUnpackRegexp);
        var topRight = row.find('.instanceConfigsTable-add_topRight').val().match(coordUnpackRegexp);
        var bottomRight = row.find('.instanceConfigsTable-add_bottomRight').val().match(coordUnpackRegexp);
        var bottomLeft = row.find('.instanceConfigsTable-add_bottomLeft').val().match(coordUnpackRegexp);

        var data = {
            sessionId: row.find('.instanceConfigsTable-add_sessionId').val(),
            userId: row.find('.instanceConfigsTable-add_userId').val(),
            topLeft: {
                x: (topLeft) ? topLeft[1] : null,
                y: (topLeft) ? topLeft[2] : null
            },
            topRight: {
                x: (topRight) ? topRight[1] : null,
                y: (topRight) ? topRight[2] : null
            },
            bottomRight: {
                x: (bottomRight) ? bottomRight[1] : null,
                y: (bottomRight) ? bottomRight[2] : null
            },
            bottomLeft: {
                x: (bottomLeft) ? bottomLeft[1] : null,
                y: (bottomLeft) ? bottomLeft[2] : null
            },
            camera: {
                host: row.find('.instanceConfigsTable-add_cameraHost').val() || 'localhost',
                port: row.find('.instanceConfigsTable-add_cameraPort').val() || 8080
            },
            kinect: {
                host: row.find('.instanceConfigsTable-add_kinectHost').val() || 'localhost',
                port: row.find('.instanceConfigsTable-add_kinectPort').val() || 8081
            }
        };

        socket.emit('update_instanceConfig', id, sessionId, userId, kinectHost);
        socket.once('update_session', function(instanceConfig) {
            row.data(instanceConfig);
            row.find('.sessionsTable-sessionId').val(instanceConfig.sessionId);
            row.find('.sessionsTable-userId').val(instanceConfig.userId);
            row.find('.sessionsTable-kinectHost').val(instanceConfig.kinectHost);
            $('option[value="' + instanceConfig.id + '"').text(instanceConfig.sessionId);
       });
   });

   // DELETE
   $(document).on('click', '.instanceConfigsTable-remove', function() {
       var row = $(this).parent().parent();
       var id = row.find('.instanceConfigsTable-configId').text();

       socket.emit('delete_instance_configuration', id);
       socket.once('delete_instance_configuration', function(success) {
           if (success) {
               row.remove();
               $('option[value="' + id + '"').remove();
           }
       })
   });

    socket.emit('get_instance_configurations');

});
