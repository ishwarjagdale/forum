import datetime

from django.contrib.auth import login
from django.shortcuts import render, redirect, reverse, HttpResponse

from .forms import SignUpForm, LogInForm, NewThreadForm
from .models import Users, Thread, ThreadContent


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
    if request.user.is_authenticated:
        if request.POST:
            form = NewThreadForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                topic = data.get('topic')
                content = data.get('content')
                tags = set(filter(lambda x: len(x) > 0, map(lambda x: x.strip(), data.get('tags').split('\n'))))
                _new_thread = Thread.create(topic=topic, author=request.user.username)
                _new_thread.tags = tags
                _new_thread.save()
                _new_thread_content = ThreadContent.create(thread_id=_new_thread.thread_id, content=content)

                return redirect('thread-view', _new_thread.thread_id)

            context['form'] = form
            return render(request, "forum/views/new-thread.html", context=context)
        return render(request, "forum/views/new-thread.html", context=context)
    return redirect(reverse('login') + "?next=/new-thread/", next='new-thread')


def sign_up(request):
    context = {"title": "Sign Up"}

    if request.user.is_authenticated:
        return redirect(request.GET.get('next', default='home'))

    if request.POST:
        form = SignUpForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            name = data.get('name')
            email = data.get('email')
            password = data.get('password')
            confirm_password = data.get('confirm_password')
            print(name, email, password, confirm_password)
            if password != confirm_password:
                form.add_error("confirm_password", "Passwords doesn't match")
            if not form.errors:
                user = Users.create(name=name, email=email, password=password, authenticated=True, is_active=True)
                login(request, user)
                user.last_login = datetime.datetime.now()
                user.save()
                return redirect(request.GET.get('next', default='home'))

        context['form'] = form
        return render(request, "forum/views/sign-up.html", context=context)

    return render(request, "forum/views/sign-up.html", context=context)


def log_in(request):
    if request.user.is_authenticated:
        return redirect(request.GET.get('next', default='home'))

    context = {"title": "Log In"}
    if request.POST:
        form = LogInForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            email = data.get("email")
            password = data.get("password")

            try:
                user = Users.objects.get(email=email, password=password)
                login(request, user)
                user.last_login = datetime.datetime.now()
                user.save()
                return redirect(request.GET.get('next', default='home'))
            except Users.DoesNotExist:
                form.add_error('email', "Invalid email or password")

        context['form'] = form
        return render(request, "forum/views/sign-up.html", context=context)
    return render(request, "forum/views/sign-up.html", context=context)


def thread_view(request, thread_id):
    try:
        thread = Thread.objects.get(thread_id=thread_id)
        content = ThreadContent.objects.get(thread_id=thread.thread_id)
        thread.__setattr__('content', content)
        thread.views += 1
        thread.save()
    except Thread.DoesNotExist:
        return HttpResponse("doesn't exist")
    context = {"title": thread.topic, "thread": thread}
    return render(request, "forum/views/thread-page.html", context=context)
