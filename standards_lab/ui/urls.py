from django.urls import path

import ui.views
from ui.apps import UiConfig

app_name = UiConfig.name

urlpatterns = [
    path("", ui.views.Home.as_view(), name="home"),
    path("p/<slug:project_name>", ui.views.ProjectView.as_view(), name="project"),
    path(
        "p/<slug:project_name>/cove-results",
        ui.views.CoveResults.as_view(),
        name="cove-results",
    ),
    path("about", ui.views.About.as_view(template_name="about.html"), name="about"),
    path("sysadmin", ui.views.SysAdmin.as_view(), name="sysadmin"),
    path("sysadmin/login", ui.views.SysAdminLogIn.as_view(), name="sysadmin_login"),
    path("sysadmin/logout", ui.views.SysAdminLogOut.as_view(), name="sysadmin_logout"),
    path("sysadmin/p", ui.views.SysAdminProjects.as_view(), name="sysadmin_projects"),
]
