from flask import Flask, render_template, url_for, request, redirect, session, flash, send_file
from flask import make_response, session, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, create_engine
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import os
from mutagen.mp3 import MP3
from pygame import *
from email.message import EmailMessage
import datetime
import os
from openpyxl import Workbook, load_workbook
import random
import model

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "You need to Login first"

app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///MusicPlayer.db'
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'
engine = create_engine('sqlite:///MusicPlayer.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

session = dict()

class Songs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False)
    path = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(15))
    genre = db.Column(db.String(15))
    cover_photo = db.Column(db.String(100))
    duration = db.Column(db.String(100))
    total_likes = db.Column(db.Integer, default=0)
    total_listen_count = db.Column(db.Integer, default=0)


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), nullable=False, unique=True)
    password = db.Column(db.String(15), nullable=False)
    mail_id = db.Column(db.String(15), nullable=False, unique=True)
    preference1 = db.Column(db.Text)
    preference2 = db.Column(db.Text)
    preference3 = db.Column(db.Text)


class Interactions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(Users.id))
    song_id = db.Column(db.Integer, db.ForeignKey(Songs.id))
    like = db.Column(db.Integer, default=0)
    listen_count = db.Column(db.Integer, default=0)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


def convert(seconds):
    hours = seconds // 3600
    seconds %= 3600
    mins = seconds // 60
    seconds %= 60
    return hours, mins, seconds


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    try:
        if mixer.get_init:
            stop()
    except:
        pass
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method="sha256")
        cpassword = request.form['cpassword']
        mail_id = request.form['mail_id']

        user = Users.query.filter_by(username=username).first()
        if user:
            flash("User Name Already Exists, Choose Different", "warning")
            return redirect("/signup")
        if(password == cpassword):
            new_user = Users(username=username,
                             password=hashed_password, mail_id=mail_id)
            db.session.add(new_user)
            db.session.commit()

            # msg = EmailMessage()
            # msg['Subject'] = 'Sucessfully Registered to Music Fiesta!'
            # msg['From'] = EMAIL_ADDRESS
            # msg['To'] = mail_id
            # msg.set_content('Thank you for Registering to Music Fiesta.')

            # f = open("templates/hello.txt", "r")
            # msg.add_alternative(f.read(), subtype='html')

            # with smtplib.SMTP_SSL('smtp.gmail.com'3, 465) as smtp:
            #     smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            #     smtp.send_message(msg)
            user = Users.query.filter_by(username=username).first()

            flash(
                "Please Select Preference to Complete the Registration Process", "success")
            return redirect(f'/preferenceform/{user.id}')
        else:
            flash("Passwords don't match", "danger")
            return redirect("/signup")

    return render_template("sign-up.html")


@app.route('/preferenceform/<int:user_id>', methods=['POST', 'GET'])
def preferenceform(user_id):
    user = Users.query.filter_by(id=user_id).first()
    if request.method == "POST":
        genre = request.form.getlist('radio-card')
        try:
            user.preference1 = genre[0]
            user.preference2 = genre[1]
            user.preference3 = genre[2]
            db.session.commit()
        except:
            db.session.commit() 
        flash("Sucessfully Registered!")       
        return redirect('/login')

    return render_template("form.html", user=user)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if mixer.get_init():
        stop()
    if request.method == "POST":
        logout()
        username = request.form.get('username')
        password = request.form.get('password')

        user = Users.query.filter_by(username=username).first()
        print(user)

        if not user:
            flash("No such User found, Try Signing Up First", "warning")
            return redirect("/signup")

        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                print("Login Done!")
                return redirect("allsonglist")
            else:
                flash("Incorrect password", "danger")
                return redirect("login")

    return render_template("log-in.html")


@app.route('/logout')
def logout():
    if mixer.get_init():
        stop()
    logout_user()
    flash("Successfully Logged out!")
    return redirect('/login')


@app.route('/')
def index():
    current_song_id = session.get("current_song",None)    
    return render_template('home.html', current_user=current_user,song_id = current_song_id)


@app.route('/dashboard/<song_id>', methods=['POST', 'GET'])
@login_required
def dashboard(song_id):
    song = Songs.query.filter_by(id=song_id).first()
    liked_song = Interactions.query.filter_by(
        user_id=current_user.id, song_id=song_id).first()

    current_time_sec = mixer.music.get_pos()
    current_time = int(current_time_sec/1000)

    return render_template('dashboard.html', song=song, current_user=current_user, liked_song=liked_song, current_time=current_time)


