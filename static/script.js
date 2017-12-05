$(document).ready(function () {
		$("#bet-button").attr("disabled",false);
		if(localStorage.getItem("remain_time_" + user_id) == null) {
    		remain_time = 1800;
    }
    else {
     		remain_time = localStorage["remain_time_" + user_id];
    }
    runCountdownTimer(remain_time);
});

function control_button() {
	document.getElementById('bet-button').disabled = true;
}

function updateRemainingTime(remaining_time) {
		var minutes = Math.floor(remaining_time/60)
		var seconds = remaining_time - minutes*60
		$("#remaining_time").val(minutes + " minutes " + seconds + " seconds ");
}

function runCountdownTimer(start_value) {
		updateRemainingTime(start_value);
		localStorage["remain_time_" + user_id] = start_value;
		if (start_value <= 0 || current_amount == 0) {
				$("#bet-button").attr("disabled","disabled");
				return;
		}
		setTimeout(function() {
				runCountdownTimer(start_value - 1);
		}, 1000);
}
