$(document).ready(function() {
	$('#fountainTextG').css('display', 'none');
	var file;

	$('#start-import-btn').on('click', function() {
		file = $('#file').get(0).files[0];
		if (file) {
			$('#modal1').css('display', 'block');
		} else {
			$('#status').text('file not set');
		}
	});

	$('#btn-cancel').on('click', function() {
		$('#modal1').css('display', 'none');
        $('#navbar').css('display', 'block');
		$('#fountainTextG').css('display', 'none');
		$('#status').text('Import canceled')
    });

    $('#btn-accept').on('click', function() {
        $('#modal1').css('display', 'none');

        $("#file").prop("disabled", true);

        $('#status').text('Import of data about 34 Kb can take from 1 to 2 hours. Please wait.')

        var fd = new FormData;
        fd.append('csv_import_file', file, 'import.csv');

        $.ajax({
	        url: '/import',
	        data: fd,
	        processData: false,
	        contentType: false,
	        type: 'POST',
	        success: function (data) {
	        	$('#fountainTextG').css('display', 'block');
	        	$('#navbar').css('display', 'none');
        		$('#btn-start-import-wrap').css('display', 'none');
	            $.get('/import', function(data) {
					$('#navbar').css('display', 'block');
					$('#fountainTextG').css('display', 'none');
					$('#status').text('Import completed');
				}).fail(function() {
				    $('#status').text('Import failed. Try again.');
				    $('#navbar').css('display', 'block');
				    $('#fountainTextG').css('display', 'none');
				    $('#btn-start-import-wrap').css('display', 'block');
				    $("#file").prop("disabled", false);
				});
	        },
	        error: function(error) {
	        	console.log(error);
	        	$('#status').text('Cant load file on server');
	        }
    	});
    });
});