@app.route('/allsonglist', methods=['POST', 'GET'])
def allsonglist():
    songs = Songs.query.order_by(Songs.name.desc()).all()
    current_song_id = session.get("current_song",None)
    return render_template('allsonglist.html', songs=songs,song_id = current_song_id)


@app.route('/likedsonglist', methods=['POST', 'GET'])
@login_required
def likedsonglist():
    songs = []
    current_song_id = session.get("current_song",None)
    liked_songs = Interactions.query.filter_by(user_id=current_user.id).all()
    for l in liked_songs:
        song = Songs.query.filter_by(id=l.song_id).first()
        songs.append(song)
    if len(songs) == 0:
        flash("LIKE some songs to Add songs in this Playlist!")
    return render_template('likedsonglist.html', songs=songs, song_id = current_song_id)


@app.route('/search', methods=['POST', 'GET'])
def search():
    current_song_id = session.get("current_song",None)
    if request.method == "POST":
        search_string = request.form['search_string']
        search = "{0}".format(search_string)
        search = search+'%'
        current_song_id = session.get("current_song",None)
        results = Songs.query.filter(
            or_(Songs.name.like(search), Songs.artist.like(search))).all()
        if len(results) == 0:
            flash("No such song availabe!")
        return render_template('search.html', results=results,song_id = current_song_id)
    return render_template('search.html',song_id = current_song_id)


def save_picture(form_picture):
    picture_fn = form_picture.filename
    print(picture_fn)
    picture_path = os.path.join(
        app.root_path, 'static\Song\SongCover', picture_fn)
    print(picture_path)
    form_picture.save(picture_path)
    print("Form_picture Saved")
    return picture_fn


def save_song(form_song):
    song_fn = form_song.filename
    song_path = os.path.join(
        app.root_path, 'static\Song\song', song_fn)
    print(song_path)
    form_song.save(song_path)
    print("Form_song Saved")
    return song_fn


@app.route('/addsongs', methods=['POST', 'GET'])
def addsongs():
    if request.method == 'POST':
        print("Inside if loop")
        songname = request.form.get('song')
        song = request.files['songpath']
        artist = request.form.get('artist')
        cover_photo = request.files['cover_photo']
        print("Got all the Form Info")
        song_file = save_song(song)
        cover_file = save_picture(cover_photo)
        print("Saved Song And Cover Photo")
        print(song_file)
        print(cover_file)

        audio = MP3(f"static\Song\song\{song_file}")
        audio_info = audio.info
        length_in_secs = int(audio_info.length)
        hours, mins, seconds = convert(length_in_secs)

        duration = f"{mins}:{seconds}"
        print(duration)

        path = f"static\Song\song\{song_file}"

        new_song = Songs(path=path, name=songname,
                         cover_photo=cover_file, artist=artist, duration=duration)
        db.session.add(new_song)
        db.session.commit()
        print("Session commited")
        return "Song Added"
    return render_template('add_songs.html')


@app.route('/play/<id>', methods=['POST', 'GET'])
@login_required
def play(id):
    mixer.init()
    song = Songs.query.filter_by(id=id).first()
    mixer.music.load(song.path)
    mixer.music.play()
    session['current_song']= song.id
    interaction = Interactions.query.filter_by(user_id = current_user.id, song_id = song.id).first()
    if interaction:
        interaction.listen_count = interaction.listen_count + 1
        song.total_listen_count = song.total_listen_count + 1
        db.session.commit()
    else:
        interaction = Interactions(user_id = current_user.id,song_id = song.id,listen_count = 1)
        song.total_listen_count = song.total_listen_count + 1
        db.session.add(interaction)
        db.session.commit()    
    url = f"/dashboard/{id}"
    return redirect(url)


@app.route('/pause/<id>', methods=['POST'])
def pause(id):
    mixer.init()
    song = Songs.query.filter_by(id=id).first()
    mixer.music.pause()
    url = f"/dashboard/{id}"
    return redirect(url)


@app.route('/unpause/<id>', methods=['POST'])
def unpause(id):
    mixer.init()
    song = Songs.query.filter_by(id=id).first()
    mixer.music.unpause()
    url = f"/dashboard/{id}"
    return redirect(url)


