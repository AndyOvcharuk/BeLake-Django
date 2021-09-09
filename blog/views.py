from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from .forms import CreateViewForm, UpdateViewForm

# enabling case-insensitive search in MySQL databases
from django.db.models import Q, TextField
from django.db.models.functions import Lower
TextField.register_lookup(Lower, "lower")


class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 20

    # modifying the function for returning posts
    def get_queryset(self):
        search_query = self.request.GET.get('search', '')
        # using Q for case-insensitive search in a MySQL database
        queryset = Post.objects.filter(
            Q(content__lower__contains=search_query)).order_by('-date_posted')
        return queryset


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    # making the class use an existing form with pre-defined validation rules
    form_class = CreateViewForm
    template_name = 'blog/post_create.html'
    success_url = '/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'blog/post_update.html'
    form_class = UpdateViewForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = '/'
    template_name = 'blog/post_delete.html'


# defining actions when the CSRF error occurs
# the reason parameter here is optional and will only be displayed in logs
def csrf_failure(request, reason=""):
    current_page = request.path
    # iterating through all the pages that contain forms where the user can potentially encounter the CSRF error
    # and calling respective functions again
    try:
        if '/post/new' in current_page:
            return PostCreateView.as_view()(request)
        elif '/update' in current_page:
            return PostUpdateView.as_view()(request)
        elif '/delete' in current_page:
            return PostDeleteView.as_view()(request)
        # redirect to the homepage in any other case, e.g. after login
        else:
            return HttpResponseRedirect('/')
    # if there was any error in calling the respective function, then redirect to the homepage
    except:
        return HttpResponseRedirect('/')
