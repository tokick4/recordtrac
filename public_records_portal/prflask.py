"""
    public_records_portal.prflask
    ~~~~~~~~~~~~~~~~

    Sets up API and admin endpoints for the RecordTrac flask application.

"""



from public_records_portal import app, models, db, views
from views import * # Import all the functions that render templates
from flask.ext.restless import APIManager
from flask.ext.admin import Admin, expose, BaseView, AdminIndexView
from flask.ext.admin.contrib.sqlamodel import ModelView
from jinja2.filters import do_mark_safe


# Create API
manager = APIManager(app, flask_sqlalchemy_db=db)


# The endpoints created are /api/object, e.g. publicrecordsareawesome.com/api/request/
manager.create_api(models.Request, methods=['GET'], results_per_page = 10, allow_functions = True, include_columns=['date_created', 'date_received', 'department', 'id', 'notes', 'offline_submission_type', 'owners', 'qas', 'records', 'status', 'status_updated', 'text'])
# manager.create_api(models.Owner, methods=['GET'], results_per_page = 10, allow_functions = True)
manager.create_api(models.Note, methods=['GET'], results_per_page = 10, allow_functions = True)
manager.create_api(models.Record, methods=['GET'], results_per_page = 10, allow_functions = True)
manager.create_api(models.QA, methods=['GET'], results_per_page =10, allow_functions = True)
# manager.create_api(models.Subscriber, methods=['GET'], results_per_page = 10, allow_functions = True)
manager.create_api(models.Visualization, methods=['GET'], results_per_page = 10, allow_functions = True)

class HomeView(AdminIndexView):
    @expose('/')
    def home(self):
        return self.render('admin.html')
    def is_accessible(self):
        return True
        if current_user.is_authenticated():
            if 'LIST_OF_ADMINS' in app.config:
                admins = app.config['LIST_OF_ADMINS'].split(",")
                if current_user.email.lower() in admins:
                    return True
        return False

# Create Admin
admin = Admin(app, name='RecordTrac Admin', url='/admin', index_view = HomeView(name='Home'))

class AdminView(ModelView):
    def is_accessible(self):
        return True
        if current_user.is_authenticated():
            if 'LIST_OF_ADMINS' in app.config:
                admins = app.config['LIST_OF_ADMINS'].split(",")
                if current_user.email.lower() in admins:
                    return True
        return False

class RequestView(AdminView):
    can_create = False
    can_edit = True
    column_list = ('id', 'text', 'date_created', 'status') # The fields the admin can view
    column_searchable_list = ('status', 'text') # The fields the admin can search a request by
    form_excluded_columns = ('date_created', 'extended', 'status', 'status_updated', 'current_owner') # The fields the admin cannot edit.

class RecordView(AdminView):
    can_create = False
    column_searchable_list = ('description', 'filename', 'url', 'download_url', 'access')
    column_list = ('request_id', 'description', 'filename', 'url', 'download_url', 'access')
    can_edit = False

class QAView(AdminView):
    can_create = False
    can_edit = True
    column_list = ('request_id', 'question', 'answer', 'date_created')
    form_excluded_columns = ('date_created')

class NoteView(AdminView):
    can_create = False
    can_edit = True
    column_list = ('request_id', 'text', 'date_created')
    form_excluded_columns = ('date_created')

class UserView(AdminView):
    can_create = True
    can_edit = True
    column_list = ('alias', 'email', 'current_department', 'phone', 'is_staff')
    column_labels = dict(alias='Name', current_department='Department', phone='Phone #')
    column_descriptions = dict(is_staff='Determines whether the user can log in and edit data through this interface.')
    form_excluded_columns = ('date_created', 'password', 'contact_for', 'backup_for')

class DepartmentView(AdminView):
    can_create = True
    can_edit = True
    column_list = ('name', 'primary_contact', 'backup_contact')
    column_descriptions = dict(backup_contact='Note that if you want to assign a user that does not yet exist as the primary or backup contact for this department, you must <a href="/admin/userview/new/?url=%2Fadmin%2Fdepartmentview%2Fnew%2F">create the user</a> first.')

    form_columns = column_list
    form_excluded_columns = ('date_created', 'date_updated')
    form_args = dict(backup_contact={
        'description': do_mark_safe(column_descriptions['backup_contact'])
    })

admin.add_view(RequestView(models.Request, db.session))
admin.add_view(RecordView(models.Record, db.session))
admin.add_view(NoteView(models.Note, db.session))
admin.add_view(QAView(models.QA, db.session))
admin.add_view(UserView(models.User, db.session))
admin.add_view(DepartmentView(models.Department, db.session))
