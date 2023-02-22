from django.shortcuts import render

from .models import *


def home(request):
    total_threads = Thread.objects().count()
    total_members = Users.objects().count()

    threads = []
    tags = set()
    query = Thread.objects().all()

    populars = map(lambda x: {
            "thread_id": x.thread_id,
            "topic": x.topic,
            "author": Users.objects.get(username=x.author),
            "views": x.views,
            "replies": x.replies,
            "date_posted": x.date_posted
        }, sorted(query, key=lambda x: x['views'], reverse=True)[: 3])

    if "search" in request.GET:
        query = filter(lambda x: (request.GET.get("search").lower() in str(x.topic).lower()) or
                                 (request.GET.get("search").lower() in " ".join(x.tags).lower()), query)
    if "filter" in request.GET:
        query = filter(lambda x: request.GET.get("filter") in x.tags, query)

    print(request.GET.get('filter'))

    for thread in query:
        threads.append({
            "thread_id": thread.thread_id,
            "topic": thread.topic,
            "author": Users.objects.get(username=thread.author),
            "views": thread.views,
            "replies": thread.replies,
            "date_posted": thread.date_posted
        })
        tags.update(thread.tags)

    context = {'title': 'Home', 'stats': {'total_threads': total_threads, 'total_members': total_members},
               'threads': threads, 'tags': tags, 'populars': populars
               }
    if request.user.is_authenticated:
        new_threads = Thread.objects(Thread.date_posted > request.user.last_login).count()
        context['new_threads'] = new_threads

    return render(request, "forum/views/home.html", context=context)


def new_thread(request):
    context = {'title': 'Home'}
    return render(request, "forum/views/new_thread.html", context=context)
