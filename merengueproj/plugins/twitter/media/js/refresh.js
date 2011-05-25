// # Copyright (c) 2010 by Yaco Sistemas 
// #
// # This file is part of Merengue. 
// #
// # Merengue is free software: you can redistribute it and/or modify 
// # it under the terms of the GNU Lesser General Public License as published by
// # the Free Software Foundation, either version 3 of the License, or 
// # (at your option) any later version.
// #
// # Merengue is distributed in the hope that it will be useful,
// # but WITHOUT ANY WARRANTY; without even the implied warranty of
// # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// # GNU Lesser General Public License for more details.
// #
// # You should have received a copy of the GNU Lesser General Public License
// # along with Merengue.  If not, see <http://www.gnu.org/licenses/>.


function refresh_usertimeline() {
	block_id_usertimeline = jQuery("#usertimeline input").val();
	jQuery.get("twitter/ajax/get_user_tweets/" + block_id_usertimeline, 
			   function(data){
				   jQuery('#usertimeline div#tweetlist').html(data);
			   });
}(jQuery);

function refresh_hashtagtimeline() {
	block_id_hashtagtimeline = jQuery("#hashtagtimeline input").val();
	jQuery.get("twitter/ajax/get_hashtag_tweets/" + block_id_hashtagtimeline,
			   function(data){
				   jQuery('#hashtagtimeline div#tweetlist').html(data);
			   });
}(jQuery);

setInterval("refresh_usertimeline()", 1000 * 60 * 5);
setInterval("refresh_hashtagtimeline()", 1000 * 90);