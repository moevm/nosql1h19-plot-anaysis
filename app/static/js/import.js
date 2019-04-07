$(document).ready(function() {
	$('#modal1').css('display', 'block');

	$('#btn-cancel').on('click', function() {
        $('#navbar').css('display', 'block');
		$('#fountainTextG').css('display', 'none');
		$('#status').text('Импорт отменен')
    });

    $('#btn-accept').on('click', function() {
        $('#modal1').css('display', 'none');
        $('#navbar').css('display', 'none');

        $.get('/import', function(data) {
			$('#navbar').css('display', 'block');
			$('#fountainTextG').css('display', 'none');
			$('#status').text('Загрузка завершена!')
		});
    });
});