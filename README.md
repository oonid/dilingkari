## Project dilingkari (circled) for Google+

## Simple project to support my (FREE) Kelas Python at http://oo.or.id/py

The live version of the project accessible via http://di.lingkari.com (an alias version of http://dilingkari.appspot.com)

 -------     ------     -----------------     ----------
 | WEB |-----| DB |-----| API Interface |-----| G+ API |
 -------     ------     -----------------     ----------

Here's how you can rebuild the app (or if you IntelliJ IDEA user, refer to [1]):

Open Terminal (if lib directory is empty or not complete)

+ $ pip install -r requirements.txt -t lib/

Open (or create) Project on Developer Console

+ activate Google+ API

+ activate Datastore HTTP API only if Developer Console request to activate it

+ put the App ID to file app.yaml, section application and env_variable (URL with appspot.com)

what you should do with the project files on lib directory:

1. we don't need jinja2 and markupsafe because already available on App Engine, so you can delete it.

1. we don't need \*.egg-info (to be uploaded to App Engine), so you can delete it.

UI with Twitter bootstrap, open source template from startbootstrap [2].

[1]http://oo.or.id/content/python-web-sample-project-di-lingkari-com
[2]http://startbootstrap.com/template-overviews/3-col-portfolio/

![Alt text](http://7langit.com/dilingkari.png "Screenshot of Website (updated per hour)")