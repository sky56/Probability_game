$(document).ready(function () {
		if(localStorage.getItem("remain_time") == null) {
    		remain_time = 1800;
    }
    else {
     		remain_time = localStorage["remain_time"];
    }
    runCountdownTimer(remain_time);
});

function updateRemainingTime(remaining_time) {
		var minutes = Math.floor(remaining_time/60)
		var seconds = remaining_time - minutes*60
		$("#remaining_time").val(minutes + " minutes " + seconds + " seconds ");
}

function runCountdownTimer(start_value) {
		updateRemainingTime(start_value);
		localStorage["remain_time"] = start_value;
		if (start_value <= 0) {
				$("#bet-button").attr("disabled","disabled");
				return;
		}
		setTimeout(function() {
				runCountdownTimer(start_value - 1);
		}, 1000);
}
