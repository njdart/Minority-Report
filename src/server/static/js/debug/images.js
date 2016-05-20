$(function() {

    var table = $('.imagesTable');
    var imagesList = $('.imagesList');

    var addImageToTable = function(image) {
    console.log(image)
        var row = $('<tr></tr>').data(image);
    
        // Image ID
        row.append($('<td class="imagesTable-imageId"></td>')
            .append($('<p></p>')
                .text(image.id))
            .append($('<div class="form-inline"></div>')
                .append($('<div class="form-group"></div>')
                    .append($('<a class="btn btn-default" role="button">Raw</a>')
                        .attr('target', '_blank')
                        .attr('href', '/api/image/' + image.id)))
                .append($('<div class="form-group"></div>')
                    .append($('<a class="btn btn-default" role="button">Projection</a>')
                        .attr('target', '_blank')
                        .attr('href', '/api/projection/' + image.id)))));
    
        // Timestamp
        row.append($('<td></td>')
            .append($('<input type="text" class="form-control imagesTable-timestamp">')
                .val(new Date(image.timestamp).toISOString())));
    
        // Instance Configuration
        row.append($('<td></td>')
            .append($('<input type="text" class="form-control imagesTable-InstanceConfigurationId">')
                .val(image.instanceConfigurationId)));
    
        // Save + Remove Button
        row.append($('<td></td>')
            .append($('<button type="submit" class="btn btn-primary imagesTable-save">Save</button>'))
            .append($('<button type="submit" class="btn btn-danger imagesTable-remove">Remove</button>'))
            .append($('<button type="submit" class="btn btn-default imagesTable-generateCanvas">Generate Canvas</button>')));

        table.append(row);
        imagesList.append($('<option class="imagesList-session"></option>')
            .attr('value', image.id)
            .text(image.id))
    };

    // CREATE
    $('.imagesTable-add').click(function() {
        var row = $(this).parent().parent();

        var file = row.find('.imagesTable-add_image').prop('files');
        var timestamp = row.find('.imagesTable-add_timestamp').val();
        timestamp = (timestamp) ? new Date(timestamp) : new Date();
        var instanceConfigId = row.find('.imagesTable-add_instanceConfigId').val();

        if (timestamp && instanceConfigId && file.length > 0) {

            var fileReader = new FileReader();

            fileReader.addEventListener('loadend', function() {
                console.log('Uploading File (' + fileReader.result.byteLength, 'bytes)');
                socket.emit('create_image', fileReader.result, timestamp.toISOString(), instanceConfigId);
            });

            fileReader.readAsArrayBuffer(file[0]);
        }
    });

    $('.imagesTable-get').click(function() {
        var row = $(this).parent().parent();

        var host = row.find('.imagesTable-add_imageUri').val() ||  'localhost';
        var port = row.find('.imagesTable-add_imagePort').val() || 8080;
        var instanceConfigId = row.find('.imagesTable-add_instanceConfigId').val();

        localStorage.setItem('cameraHost', host);
        localStorage.setItem('cameraPort', port);

        if (host && port && instanceConfigId) {
            console.log(host);
            console.log(port);
            console.log(instanceConfigId);
            socket.emit('get_image', instanceConfigId, 'http://' + host + ':' + port);
        }

    });

    socket.on('create_image', function(image) {
        addImageToTable(image);
        $('.imagesTable-add_image').val('');
        $('.imagesTable-add_instanceConfigId').val('');
        $('.imagesTable-add_timestamp').val('');
    });

    // READ
    socket.on('get_images', function (images) {

        table.empty();
        $('.imagesList-image').remove();

        images.forEach(addImageToTable);
    });

    // UPDATE
    $(document).on('click', '.imagesTable-save', function() {
        var row = $(this).parent().parent();
        var id = row.find('.imagesTable-imageId').text();
        var timestamp = new Date(row.find('.imagesTable-timestamp').val()).toISOString();
        var instanceConfigurationId = row.find('.imagesTable-instanceConfigId').val();

        socket.emit('update_image', id, timestamp, instanceConfigurationId);
        socket.once('update_image', function(image) {
            row.data(image);
            row.find('.imagesTable-instanceConfigId').val(image.instanceConfigId);
            row.find('.imagesTable-timestamp').val(new Date(image.timestamp).toISOString());
            $('option[value="' + image.id + '"').text(image.id);
        });
    });

    // DELETE
    $(document).on('click', '.imagesTable-remove', function() {
        var row = $(this).parent().parent();
        var id = row.find('.imagesTable-imageId').text();

        socket.emit('delete_image', id);
        socket.once('delete_image', function(success) {
            if (success) {
                row.remove();
                $('option[value="' + id + '"').remove();
            }
        })
    });

    $(document).on('click', '.imagesTable-generateCanvas', function() {
        var row = $(this).parent().parent();
        var id = row.find('.imagesTable-imageId').text();
        var instanceConfigurationId = row.find('.imagesTable-instanceConfigId').val();

        socket.emit('generate_canvas', id, instanceConfigurationId)
    });

    socket.emit('get_images');
});