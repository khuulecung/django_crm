# When a new app is created, the urls.py is created to manage the url
from django.urls import path
from .views import ( # if the file is located in the same app (folder), place a period before it (.views)
    AgentListView, AgentCreateView, AgentDetailView, 
    AgentUpdateView, AgentDeleteView
)
# specify app name
app_name = 'agents'

urlpatterns = [
    path('', AgentListView.as_view(), name="agent-list"), # first argument is empty because list view is default page. Use as_view() as this is a Class Based View
    path('<int:pk>/', AgentDetailView.as_view(), name="agent-detail"), # <int:pk>/ => agent/1/
    path('<int:pk>/update/', AgentUpdateView.as_view(), name="agent-update"), # <int:pk>/update => agent/1/update
    path('<int:pk>/delete/', AgentDeleteView.as_view(), name='agent-delete'),
    path('create/', AgentCreateView.as_view(), name="agent-create"),
]
