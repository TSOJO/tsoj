let problems_count = 0

function add_problem() {
    problems_count++;
    let this_id = 'problem' + problems_count;
    var selected_problem_id = $('#problem-selector').val();
    const container = document.getElementById('problem-container');
    const wrapper = document.createElement('div');
    wrapper.setAttribute('id', this_id);
    wrapper.innerHTML = [
        '<div class="card mb-3" aria-hidden="true">',
        '   <div class="card-body">',
        '       <h5 class="card-title placeholder-glow">',
        '           <span class="placeholder col-3"></span>',
        '       </h5>',
        '       <p class="card-text placeholder-glow">',
        '           <span class="placeholder col-7"></span>',
        '       </p>',
        '       <a href="#" tabindex="-1" class="btn btn-primary disabled placeholder col-1"></a>',
        '       <button type="button" class="btn btn-danger disabled placeholder col-1"></button>',
        '   </div>',
        '</div>'
    ].join('');
    container.append(wrapper);
    fetch('/api/db/problem/' + selected_problem_id)
        .then(response => response.json())
        .then(data => {
            document.getElementById(this_id).remove();
            const wrapper_new = document.createElement('div');
            wrapper_new.setAttribute('id', this_id);
            wrapper_new.innerHTML = [
                '<div class="card mb-3" aria-hidden="true">',
                '   <div class="card-body">',
                '       <h5 class="card-title">',
                '           ' + data['id'] + ': ' + data['name'],
                '       </h5>',
                '       <p class="card-text">',
                '           ' + data['description'],
                '       </p>',
                '       <a href="/problem/' + data['id'] + '" class="btn btn-primary">View</a>',
                '       <button type="button" class="btn btn-danger" onclick="remove_problem(\'' + this_id + '\')">Remove</button>',
                '   </div>',
                '</div>',
                '<input type="hidden" name="' + this_id + '" value="' + data['id'] + '" />'
            ].join('');
            container.append(wrapper_new);
        })
}

function remove_problem(id) {
    document.getElementById(id).remove();
}