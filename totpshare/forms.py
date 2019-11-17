try:
    from flask_wtf import FlaskForm
    from wtforms import StringField, PasswordField, BooleanField, SubmitField
    from wtforms.validators import DataRequired
except:
    raise ImportError("Unable to access Crypto.Cipher")

class AddForm(FlaskForm):
    """ Form to add new tokens to the data store
    """
    id = StringField('id', validators=[DataRequired()])
    display_name = StringField('display_name', validators=[DataRequired()])
    secret = PasswordField('secret', validators=[DataRequired()])
    submit = SubmitField('Add')