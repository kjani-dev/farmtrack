from flask import Flask, render_template, request, redirect, url_for, Response
import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/log', methods=['GET', 'POST'])
def log_cost():
    data_file = '/home/farmtrackdev/farmtrack/data/entries.json'
    if request.method == 'POST':
        field_name = request.form['field_name']
        if field_name == '__new__':
            field_name = request.form['new_field_name'].strip()
        entry = {
            'field_name': field_name,
            'acres': request.form['acres'],
            'input_type': request.form['input_type'],
            'cost': request.form['cost'],
            'date': request.form['date']
        }
        if os.path.exists(data_file):
            with open(data_file, 'r') as f:
                entries = json.load(f)
        else:
            entries = []
        entries.append(entry)
        with open(data_file, 'w') as f:
            json.dump(entries, f)
        return redirect(url_for('dashboard'))
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            entries = json.load(f)
        existing_fields = sorted(set(
            (e['field_name'], e['acres']) for e in entries
        ), key=lambda x: x[0])
    else:
        existing_fields = []
    return render_template('log_cost.html', existing_fields=existing_fields)

@app.route('/view')
def view_costs():
    data_file = '/home/farmtrackdev/farmtrack/data/entries.json'
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            entries = json.load(f)
    else:
        entries = []
    fields = {}
    for entry in entries:
        name = entry['field_name']
        if name not in fields:
            fields[name] = {'acres': entry['acres'], 'costs': []}
        fields[name]['costs'].append({
            'input_type': entry['input_type'],
            'cost': float(entry['cost']),
            'date': entry['date']
        })
    return render_template('view_costs.html', fields=fields)

@app.route('/summary')
def summary():
    data_file = '/home/farmtrackdev/farmtrack/data/entries.json'
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            entries = json.load(f)
    else:
        entries = []
    fields = {}
    for entry in entries:
        name = entry['field_name']
        if name not in fields:
            fields[name] = {'acres': float(entry['acres']), 'total_cost': 0}
        fields[name]['total_cost'] += float(entry['cost'])
    for field in fields.values():
        field['cost_per_acre'] = field['total_cost'] / field['acres']
    grand_total = sum(f['total_cost'] for f in fields.values())
    return render_template('summary.html', fields=fields, grand_total=grand_total)

@app.route('/delete/<int:index>')
def delete_entry(index):
    data_file = '/home/farmtrackdev/farmtrack/data/entries.json'
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            entries = json.load(f)
    if 0 <= index < len(entries):
        entries.pop(index)
    with open(data_file, 'w') as f:
        json.dump(entries, f)
    return redirect(url_for('view_costs'))

@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit_entry(index):
    data_file = '/home/farmtrackdev/farmtrack/data/entries.json'
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            entries = json.load(f)
    else:
        entries = []
    if request.method == 'POST':
        entries[index] = {
            'field_name': request.form['field_name'],
            'acres': request.form['acres'],
            'input_type': request.form['input_type'],
            'cost': request.form['cost'],
            'date': request.form['date']
        }
        with open(data_file, 'w') as f:
            json.dump(entries, f)
        return redirect(url_for('view_costs'))
    entry = entries[index]
    return render_template('edit_entry.html', entry=entry, index=index)

@app.route('/download')
def download_pdf():
    data_file = '/home/farmtrackdev/farmtrack/data/entries.json'
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            entries = json.load(f)
    else:
        entries = []
    fields = {}
    for entry in entries:
        name = entry['field_name']
        if name not in fields:
            fields[name] = {'acres': float(entry['acres']), 'total_cost': 0}
        fields[name]['total_cost'] += float(entry['cost'])
    for field in fields.values():
        field['cost_per_acre'] = field['total_cost'] / field['acres']
    grand_total = sum(f['total_cost'] for f in fields.values())

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "FarmTrack Season Cost Report")
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 70, "Manitoba Farm Input Cost Summary")

    y = height - 120
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, f"Total Season Cost: ${grand_total:.2f}")
    y -= 40

    for field_name, field in fields.items():
        p.setFont("Helvetica-Bold", 13)
        p.drawString(50, y, f"Field: {field_name}")
        y -= 20
        p.setFont("Helvetica", 12)
        p.drawString(50, y, f"Acres: {field['acres']}")
        y -= 20
        p.drawString(50, y, f"Total Cost: ${field['total_cost']:.2f}")
        y -= 20
        p.drawString(50, y, f"Cost Per Acre: ${field['cost_per_acre']:.2f}")
        y -= 30

    p.save()
    buffer.seek(0)

    return Response(buffer, mimetype='application/pdf',
        headers={'Content-Disposition': 'attachment;filename=farmtrack_report.pdf'})

if __name__ == '__main__':
    app.run(debug=True)
