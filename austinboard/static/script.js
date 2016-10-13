function confirm_deleting_post(post_id) {
	var sure = confirm("Are you sure you want to delete this post?");
	if (sure == true) {	
		location.href="/deletepost_"+post_id;
	} else {
		location.href="";
	}
	
}

function confirm_test() {
	var sure = confirm("Shit!!!");
	if (sure) {
		location.href="/test";
	}
}