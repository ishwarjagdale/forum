from django import forms


class SignUpForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, min_length=6)
    confirm_password = forms.CharField(widget=forms.PasswordInput, min_length=6)


class LogInForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, min_length=6)


class NewThreadForm(forms.Form):
    topic = forms.CharField(required=True)
    content = forms.CharField(required=True)
    tags = forms.CharField(required=False)


class NewCommentForm(forms.Form):
    comment = forms.CharField(required=True, min_length=0, max_length=500)
