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
    print("In get_entry")
    markdowner = Markdown()
    entry_page = util.get_entry(entry)

    if entry_page is None:
        return render(request, "encyclopedia/notFound.html", {
            "title": entry
        })
    else:
        return render(request, "encyclopedia/entry.html", {
            "entry": markdowner.convert(entry_page),
            "title": entry
        })


def new_entry(request):
    print("In new_entry")
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


def edit_entry(request, title):
    if request.method == "GET":

        entry = util.get_entry(title)

        if entry:
            title = entry.split("\n")[0][2:]
            content = "\n".join(entry.split("\n")[2:])

            form = EntryForm(initial={'title': title, 'content': content})
            form.fields.get('title').widget.attrs["readonly"] = True

            return render(request, "encyclopedia/edit_entry.html", {"form": form, "title": title})
    elif request.method == "POST":

        form = EntryForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']

            existing_entries = util.list_entries()

            if title not in existing_entries:
                return render(request, "encyclopedia/new_entry.html",
                              {"form": form, "error_message": "This entry does not exist."}
                              )

            else:
                content = f"# {title}\n\n{content}"
                util.save_entry(title, content)
                return redirect("encyclopedia:entry", entry=title)

        else:
            return render(request, "encyclopedia/new_entry.html",
                          {"form": form}
                          )
