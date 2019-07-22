import os, werkzeug
from flask import Flask, render_template, session

from views.file import data_blueprint
from views.alert import alert_blueprint

from models.rule_model import RuleModel
from data_handlers import o365_handler

app = Flask(__name__)
app.secret_key = os.urandom(64)
app.config.update(
    ADMIN=os.environ.get('ADMIN')
)


@app.route('/')
def home():
    return render_template('home.html')


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

    pass_rule = RuleModel(*pass_rule_format)
    pass_rule.replace_or_create_to_db({'type': pass_rule_format['type']}, pass_rule_format)
    raise_rule = RuleModel(*raise_rule_format)
    raise_rule.replace_or_create_to_db({'type': raise_rule_format['type']}, raise_rule_format)

temp = o365_handler.o365()
temp.file_parser()


app.register_blueprint(data_blueprint, url_prefix='/file')
app.register_blueprint(alert_blueprint, url_prefix='/alert')


if __name__ == '__main__':
    # app.run()
    app.run()