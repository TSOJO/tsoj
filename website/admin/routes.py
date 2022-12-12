from flask import render_template, Blueprint, request, redirect, url_for
from typing import List
import asyncio

from website.models import Problem, Assignment
from isolate_wrapper import IsolateSandbox, Verdict, Testcase

admin_bp = Blueprint('admin_bp', __name__,
                     template_folder='templates',
                     static_folder='static')


@admin_bp.route('/')
def admin():
    return render_template('admin.html')


@admin_bp.route('/create/problem', methods=['GET', 'POST'])
def create_problem():
    if request.method == 'POST':
        # print(request.form)
        problem_info = {
            'id': request.form['id'],
            'name': request.form['name'],
            'description': request.form['description'],
            'time_limit': int(round(float(request.form['time-limit']) * 1000)),
            'memory_limit': int(round(float(request.form['memory-limit']) * 1024)),
        }
        testcases: List[Testcase] = []

        testcases_count = int(request.form['testcases-count'])
        for i in range(testcases_count):
            testcases.append(
                Testcase(request.form[f'input{i+1}'], request.form[f'answer{i+1}']))

        if 'generator-checkbox' in request.form:
            code = request.form['generator-code']
            verdict: Verdict = IsolateSandbox().generate_answer(
                code, testcases, problem_info['time_limit'], problem_info['memory_limit'])[0]
            if not verdict.is_ac():
                raise NotImplementedError()

        problem = Problem(**problem_info, testcases=testcases)
        asyncio.run(problem.save())

        # ? redirect to /problem/<id>/edit
        return redirect(url_for('admin_bp.admin'))
    return render_template('create_problem.html')


@admin_bp.route('/create/assignment', methods=['GET', 'POST'])
def create_assignment():
    if request.method == 'POST':
        new_assignment = Assignment([])
        for _, problem_id in request.form.to_dict().items():
            # Will only be `problemX`
            new_assignment.add_problem(problem_id)
        asyncio.run(new_assignment.save())
        # ? redirect to /assignments/ something something
        return redirect(url_for('admin_bp.admin'))
    problems = asyncio.run(Problem.find_all())
    return render_template('create_assignment.html', problems=problems)
