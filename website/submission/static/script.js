function verdict_to_html(verdict) {
    // An example for the verdict object here is {verdict: 'AC', verdict_long: 'Accepted'}
    switch (verdict.verdict) {
        case 'AC':
            return ['<span class="badge rounded-pill text-bg-success d-inline-flex align-items-center">',
                        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check-circle" viewBox="0 0 16 16">',
                            '<path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"></path>',
                            '<path d="M10.97 4.97a.235.235 0 0 0-.02.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-1.071-1.05z"></path>',
                        '</svg>',
                        '&nbsp;' + verdict.verdict_long,
                    '</span>'].join('')
        case 'WJ':
            return ['<span class="badge rounded-pill text-bg-secondary d-inline-flex align-items-center">',
                        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-clockwise" viewBox="0 0 16 16">',
                            '<path fill-rule="evenodd" d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2v1z"></path>',
                            '<path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466z"></path>',
                        '</svg>',
                        '&nbsp;' + verdict.verdict_long,
                    '</span>'].join('')
        default:
            return ['<span class="badge rounded-pill text-bg-danger d-inline-flex align-items-center">',
                        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-circle" viewBox="0 0 16 16">',
                            '<path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"></path>',
                            '<path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"></path>',
                        '</svg>',
                        '&nbsp;' + verdict.verdict_long,
                    '</span>'].join('')
    }
}

function make_request() {
    var payload = {
        id: submission_id,
        testsCompleted: tests_completed
    };
    
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
            if (tests_completed == num_tests) {
                document.getElementById('final-verdict').innerHTML = verdict_to_html(data['finalVerdict']);
            } else {
                // For problems with only fast testcases, give judge some time so we don't DDOS it
                // (a request will be sent after every testcase has finished).
                setTimeout(make_request, 500);
            }
        })
}

function update_results(results) {
    for (let i = 0; i < results.length; i++) {
        document.getElementById('verdict' + (i+1)).innerHTML = verdict_to_html(results[i].verdict);
        if (results[i].verdict.verdict != 'WJ') {
            document.getElementById('time' + (i+1)).innerHTML = results[i].time + 'ms';
            document.getElementById('memory' + (i+1)).innerHTML = results[i].memory + ' KB';
        }
    }
}

// Use `onpageshow` instead of `$(document).ready()` so this runs even when user gets here by back button.
window.onpageshow = function(event) {
    // Initialise code editor.
    let editor = ace.edit('editor');
    ace.config.set('basePath', 'https://cdn.jsdelivr.net/npm/ace-builds@1.13.1/src-noconflict/');
    editor.setTheme("ace/theme/textmate");
    editor.session.setMode("ace/mode/python");
    editor.session.setUseWrapMode(true);
    // Readonly
    editor.setReadOnly(true);
    // Disable cursor
    editor.setOptions({readOnly: true, highlightActiveLine: false, highlightGutterLine: false});
    editor.renderer.$cursorLayer.element.style.display = "none"

    if (tests_completed != num_tests) {
        // For problems with only fast testcases, give judge some time so we don't DDOS it
        // (a request will be sent after every testcase has finished).
        setTimeout(make_request, 500);
    }
}
