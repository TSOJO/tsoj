function make_request() {
    var payload = {
        id: submission_id,
        testsCompleted: tests_completed
    };
    
    const placeholder = document.getElementById('gen-alert-placeholder');
    fetch("/api/grab-submission-change",
    {
        method: "POST",
        body: JSON.stringify(payload),
    })
        .then(response => response.json())
        .then(data => {
            tests_completed = data['testsCompleted']
            console.log(data);
            update_results(data['results']);
            if (data['testsCompleted'] == num_tests) {
                document.getElementById('final-verdict').innerHTML = data['finalVerdict'];
                console.log('Done!');
            } else {
                console.log(data['results']);
                console.log('Not quite yet');
                // Note API handles 'timeout'.
                make_request();
            }
        })
}

function update_results(results) {
    for (let i = 0; i < results.length; i++) {
        document.getElementById('verdict' + (i+1)).innerHTML = results[i].verdict.verdict;
        document.getElementById('time' + (i+1)).innerHTML = results[i].time + 'ms';
        document.getElementById('memory' + (i+1)).innerHTML = results[i].memory + ' KB';
    }
}

// Use `onpageshow` instead of `$(document).ready()` so this runs even when user gets here by back button.
window.onpageshow = function(event) {
    // alert(num_tests)
    console.log(tests_completed, num_tests)
    if (tests_completed != num_tests) {
        make_request()
    }
}
