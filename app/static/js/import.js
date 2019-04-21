$(document).ready(function() {
	$('#fountainTextG').css('display', 'none');
	var file;

	$('#file').on('change', function() {
		$('#status').text('');
	});

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
        $('#navbar').css('display', 'none');
        $('#btn-start-import-wrap').css('display', 'none');
        $('#fountainTextG').css('display', 'block');

        $("#file").prop("disabled", true);

        $('#status').text('Import of data about 34 Kb can take from 1 to 2 hours. Please wait.')

        $.get('/import', function(data) {
			$('#navbar').css('display', 'block');
			$('#fountainTextG').css('display', 'none');
			$('#status').text('Import completed')
		});
    });
});