@app.route('/voldown/<id>', methods=['POST'])
def voldown(id):
    vol = mixer.music.get_volume()
    if vol == 0.0:
        pass
    vol = vol-0.1
    mixer.music.set_volume(vol)
    url = f"/dashboard/{id}"
    return redirect(url)


@app.route('/volup/<id>', methods=['POST'])
def volup(id):
    vol = mixer.music.get_volume()
    if vol == 1.0:
        pass
    vol = vol+0.1
    mixer.music.set_volume(vol)
    url = f"/dashboard/{id}"
    return redirect(url)


def stop():
    mixer.music.stop()
    return 0


@app.route('/liked/<user_id>/<song_id>', methods=['GET', 'POST'])
def liked(user_id, song_id):
    information = request.data
    info = information.decode("utf-8")
    user = Users.query.filter_by(id=user_id).first()
    song = Songs.query.filter_by(id=song_id).first()
    if info == 'true':
        print("info - ", info)
        u = Interactions.query.filter_by(user_id=user.id, song_id=song.id).first()
        if u:
            print("Inside if, userid and songid exists")
            u.like = 1
            db.commit()
        else:
            print("Inside else, creating new liked row")
            new = Interactions(user_id=user.id, song_id=song.id, like=1)
            db.session.add(new)
            db.session.commit()
    elif info == 'false':
        print("info - ", info)
        u = Interactions.query.filter_by(user_id=user.id, song_id=song.id, like=1).first()
        if u:
            db.session.delete(u)
            db.session.commit()
            pass
    else:
        pass
    url = f"/dashboard/{song_id}"
    return redirect(url)


@app.route('/uploaddataset')
def uploaddataset():
    genre = ['garhwali','ghazal','sufi','bollywood_rap','bollywood_romantic','bhojpuri','bhajan']
    for g in genre:
        count = 0
        for filename in os.listdir(f'Dataset\\{g}'):
            if filename.endswith(".mp3"):
                name = filename.split(" - ")[1]
                artist = filename.split(" - ")[0]
                genre = g
                path = f'Dataset\\{g}\{filename}'
                coverphoto = url_for('static', filename=f'images/{g}.jpeg')
                audio = MP3(path)
                audio_info = audio.info
                length_in_secs = int(audio_info.length)
                hours, mins, seconds = convert(length_in_secs)
                duration = f"{mins}:{seconds}"
                new_song = Songs(name=name, path=path, artist=artist, genre=genre,
                                cover_photo=coverphoto, duration=duration)
                db.session.add(new_song)
                count = count+1
        db.session.commit()
        print("COUNT ", count)
    return "DONE"


def save_excel(form_excel):
    _, f_ext = os.path.splitext(form_excel.filename)
    excel_fn = "sheet" + f_ext
    excel_path = os.path.join(app.root_path, excel_fn)
    form_excel.save(excel_path)
    return excel_fn

@app.route('/uploaduserdata',methods = ['GET','POST'])
def uploaduserdata():
    if request.method == "POST":
        sheet = request.files['Excel']
        data_file = save_excel(sheet)
        # Load the entire workbook.
        wb = load_workbook(data_file, data_only=True)
        # Load one worksheet.
        ws = wb['data']
        all_rows = list(ws.rows)
        genres = ['bhojpuri','sufi','bollywood_rap','bollywood_romantic','bhajan','ghazal','garhwali']
        # Pull information from specific cells.
        for row in all_rows[2:]:
            fullname = row[0].value
            username = f"{fullname.split(' ')[0]}.{fullname.split(' ')[1]}"
            email = f"{fullname.split(' ')[0]}.{fullname.split(' ')[1]}@gmail.com"
            pref = random.sample(genres, 3)
            preference1 = pref[0]
            preference2 = pref[1]
            preference3 = pref[2]            
            user = Users.query.filter_by(username = username).first()
            if user:
                pass
            else:
                newuser = Users(username = username,password='sha256$cBl7wrlwRwy9QHJB$7a873cb0e1cd6cd2070c00147540fc6ba209e9114152385c94e06fb641951076', mail_id = email, preference1 = preference1, preference2 = preference2, preference3 = preference3)
                db.session.add(newuser)

        db.session.commit()        
        return "Data Added"        
    return render_template('uploaduserdata.html') 
    

