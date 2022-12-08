let counter = 0

function add_field() {
    counter++;
    let testcase_html = document.getElementById('testcase_div').cloneNode(true);
    testcase_html.id = '';
    testcase_html.style.display = 'block';
    for (let child in testcase_html.childNodes)
}