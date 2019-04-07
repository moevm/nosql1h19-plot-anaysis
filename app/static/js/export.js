$(document).ready(function() {
	$('#navbar').css('display', 'none');
	$.get('/export', function(data) {
		$('#navbar').css('display', 'block');
		alert('Загрузка завершена.');
	});
});