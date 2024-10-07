from django import forms

from django.views.generic.edit import UpdateView


class EntryForm(forms.Form):
    title = forms.CharField(label="Title", max_length=100)
    content = forms.CharField(widget=forms.Textarea(attrs={"rows": "5"}))

