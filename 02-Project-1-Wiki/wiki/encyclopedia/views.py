from django.shortcuts import render, redirect
import random

from .forms import EntryForm


from markdown2 import Markdown

from . import util


# Index Page
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


# Entry Page
def get_entry(request, entry):
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


# New Page
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


# Edit Page
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


# Random Page
def get_random(request):
    entries_list = util.list_entries()

    if entries_list:
        random_entry = random.choice(entries_list)
        # Redirect to the detail page of the randomly chosen entry
        return redirect("encyclopedia:entry", entry=random_entry)


# Search Page
def search_entry(request):
    entries_list = util.list_entries()
    results_list = []

    query = request.GET.get("q")

    if query in entries_list:
        return redirect("encyclopedia:entry", entry=query)

    for entry in entries_list:
        if query.lower() in entry.lower():
            results_list.append(entry)

    return render(request, "encyclopedia/search_result.html", {"title": "Search results", "results": results_list} )



    # if user_input in entries_list:
    #         return redirect("encyclopedia:entry", entry=user_input)
