import markdown2
from django.http import HttpResponseRedirect
from django.core.files.storage import default_storage


from django.shortcuts import render, redirect
from django.views import generic

from .forms import EntryForm

from markdown2 import Markdown

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def get_entry(request, entry):
    markdowner = Markdown()
    entryPage = util.get_entry(entry)

    if entryPage is None:
        return render(request, "encyclopedia/notFound.html", {
            "title": entry
        })
    else:
        return render(request, "encyclopedia/entry.html", {
            "entry": markdowner.convert(entryPage),
            "title": entry
        })


def new_entry(request):
    if request.method == "GET":
        form = EntryForm()
        return render(request, "encyclopedia/new_entry.html",
                      {"form": form}
                      )

    if request.method == "POST":
        form = EntryForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']

            existing_entries = util.list_entries()

            if title in existing_entries:
                return render(request, "encyclopedia/new_entry.html",
                          {"form": form, "error_message": "Entry already exists."}
                          )

            else:
                content = f"# {title}\n\n{content}"
                util.save_entry(title, content)
                return redirect("encyclopedia:entry", entry=title)

        else:
            return render(request, "encyclopedia/new_entry.html",
                          {"form": form}
                          )

