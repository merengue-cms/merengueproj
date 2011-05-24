
//$(document).ready(function (data) {
//	block_id = $("#usertimeline input").val();
//	alert(block_id);
//}(jQuery));


//$(document).ready(function (){
function refresh_usertimeline() {
	$(".tweet img").bind("mouseover", function() {
			block_id_usertimeline = $("#usertimeline input").val();
			alert(block_id_usertimeline);
			$.get("twitter/ajax/get_user_tweets/" + block_id_usertimeline, 
				  function(data){
					  alert(data);
					  $('#usertimeline div.tweetlist').html(data);
				  });
		});
}(jQuery);

function refresh_hashtagtimeline() {
$(".tweet img").bind("mouseover", function() {
	block_id_hashtagtimeline = $("#hashtagtimeline input").val();
	$.get("twitter/ajax/get_hashtag_tweets/" + block_id_hashtagtimeline,
		  function(data){
			  $('#hashtagtimeline div.tweetlist').html(data);
		  });
	});
}(jQuery);