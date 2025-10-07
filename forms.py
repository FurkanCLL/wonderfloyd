from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField, HiddenField, TextAreaField
from wtforms.validators import DataRequired, URL, Optional
from wtforms.validators import Email, Length
from flask_ckeditor import CKEditorField
from wtforms.widgets import ListWidget, CheckboxInput
from flask_wtf.file import FileField, FileAllowed

# Custom checkbox field for categories
class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

# WTForm for creating or editing a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[Optional(), URL()])
    cover_image = FileField("Upload Cover Image", validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'webp'], "Only image files are allowed.")
    ])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    categories = MultiCheckboxField("Categories", coerce=int)
    submit = SubmitField("Submit Post")

class ContactForm(FlaskForm):
    # Basic fields
    name = StringField("Your Name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Your Email", validators=[DataRequired(), Email(), Length(max=254)])
    subject = StringField("Subject", validators=[Optional(), Length(max=160)])
    message = TextAreaField("Message", validators=[DataRequired(), Length(min=10, max=2000)])

    website = HiddenField()

    submit = SubmitField("Send Message")
