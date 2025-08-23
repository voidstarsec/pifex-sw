from flask import Flask, url_for, render_template, send_from_directory
import jinja2.exceptions

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buttons.html')
def buttons():
    return render_template('buttons.html')

@app.route('/<pagename>')
def admin(pagename):
    return render_template(pagename)

@app.route('/<path:resource>')
def serveStaticResource(resource):
	return send_from_directory('static/', resource)

@app.errorhandler(jinja2.exceptions.TemplateNotFound)
def template_not_found(e):
    return not_found(e)

@app.errorhandler(404)
def not_found(e):
    return '<strong>Page Not Found!</strong>', 404

if __name__ == '__main__':
    #app.run(host='0.0.0.0',port=80)
    app.run()
