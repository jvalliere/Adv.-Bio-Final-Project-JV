from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SubmitField, SelectField
from wtforms.validators import DataRequired
from datetime import datetime
from datetime import date
import pandas as pd
import os
from Bio.Blast.Applications import NcbiblastpCommandline

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thequickbrownfrog'

import jinja2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thequickbrownfrog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'


##PSQL sign on info
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Soccer08@localhost/cifgene'

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)


###########################################################################################################################
class BlastButton_Form(FlaskForm):
    submit = SubmitField('Go to BLAST')
###########################################################################################################################
class SearchButton_Form(FlaskForm):
    submit = SubmitField('Go To Search')
###########################################################################################################################
class BrowseButton_Form(FlaskForm):
    submit = SubmitField('Go To Browse')
###########################################################################################################################
class UploadButton_Form(FlaskForm):
    submit = SubmitField('Upload an Entry!')
###########################################################################################################################
class SearchForm(FlaskForm):
    name2 = RadioField('Search by Wolbachia Strain, Arthropod Host, or entry ID:', choices=[('strain', 'Wolbachia Strain'), ('host', 'Arthropod Host'), ('id', 'Entry ID')])
    name1 = StringField('Enter an organism or ID:', validators=[DataRequired()])
    name3 = SelectField('Limit results by:', choices=[('1', '1'), ('5', '5'), ('10', '10'), ('25', '25'), ('50', '50')])
    name4 = SelectField('Order results by:', choices=[('strain', 
            'Wolbachia Strain'), ('host', 'Arthropod Host')])
    submit = SubmitField('Submit')

###########################################################################################################################
class BLASTForm(FlaskForm):
    seq = StringField("Enter a sequence:", validators=[DataRequired()])
    limit = SelectField('Limit results by:', choices=[('1', '1'), ('5', '5'), ('10', '10'), ('25', '25'), ('50', '50')])
    submit = SubmitField('Submit')

###########################################################################################################################
class BrowseForm(FlaskForm):
    parameter = RadioField('Search by: ', choices=[('cifA', 'cifA (gene)'), ('cifB', 'cifB (gene)'), ('Type I', 'Type I (CIF type)'), ('Type II', 'Type II (CIF type)'), ('Type III', 'Type III (CIF type)'), ('Type IV', 'Type IV (CIF type)'), ('Type V', 'Type V (CIF type)')])
    limit = SelectField('Limit results by:', choices=[('1', '1'), ('5', '5'), ('10', '10'), ('25', '25'), ('50', '50')])
    submit = SubmitField('Submit')

###########################################################################################################################  
class UploadForm(FlaskForm):
    u_gene = SelectField('Select Gene Type:', choices=[('cifA', 'CIF A'), ('cifB', 'CIF B')])
    u_cif_type = SelectField('Select CIF Type:', choices=[('Type I', 'Type I'), ('Type II', 'Type II'), ('Type III', 'Type III'), ('Type IV', 'Type IV'), ('Type V', 'Type V')])
    u_organism = StringField("Enter Organism:", validators=[DataRequired()])
    u_strain = StringField("Enter Strain:", validators=[DataRequired()])
    u_host = StringField("Enter Host:", validators=[DataRequired()])
    u_ncbi_nucleotide = StringField("Enter NCBI Nucleotide ID if possible:")
    u_ncbi_protein = StringField("Enter NCBI Protein ID if possible:")
    u_locus_tag = StringField("Enter Locus Tag:", validators=[DataRequired()])
    u_aa_sequence = StringField("Enter Amino Acid Sequence:", validators=[DataRequired()])
    submit = SubmitField('Submit')

###########################################################################################################################   
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

