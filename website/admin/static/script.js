let counter = 0

function add_field() {
    counter++;
    let testcase_node = document.getElementById('testcase-div').cloneNode(true);
    testcase_node.id = '';
    testcase_node.style.display = 'block';
    let h5_node = testcase_node.getElementsByTagName('h5')[0];
    h5_node.innerHTML = 'Testcase ' + counter;
    let input_nodes = testcase_node.getElementsByClassName('form-control');
    for (let i = 0; i < input_nodes.length; i++) {
        input_nodes[i].name = input_nodes[i].name + counter;
    }
    let testcase_container = document.getElementById('testcase-container');
    testcase_container.appendChild(testcase_node);
}

function remove_field(index) {
    let testcase_container = document.getElementById('testcase-container');
    testcase_container.removeChild(testcase_container.childNodes[index]);
    // reindex
    for (let i = 0; i < testcase_container.childNodes.length; i++) {
        let testcase_node = testcase_container.childNodes[i];
        let inputs = testcase_node.getElementsByTagName('input');
        for (let j = 0; j < inputs.length; j++) {
            inputs[j].name = inputs[j].name.replace(/\d+/, i);
        }
    }
}