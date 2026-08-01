from django.urls import path
from apps.agents import views
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('agent/dashboard/', views.agent_dashboard, name='agent_dashboard'),
    path('agent/chat/', views.agent_chat, name='agent_chat'),
    path('agent/profile/', views.agent_profile, name='agent_profile'),
    path('admin-panel/agents/', views.admin_agents, name='admin_agents'),
    path('admin-panel/agents/add/', views.admin_add_agent, name='admin_add_agent'),
    path('admin-panel/agents/<int:aid>/delete/', views.admin_delete_agent, name='admin_delete_agent'),
    path('admin-panel/agents/<int:aid>/toggle/', views.admin_toggle_agent, name='admin_toggle_agent'),
    path('admin-panel/agents/<int:aid>/report/', views.agent_report_pdf, name='agent_report'),
    path('api/agents/status/', views.api_agents_status, name='api_agents_status'),
]
