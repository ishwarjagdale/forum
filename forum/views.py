import datetime

from django.contrib.auth import login
from django.shortcuts import render, redirect, reverse, HttpResponse

from .forms import SignUpForm, LogInForm, NewThreadForm, NewCommentForm, NewAnswerForm
from .models import Users, Thread, ThreadContent, Comments, ThreadVotes, ThreadAnswers
from .templatetags.tags import to_tags


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


def new_thread(request, thread_id=None):
    if request.user.is_authenticated:

        context = {'title': 'Edit Thread' if thread_id else 'New Thread'}
        if request.POST:
            form = NewThreadForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                topic = data.get('topic')
                content = data.get('content')
                tags = to_tags(data.get('tags'))

                if thread_id:
                    try:
                        thread = Thread.objects.get(thread_id=thread_id)
                        thread_content = ThreadContent.objects.get(thread_id=thread_id)
                        thread.__setattr__('content', thread_content)
                        if thread.is_active:
                            thread.topic = topic
                            thread_content.content = content
                            thread.tags = tags
                            thread_content.last_modified = datetime.datetime.now()

                            thread.save()
                            thread_content.save()

                            return redirect('thread-view', thread.thread_id)
                        else:
                            context['thread'] = thread
                            context['errors'] = ["This thread has been closed, and no changes can be made in it."]
                            return render(request, "forum/views/new-thread.html", context=context)
                    except Thread.DoesNotExist:
                        form.add_error('topic', f"No thread exist with id: {thread_id}")
                else:
                    _new_thread = Thread.create(topic=topic, author=request.user.username)
                    _new_thread.tags = tags
                    _new_thread.save()
                    _new_thread_content = ThreadContent.create(thread_id=_new_thread.thread_id, content=content)
                    ThreadVotes.create(thread_id=_new_thread.thread_id)
                    return redirect('thread-view', _new_thread.thread_id)

            context['form'] = form
            return render(request, "forum/views/new-thread.html", context=context)

        if thread_id:
            try:
                thread = Thread.objects.get(thread_id=thread_id)
                if request.user.username == thread.author:
                    thread_content = ThreadContent.objects.get(thread_id=thread_id)
                    thread.__setattr__('content', thread_content)
                    context['thread'] = thread

                    if 'deactivate' in request.GET:
                        thread.is_active = False
                        thread.save()
                else:
                    context['errors'] = [f"Unauthorized access, thread with id: {thread_id} doesn't belong to you"]
                    context['title'] = "New Thread"
            except Thread.DoesNotExist or ThreadContent.DoesNotExist:
                context['errors'] = [f"No thread exist with id: {thread_id}"]
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
            if password != confirm_password:
                form.add_error("confirm_password", "Passwords doesn't match")
            if not form.errors:
                try:
                    user = Users.objects.get(email=email)
                    if user:
                        form.add_error('email', "User already exists!")
                except Users.DoesNotExist:
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
    context = {}
    try:
        thread = Thread.objects.get(thread_id=thread_id)
        content = ThreadContent.objects.get(thread_id=thread.thread_id)
        thread.__setattr__('content', content)
        thread.views += 1
        thread.save()

        if request.user.is_authenticated:
            try:
                thread_vote = ThreadVotes.objects.get(thread_id=thread.thread_id)
            except ThreadVotes.DoesNotExist:
                thread_vote = ThreadVotes.create(thread_id=thread.thread_id, ups=set(), downs=set())

            if request.user.username in thread_vote.ups:
                context['user_vote'] = 1
            elif request.user.username in thread_vote.downs:
                context['user_vote'] = -1
            else:
                context['user_vote'] = 0

        answers = ThreadAnswers.objects.filter(parent_thread=thread.thread_id).all()
        answers = sorted(map(lambda x: {
            "answer_id": x.answer_id,
            "content": ThreadContent.objects.get(thread_id=x.answer_id),
            "author": Users.objects.get(username=x.author),
            "votes": x.votes,
            "date_posted": x.date_posted,
            "user_vote": 1 if request.user.username in ThreadVotes.objects.get(thread_id=x.answer_id).ups else
            -1 if request.user.username in ThreadVotes.objects.get(thread_id=x.answer_id).downs else 0
        }, answers), key=lambda x: x['votes'], reverse=True)

        context['answers'] = list(answers)

        thread.author = Users.objects.get(username=thread.author)

        comments = Comments.objects.filter(thread_id=thread.thread_id).limit(10)
        comments = map(lambda x: {
            "comment_id": x.comment_id,
            "comment": x.comment,
            "author": Users.objects.get(username=x.author),
            "date_posted": x.date_posted
        }, comments)
        context['comments'] = list(comments)

    except Thread.DoesNotExist:
        return HttpResponse("doesn't exist")
    context.update({"title": thread.topic, "thread": thread})
    return render(request, "forum/views/thread-page.html", context=context)


def new_comment(request, thread_id):
    if request.POST and request.user.is_authenticated:
        try:
            thread = Thread.objects.get(thread_id=thread_id)
        except Thread.DoesNotExist:
            return redirect(request.META.get('HTTP_REFERER'))
        if thread.is_active:
            form = NewCommentForm(request.POST)
            if form.is_valid():
                comment = form.cleaned_data.get('comment')
                Comments.create(thread_id=thread.thread_id, author=request.user.username,
                                comment=comment)
        return redirect(request.META.get('HTTP_REFERER'))


def vote_thread(request, thread_id):
    if request.POST and request.user.is_authenticated:
        try:
            thread = Thread.objects.get(thread_id=thread_id)
        except Thread.DoesNotExist:
            try:
                thread = ThreadAnswers.objects.get(answer_id=thread_id)
            except ThreadAnswers.DoesNotExist:
                return redirect(request.META.get('HTTP_REFERER'))
        try:
            thread_vote = ThreadVotes.objects.get(thread_id=thread_id)
        except ThreadVotes.DoesNotExist:
            thread_vote = ThreadVotes.create(thread_id=thread_id, ups=set(), downs=set())

        if "vote" in request.POST:
            vote = request.POST.get('vote')
            if vote in ["up", "down"]:
                if vote == "up":
                    thread_vote.ups.add(request.user.username)
                    thread_vote.downs.discard(request.user.username)
                else:
                    thread_vote.ups.discard(request.user.username)
                    thread_vote.downs.add(request.user.username)
                thread_vote.save()
                thread.votes = len(thread_vote.ups) - len(thread_vote.downs)
                thread.save()
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('login')


def new_answer(request, thread_id):
    if request.POST and request.user.is_authenticated:
        try:
            thread = Thread.objects.get(thread_id=thread_id)
        except Thread.DoesNotExist:
            return redirect(request.META.get('HTTP_REFERER'))
        form = NewAnswerForm(request.POST)
        if form.is_valid():
            answer = ThreadAnswers.create(parent_thread=thread.thread_id, author=request.user.username)
            thread.replies += 1
            thread.save()
            ThreadContent.create(thread_id=answer.answer_id, content=form.cleaned_data.get('content'))
            ThreadVotes.create(thread_id=answer.answer_id)

        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('login')
