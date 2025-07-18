from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField
from wtforms.widgets import ListWidget, CheckboxInput

# Custom checkbox field for categories
class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

# WTForm for creating or editing a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    categories = MultiCheckboxField("Categories", coerce=int)  # 🌟 Çoklu seçim alanı
    submit = SubmitField("Submit Post")
