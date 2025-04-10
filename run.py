import os

from app import create_app, db
from werkzeug.middleware.profiler import ProfilerMiddleware

app = create_app()

profile_directory = './profiles'

if not os.path.exists(profile_directory):
    os.makedirs(profile_directory)

if os.environ.get("PROFILE") == "true":
    print("Profiler is enabled")
    app.wsgi_app = ProfilerMiddleware(
        app.wsgi_app,
        sort_by=('cumulative',),
        restrictions=[50],
        profile_dir=profile_directory
    )

if __name__ == '__main__':
    #with app.app_context():
    #    db.create_all()
    app.run(debug=True)
