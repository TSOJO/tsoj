let counter = 0

function add_field() {
    counter++;
    $('#testcases-count').val(counter);
    let testcase_node = document.getElementById('testcase-div').cloneNode(true);
    testcase_node.id = '';
    testcase_node.style.display = 'block';
    let h5_node = testcase_node.getElementsByClassName('testcase-number')[0];
    h5_node.innerHTML = 'Testcase ' + counter;
    let input_node = testcase_node.getElementsByClassName('testcase-input')[0];
    input_node.name = 'input' + counter;
    let answer_node = testcase_node.getElementsByClassName('testcase-answer')[0];
    answer_node.name = 'answer' + counter;
    let testcase_container = document.getElementById('testcase-container');
    testcase_container.appendChild(testcase_node);
}

function remove_field(node) {
    counter--;
    $('#testcases-count').val(counter);
    let testcase_container = document.getElementById('testcase-container');
    testcase_container.removeChild(node);
    // reindex
    for (let i = 0; i < counter; i++) {
        let testcase_node = testcase_container.childNodes[i];
        let h5_node = testcase_node.getElementsByTagName('h5')[0];
        h5_node.innerHTML = 'Testcase ' + (i + 1);
        let input_node = testcase_node.getElementsByClassName('testcase-input')[0];
        console.log(input_node);
        input_node.name = input_node.name.slice(0, -1) + (i + 1);
        let answer_node = testcase_node.getElementsByClassName('testcase-answer')[0];
        answer_node.name = answer_node.name.slice(0, -1) + (i + 1);
    }
}

// Initialise code editor.
let editor = ace.edit('editor');
ace.config.set('basePath', 'https://cdn.jsdelivr.net/npm/ace-builds@1.13.1/src-noconflict/');
editor.setTheme("ace/theme/textmate");
editor.session.setMode("ace/mode/python");
// editor.session.setUseWrapMode(true);

editor.getSession().on('change', function () {
    $('textarea[name="generator-code"]').val(editor.getValue());
});

// Checkbox on changed
$('input[name="generator-checkbox"]').change(function () {
    if (this.checked) {
        $('#editor-group').show();
    } else {
        $('#editor-group').hide();
    }
});