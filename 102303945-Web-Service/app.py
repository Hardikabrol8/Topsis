import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flash messages
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_email(receiver_email, result_file):
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")

    if not sender_email or not sender_password:
        print(f"Warning: SENDER_EMAIL or SENDER_PASSWORD not set. Email to {receiver_email} skipped.")
        print(f"Result file generated: {result_file}")
        return False, "Sender credentials not set in .env"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "TOPSIS Result"

    body = "Please find attached the result of your TOPSIS analysis."
    msg.attach(MIMEText(body, 'plain'))

    attachment = open(result_file, "rb")

    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % os.path.basename(result_file))

    msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        return True, None
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False, str(e)

def topsis_algorithm(input_file, weights_str, impacts_str):
    try:
        df = pd.read_csv(input_file)
        if df.shape[1] < 3:
            return None, "Input file must contain three or more columns."

        df_numeric = df.iloc[:, 1:].copy()
        try:
            df_numeric = df_numeric.apply(pd.to_numeric)
        except ValueError:
            return None, "From 2nd to last columns must contain numeric values only."

        try:
            weights = [float(w) for w in weights_str.split(',')]
            impacts = impacts_str.split(',')
        except ValueError:
            return None, "Weights must be numeric."

        if len(weights) != df_numeric.shape[1] or len(impacts) != df_numeric.shape[1]:
            return None, "Number of weights/impacts must match input columns."

        if not all([i in ['+', '-'] for i in impacts]):
            return None, "Impacts must be '+' or '-'."

        normalized_df = df_numeric.div(np.sqrt((df_numeric**2).sum()), axis=1)
        weighted_normalized_df = normalized_df.mul(weights, axis=1)

        ideal_best = []
        ideal_worst = []

        for col_idx, col in enumerate(weighted_normalized_df.columns):
            if impacts[col_idx] == '+':
                ideal_best.append(weighted_normalized_df[col].max())
                ideal_worst.append(weighted_normalized_df[col].min())
            else:
                ideal_best.append(weighted_normalized_df[col].min())
                ideal_worst.append(weighted_normalized_df[col].max())

        s_plus = np.sqrt(((weighted_normalized_df - ideal_best) ** 2).sum(axis=1))
        s_minus = np.sqrt(((weighted_normalized_df - ideal_worst) ** 2).sum(axis=1))

        total_dist = s_plus + s_minus
        performance_score = np.divide(s_minus, total_dist, out=np.zeros_like(s_minus), where=total_dist!=0)

        df['Topsis Score'] = performance_score
        df['Rank'] = df['Topsis Score'].rank(ascending=False).astype(int)

        output_filename = f"result_{os.path.basename(input_file)}"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        df.to_csv(output_path, index=False)
        return output_path, None

    except Exception as e:
        return None, str(e)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        email = request.form['email']
        weights = request.form['weights']
        impacts = request.form['impacts']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            result_file, error = topsis_algorithm(filepath, weights, impacts)

            if error:
                flash(f"Error: {error}")
                return redirect(request.url)
            
            # Send Email
            email_sent, error_msg = send_email(email, result_file)
            
            if email_sent:
                flash(f"Success! Result sent to {email}")
            else:
                flash(f"Success! Result generated, but email failed: {error_msg}")

            return redirect(request.url)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