@app.route('/uploadlikes',methods = ['GET'])
def uploadlikes():
    users = Users.query.all()
    for user in users:
        if user.preference1 == "garhwali" or user.preference2 == "garhwali" or user.preference3 == "garhwali":
            for i in range(5):
                song_id = random.randrange(1,91)
                listen_count = random.randrange(1,1000)
                like = Interactions(user_id = user.id, song_id = song_id, like = 1, listen_count = listen_count) 
                song = Songs.query.filter_by(id = song_id).first()
                song.total_listen_count = song.total_listen_count + listen_count
                song.total_likes = song.total_likes + 1
                db.session.add(like)
                db.session.commit()
        if user.preference1 == "ghazal" or user.preference2 == "ghazal" or user.preference3 == "ghazal":
            for i in range(5):
                song_id = random.randrange(91,185)
                listen_count = random.randrange(1,1000)
                like = Interactions(user_id = user.id, song_id = song_id, like = 1, listen_count = listen_count)
                song = Songs.query.filter_by(id = song_id).first()
                song.total_listen_count = song.total_listen_count + listen_count
                song.total_likes = song.total_likes + 1 
                db.session.add(like)
                db.session.commit()
        if user.preference1 == "bhajan" or user.preference2 == "bhajan" or user.preference3 == "bhajan":
            for i in range(5):
                song_id = random.randrange(515,563)
                listen_count = random.randrange(1,1000)
                like = Interactions(user_id = user.id, song_id = song_id, like = 1, listen_count = listen_count) 
                song = Songs.query.filter_by(id = song_id).first()
                song.total_listen_count = song.total_listen_count + listen_count
                song.total_likes = song.total_likes + 1 
                db.session.add(like)
                db.session.commit()
        if user.preference1 == "bhojpuri" or user.preference2 == "bhojpuri" or user.preference3 == "bhojpuri":
            for i in range(5):
                song_id = random.randrange(440,515)
                listen_count = random.randrange(1,1000)
                like = Interactions(user_id = user.id, song_id = song_id, like = 1, listen_count = listen_count) 
                song = Songs.query.filter_by(id = song_id).first()
                song.total_listen_count = song.total_listen_count + listen_count
                song.total_likes = song.total_likes + 1 
                db.session.add(like)
                db.session.commit()
        if user.preference1 == "bollywood_rap" or user.preference2 == "bollywood_rap" or user.preference3 == "bollywood_rap":
            for i in range(5):
                song_id = random.randrange(259,359)
                listen_count = random.randrange(1,1000)
                like = Interactions(user_id = user.id, song_id = song_id, like = 1, listen_count = listen_count) 
                song = Songs.query.filter_by(id = song_id).first()
                song.total_listen_count = song.total_listen_count + listen_count
                song.total_likes = song.total_likes + 1 
                db.session.add(like)
                db.session.commit()
        if user.preference1 == "bollywood_romantic" or user.preference2 == "bollywood_romantic" or user.preference3 == "bollywood_romantic":
            for i in range(5):
                song_id = random.randrange(359,440)
                listen_count = random.randrange(1,1000)
                like = Interactions(user_id = user.id, song_id = song_id, like = 1, listen_count = listen_count) 
                song = Songs.query.filter_by(id = song_id).first()
                song.total_listen_count =  song.total_listen_count +listen_count
                song.total_likes = song.total_likes + 1 
                db.session.add(like)
                db.session.commit()
        if user.preference1 == "sufi" or user.preference2 == "sufi" or user.preference3 == "sufi":
            for i in range(5):
                song_id = random.randrange(185,259)
                listen_count = random.randrange(1,1000)
                like = Interactions(user_id = user.id, song_id = song_id, like = 1, listen_count = listen_count) 
                song = Songs.query.filter_by(id = song_id).first()
                song.total_listen_count =  song.total_listen_count +listen_count
                song.total_likes = song.total_likes + 1
                db.session.add(like)
                db.session.commit()       
        for i in range(5):
            song_id = random.randrange(1,563)
            listen_count = random.randrange(1,1000)
            like = Interactions(user_id = user.id, song_id = song_id, like = 1, listen_count = listen_count) 
            song = Songs.query.filter_by(id = song_id).first()
            song.total_listen_count =  song.total_listen_count +listen_count
            song.total_likes = song.total_likes + 1
            db.session.add(like)
            db.session.commit()
    return "Data Added"    


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
