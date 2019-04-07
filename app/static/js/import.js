$(document).ready(function() {
	$('#navbar').css('display', 'none');
	$.get('/import', function(data) {
		$('#navbar').css('display', 'block');
		alert('Загрузка завершена.');
	});
});