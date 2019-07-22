import os, os.path
from flask import Flask, Blueprint, render_template, request, url_for, redirect, session, flash
from models.alert_model import AlertModel
from models.rule_model import RuleModel

alert_blueprint = Blueprint('alert', __name__)


base_path = os.path.dirname(os.path.realpath(__file__))
base_path = os.path.dirname(base_path)
upload_path = os.path.join(base_path, 'static/assets/csv_files')
process_path = os.path.join(base_path, 'static/assets/csv_export')


@alert_blueprint.route('/', methods=['GET', 'POST'])
def alert_index():
    alerts = AlertModel.all()
    all_users = []
    for alert in alerts:
        full_user_id = alert.UserId
        split_username = full_user_id.split('@')
        username = split_username[0]
        all_users.append(username)

    users = set(all_users)

    return render_template('alert/alert_index.html', users=users, title='Alerts')


@alert_blueprint.route('/user_alert/<string:user_id>')
def user_alert(user_id):
    email = user_id + '@plymouth.ac.uk'
    alerts = AlertModel.find_many_by('UserId', email)

    return render_template('alert/user_alert.html', user_id=user_id, email=email, alerts=alerts, title='Alerts')


@alert_blueprint.route('/rule_index', methods=['GET', 'POST'])
def rule_index():
    rules = RuleModel.all()
    if not rules:
        pass_rule_format = {
            'rule': "Empty",
            'type': 'pass'
        }

        raise_rule_format = {
            'rule': "Empty",
            'type': 'raise'
        }
        print(pass_rule_format)
        pass_rule = RuleModel(*pass_rule_format)
        pass_rule.replace_or_create_to_db({'type': pass_rule_format['type']}, pass_rule_format)
        raise_rule = RuleModel(*raise_rule_format)
        raise_rule.replace_or_create_to_db({'type': raise_rule_format['type']}, raise_rule_format)

    return render_template('alert/rule_index.html', rules=rules, title='Rules')


@alert_blueprint.route('/rule/<string:type>',  methods=['GET', 'POST'])
def rule_detail(type):
    rule = RuleModel.find_one_by('type', type)

    if request.method == 'POST':
        edited_rule = request.form['rule_input']

        rule.rule = edited_rule

        rule.save_to_db()
        flash(f'{rule.type} rule Updated', 'success')
        return redirect(url_for('alert.rule_index'))

    return render_template('alert/rule_detail.html', rule=rule, title='Rule')
