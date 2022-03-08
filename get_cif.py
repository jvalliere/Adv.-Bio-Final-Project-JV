from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SubmitField, SelectField
from wtforms.validators import DataRequired
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thequickbrownfrog'

import jinja2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thequickbrownfrog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'

##*****************************************##
## Connect to your local postgres database ##
##*****************************************##

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Soccer08@localhost/cifgene'



db = SQLAlchemy(app)
bootstrap = Bootstrap(app)


class SearchButton_Form(FlaskForm):
    submit = SubmitField('Go To Search')


class NameForm(FlaskForm):
    name2 = RadioField('Search by Wolbachia Strain or Arthropod Host:', choices=[('strain', 'Wolbachia Strain'), ('host', 'Arthropod Host')])
    name1 = StringField('Enter an organism or strain:', validators=[DataRequired()])
    name3 = SelectField('Limit results by:', choices=[('1', '1'), ('5', '5'), ('10', '10'),('50', '50')])
    name4 = SelectField('Order results by:', choices=[('strain', 
            'Wolbachia Strain'), ('host', 'Arthropod Host')])
    submit = SubmitField('Submit')

#class BLASTForm(FlaskForm):
#    name1 = StringField("Enter a sequence:", validators=[DataRequired()])
#    name3 = SelectField('Limit results by:', choices=[('1', '1'), ('5', '5'), ('10', '10'),('50', '50')])
#    submit = SubmitField('Submit')


class Data(db.Model):
    __tablename__ = "cifgene"
    id = db.Column(db.String(10),
                        primary_key=True,
                        nullable=False)
    gene = db.Column(db.String(4),
                        index=False,
                        nullable=False)
    product = db.Column(db.String(50),
                        index=False,
                        nullable=False)
    cif_type = db.Column(db.String(10),
                        index=False,
                        nullable=False)
    organism = db.Column(db.String(25),
                        index=False,
                        nullable=False)
    strain = db.Column(db.String(30),
                        index=False,
                        nullable=False)
    host = db.Column(db.String(30),
                        index=False,
                        nullable=False)
    description = db.Column(db.String(100),
                        index=False,
                        nullable=False)
    ncbi_nucleotide = db.Column(db.String(30),
                        index=False,
                        nullable=True)
    locus_tag = db.Column(db.String(30),
                        index=False,
                        nullable=True)
    ncbi_protein = db.Column(db.String(30),
                        index=False,
                        nullable=True)
    aa_sequence = db.Column(db.String(10000),
                        index=False,
                        nullable=True)

    def __init__(self, id, gene, product, cif_type, organism, strain, host, description, ncbi_nucleotide, locus_tag, ncbi_protein, aa_sequence):
        self.id = id
        self.gene = gene
        self.product = product
        self.cif_type = cif_type
        self.organism = organism
        self.strain = strain
        self.host = host
        self.description = description
        self.ncbi_nucleotide = ncbi_nucleotide
        self.locus_tag = locus_tag
        self.ncbi_protein = ncbi_protein
        self.aa_sequence = aa_sequence


    def __repr__(self):
        return f"<cifgene {self.host}>"


@app.route("/", methods =['GET','POST'])
def index():
    form2 = SearchButton_Form()
    if request.method == 'POST':
        return redirect('/search')
    return render_template("index.html", form2=form2)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/ref')
def ref():
    return render_template('ref.html')

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/blast')
def blast():
    return render_template('blast.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/gene/<id>')
def gene(id):
    entry = Data.query.filter_by(id=id).first_or_404()
    return render_template('gene.html', entry=entry)

@app.route("/results", methods = ['GET', 'POST'])
def presults():
    name1 = session.get('name1')
    name2 = session.get('name2')
    name3 = session.get('name3')
    name4 = session.get('name4')
    form3 = SearchButton_Form()

    searchterm = "%{}%".format(name1) ## adds % wildcards to front & back of search term
    displayorder = eval('Data.{}'.format(name4))

    if name2 == 'host':
        presults = Data.query.filter(Data.host.like(searchterm)).order_by(displayorder).limit(name3).all()
    else:  ##  if not host defaults to strain
        presults = Data.query.filter(Data.strain.like(searchterm)).order_by(displayorder).limit(name3).all()

    #presults = Data.query.all()
    #presults = Data.query.order_by(Data.strain).all()
    #presults = Data.query.filter(Data.arthropod_host == name1).order_by(Data.arthropod_host).all()
    #presults = Data.query.filter_by(Data.arthropod_host.like(searchterm)).order_by(displayorder).all()

    if request.method == 'POST':
        return redirect('/search')

    return render_template('results.html', presults=presults,\
     name1=name1,name2=name2,name3=name3,name4=name4,form3=form3)


@app.route('/search', methods=['GET', 'POST'])
def search():
    name1 = None
    name2 = None
    name3 = None
    name4 = None
    form = NameForm()
    if form.validate_on_submit():
        if request.method == 'POST':
           session['name1']  = form.name1.data		# name1 is search term entered in first text box on form
           session['name2']  = form.name2.data		# name2 is to specify first or last name in search query
           session['name3']  = form.name3.data		# name3 is to limit the number of results displayed in table
           session['name4']  = form.name4.data		# name4 is to specify the order of the search results
#          return '''<h1>The name1 value is: {}</h1>
#                  <h1>The name2  value is: {}</h1>'''.format(name1, name2)
           return redirect('/results')

        form.name1.data = ''	## Reset form values
        form.name2.data = ''
        form.name3.data = ''
        form.name4.data = ''
    return render_template('search.html', form=form) 

if __name__ == "__main__":
    app.run(debug=True)