###########################################################################################################################
@app.route("/", methods =['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template("index.html")
    elif request.method == 'POST':
        if request.form['action'] == 'Go to Search':
            return redirect('/search')
        elif request.form['action'] == 'Go to BLAST':
            return redirect('/blast')
        elif request.form['action'] == 'Go to Browse':
            return redirect('/browse')
        else:
            return redirect('/upload')            
  
    return render_template("index.html")

###########################################################################################################################
@app.route('/about')
def about():
    return render_template('about.html')

###########################################################################################################################
@app.route('/ref')
def ref():
    return render_template('ref.html')

###########################################################################################################################
@app.route('/help')
def help():
    return render_template('help.html')

###########################################################################################################################
@app.route('/upload', methods=['GET', 'POST'])
def upload():

    u_gene = None
    u_cif_type = None
    u_organism = None
    u_strain = None
    u_host = None
    u_ncbi_nucleotide = None
    u_ncbi_protein = None
    u_locus_tag = None
    u_aa_sequence = None 
    form = UploadForm()

    if form.validate_on_submit():
        if request.method == 'POST':
           session['u_gene']  = form.u_gene.data     
           session['u_cif_type']  = form.u_cif_type.data
           session['u_organism']  = form.u_organism.data
           session['u_strain']  = form.u_strain.data
           session['u_host']  = form.u_host.data
           session['u_ncbi_nucleotide']  = form.u_ncbi_nucleotide.data
           session['u_ncbi_protein']  = form.u_ncbi_protein.data
           session['u_locus_tag']  = form.u_locus_tag.data
           session['u_aa_sequence']  = form.u_aa_sequence.data
           return redirect('/upload_ty')

        form.u_gene.data = ''    ## Reset form values
        form.u_cif_type.data = ''
        form.u_organism.data = ''
        form.u_strain.data = ''
        form.u_host.data = ''
        form.u_ncbi_nucleotide.data = ''
        form.u_ncbi_protein.data = ''
        form.u_locus_tag.data = ''
        form.u_aa_sequence.data = ''
    return render_template('upload.html', form=form)

###########################################################################################################################
@app.route('/upload_ty')
def upload_ty():
    u_gene = session.get('u_gene')
    u_cif_type = session.get('u_cif_type')
    u_organism = session.get('u_organism')
    u_strain = session.get('u_strain')
    u_host = session.get('u_host')
    u_ncbi_nucleotide = session.get('u_ncbi_nucleotide')
    u_ncbi_protein = session.get('u_ncbi_protein')
    u_locus_tag = session.get('u_locus_tag')
    u_aa_sequence = session.get('u_aa_sequence')

    u_description = (str(u_cif_type) + ' ' + str(u_gene) + '; ' + str(u_organism) + ' ' + str(u_strain) + ' of ' + str(u_host))

    print(u_description)
    u_product = ""

    if str(u_gene) == "cifA":
        u_product = "cytoplasmic incompatibility factor cifA"
    else:
        u_product = "cytoplasmic incompatibility factor cifB"

    today = date.today()
    c_date = today.strftime("%m/%d/%Y")

    df = pd.read_excel('C:/Users/Jesse/Adv_Bio/Local_Database/static/uploads.xlsx')    

    df1 = pd.DataFrame({'Date':[c_date],
    'ID':[''],
    'gene':[u_gene],
    'product':[u_product],
    'cif_type':[u_cif_type],
    'organism':[u_organism],
    'strain':[u_strain],
    'host':[u_host],
    'description':[u_description],
    'NCBI_nucleotide':[u_ncbi_nucleotide],
    'locus_tag':[u_locus_tag],
    'NCBI_protein':[u_ncbi_protein],
    'aa_sequence':[u_aa_sequence]})

    df = df.append(df1)

    #changed
    df.to_excel('C:/Users/Jesse/Adv_Bio/Local_Database/static/uploads.xlsx', index=False)

    return render_template('upload_ty.html')

###########################################################################################################################    
@app.route('/blast', methods=['GET', 'POST'])
def blast():
    seq = None
    limit = None    
    form = BLASTForm()

    if form.validate_on_submit():
        if request.method == 'POST':
           session['seq']  = form.seq.data      # seq is search sequence entered in first text box on form
           session['limit']  = form.limit.data      # limit is to limit the number of results displayed in table
           return redirect('/blast_results')

        form.seq.data = ''    ## Reset form values
        form.limit.data = ''
    return render_template('blast.html', form=form)

###########################################################################################################################
@app.route('/blast_results', methods = ['GET', 'POST'])
def blast_presults():

    seq = session.get('seq')
    limit = session.get('limit')
    form3 = BlastButton_Form()

    #open raw data csv, create fasta file from it
    df = pd.read_csv("Cif_Database.csv")
    list_of_id = df['ID'].to_list()
    list_of_seq = df['aa_sequence'].to_list()
    ofile = open("db_entries.fasta", "w")
    for i in range(len(list_of_seq)):
        ofile.write(">" + list_of_id[i] + "\n" +list_of_seq[i] + "\n")
    ofile.close()

    #use the created fasta file to make a database to search against
    os.system("makeblastdb -in db_entries.fasta -dbtype prot")

    #open query file, erase contents, and put in the query the user wants 
    ofile = open("query.seq", "r+")
    ofile.truncate(0)
    ofile.write(seq)
    ofile.close()

    #open output file, erase any contents so that the commandline can write in results 
    ofile = open("output.txt", "r+")
    ofile.truncate(0)
    ofile.close()


    #run the blast, and put the results into output.txt
    cline = NcbiblastpCommandline(query= "query.seq", db="db_entries.fasta",
                              evalue=0.001, max_target_seqs = int(limit), ungapped=False, out = "output.txt", outfmt = 6)
    os.system(str(cline))


    #open output file, write contents of output file to blast_presults, and close
    ofile = open("output.txt", "r")
    blast_presults = []

    lines = ofile.readlines()

    for line in lines:
        temp = line.split()
        temp.remove('Query_1')
        #HARD CODED
        temp[0] = '<a href=\"http://127.0.0.1:5000/' + temp[0] + '\">' + temp[0] + '</a>'
        blast_presults.append(temp)
   
    ofile.close()

    if request.method == 'POST':
        return redirect('/blast')

    return render_template('blast_results.html', blast_presults=blast_presults,\
    seq=seq,limit=limit, form3=form3)

###########################################################################################################################
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

###########################################################################################################################
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

###########################################################################################################################
@app.route('/gene/<id>')
def gene(id):
    entry = Data.query.filter_by(id=id).first_or_404()

    return render_template('gene.html', entry=entry)

###########################################################################################################################
@app.route('/browse', methods=['GET', 'POST'])
def browse():

    parameter = None
    limit = None
    form = BrowseForm()

    if form.validate_on_submit():
        if request.method == 'POST':
            session['parameter'] = form.parameter.data
            session['limit'] = form.limit.data

            return redirect('/browse_results')

        form.parameter.data = ''
        form.limit.data = ''

    return render_template('browse.html', form=form)

###########################################################################################################################
@app.route('/browse_results', methods=['GET', 'POST'])
def browse_presults():

    parameter = session.get('parameter')
    limit = session.get('limit')
    form3 = BrowseButton_Form()


    if parameter == 'cifA' or parameter == 'cifB':
        browse_presults = Data.query.filter(Data.gene.like(parameter)).limit(limit).all()
    else:
        browse_presults = Data.query.filter(Data.cif_type.like(parameter)).limit(limit).all()

    if request.method == 'POST':
        return redirect('/browse')

    return render_template('browse_results.html', browse_presults=browse_presults,\
    parameter=parameter,limit=limit,form3=form3)

###########################################################################################################################
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
    elif name2 == 'strain':  ##  if not host, check strain
        presults = Data.query.filter(Data.strain.like(searchterm)).order_by(displayorder).limit(name3).all()
    else:
        presults = Data.query.filter(Data.id.like(searchterm)).order_by(displayorder).limit(name3).all()

    if request.method == 'POST':
        return redirect('/search')

    return render_template('results.html', presults=presults,\
    name1=name1,name2=name2,name3=name3,name4=name4,form3=form3)

###########################################################################################################################
@app.route('/search', methods=['GET', 'POST'])
def search():
    name1 = None
    name2 = None
    name3 = None
    name4 = None
    form = SearchForm()

    if form.validate_on_submit():
        if request.method == 'POST':
           session['name1']  = form.name1.data      # name1 is search term entered in first text box on form
           session['name2']  = form.name2.data      # name2 is to specify first or last name in search query
           session['name3']  = form.name3.data      # name3 is to limit the number of results displayed in table
           session['name4']  = form.name4.data      # name4 is to specify the order of the search results

           return redirect('/results')

        form.name1.data = ''    ## Reset form values
        form.name2.data = ''
        form.name3.data = ''
        form.name4.data = ''
    return render_template('search.html', form=form) 

if __name__ == "__main__":
    app.run(debug=True)
