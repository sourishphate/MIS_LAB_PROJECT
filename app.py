from flask import Flask, render_template, request, redirect, session, url_for, g, make_response
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'mis_secret_key_2024'
DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    db = get_db()
    db.execute(query, args)
    db.commit()

def log_action(user_id, user_name, user_role, action, details=''):
    execute_db('INSERT INTO audit_log (user_id,user_name,user_role,action,details) VALUES (?,?,?,?,?)',
               (user_id, user_name, user_role, action, details))

def generate_incident_id():
    last = query_db("SELECT incident_id FROM incidents ORDER BY id DESC LIMIT 1", one=True)
    num = int(last['incident_id'].split('-')[1]) + 1 if last else 1
    return f"INC-{num:03d}"

# ── INIT DB ──────────────────────────────────

def init_db():
    with app.app_context():
        db = get_db()
        db.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL, role TEXT NOT NULL,
            department TEXT DEFAULT '', phone TEXT DEFAULT '',
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP);

        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id TEXT UNIQUE NOT NULL,
            type TEXT NOT NULL, description TEXT NOT NULL,
            severity TEXT NOT NULL, affected_resources TEXT NOT NULL,
            affected_systems TEXT DEFAULT '', estimated_impact TEXT DEFAULT '',
            no_of_users_affected TEXT DEFAULT '', location TEXT DEFAULT '',
            occurred_at TEXT NOT NULL, discovered_at TEXT DEFAULT '',
            status TEXT DEFAULT 'Reported', reported_by INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(reported_by) REFERENCES users(id));

        CREATE TABLE IF NOT EXISTS classifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id INTEGER UNIQUE,
            severity_category TEXT, impact_level TEXT, priority TEXT,
            classified_by INTEGER, classified_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(incident_id) REFERENCES incidents(id));

        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id INTEGER UNIQUE, assigned_to INTEGER, assigned_by INTEGER,
            assigned_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(incident_id) REFERENCES incidents(id),
            FOREIGN KEY(assigned_to) REFERENCES users(id));

        CREATE TABLE IF NOT EXISTS investigations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id INTEGER UNIQUE,
            findings TEXT DEFAULT '', actions_taken TEXT DEFAULT '',
            resolution_details TEXT DEFAULT '',
            updated_by INTEGER, updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(incident_id) REFERENCES incidents(id));

        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, user_name TEXT, user_role TEXT,
            action TEXT NOT NULL, details TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id));
        ''')
        db.commit()

        if db.execute('SELECT COUNT(*) FROM users').fetchone()[0] == 0:
            seed_users = [
                ('Arjun Mehta','reporter@mis.com',generate_password_hash('reporter123'),'reporter','HR Department','9876543210'),
                ('Priya Sharma','analyst@mis.com',generate_password_hash('analyst123'),'analyst','IT Security','9876543211'),
                ('Rahul Desai','analyst2@mis.com',generate_password_hash('analyst456'),'analyst','IT Security','9876543212'),
                ('Neha Kulkarni','admin@mis.com',generate_password_hash('admin123'),'admin','System Admin','9876543213'),
                ('Vikram Joshi','management@mis.com',generate_password_hash('management123'),'management','Senior Management','9876543214'),
                ('Sneha Patil','reporter2@mis.com',generate_password_hash('reporter456'),'reporter','Finance','9876543215'),
            ]
            for u in seed_users:
                db.execute('INSERT INTO users (name,email,password,role,department,phone) VALUES (?,?,?,?,?,?)', u)
            db.commit()

        if db.execute('SELECT COUNT(*) FROM incidents').fetchone()[0] == 0:
            rid  = db.execute("SELECT id FROM users WHERE email='reporter@mis.com'").fetchone()[0]
            rid2 = db.execute("SELECT id FROM users WHERE email='reporter2@mis.com'").fetchone()[0]
            aid  = db.execute("SELECT id FROM users WHERE email='analyst@mis.com'").fetchone()[0]
            aid2 = db.execute("SELECT id FROM users WHERE email='analyst2@mis.com'").fetchone()[0]
            adm  = db.execute("SELECT id FROM users WHERE email='admin@mis.com'").fetchone()[0]

            incs = [
              ('INC-001','Phishing','Employee received phishing email with malicious link mimicking IT helpdesk. Clicked link and entered credentials on fake portal.','High','Email Server, User Account','Outlook, Active Directory','Credential theft, data exposure','1','Mumbai HQ','2024-03-01 09:30','2024-03-01 10:00','Closed',rid),
              ('INC-002','Malware','Ransomware detected on finance workstation. Multiple files encrypted. Backup server also affected.','Critical','Finance Workstation, File Server','Windows 10, File Server','Data loss, operational disruption','12','Pune Office','2024-03-05 14:00','2024-03-05 14:30','Resolved',rid),
              ('INC-003','Unauthorized Access','Multiple failed login attempts on admin portal from unknown external IP. Brute force attack pattern detected.','Medium','Admin Portal, Auth System','Web Portal, Auth Server','Possible account takeover','0','Remote','2024-03-10 11:00','2024-03-10 11:15','Under Investigation',rid2),
              ('INC-004','Data Breach','Sensitive customer data exposed on misconfigured AWS S3 bucket. Approx 5000 customer records visible publicly.','Critical','AWS S3, Customer Database','AWS S3, RDS Database','Customer PII exposed','5000','Cloud','2024-03-12 16:45','2024-03-12 17:00','Under Investigation',rid2),
              ('INC-005','Phishing','Bulk phishing campaign targeting HR employees mimicking payroll login. 3 employees clicked link and entered credentials.','High','HR Systems, Email Server','SAP HR, Email Gateway','Credential theft, payroll fraud risk','3','Mumbai HQ','2024-03-15 08:00','2024-03-15 08:45','Resolved',rid),
              ('INC-006','Unauthorized Access','Former employee account not deactivated post resignation. Account used to access SharePoint 3 times.','High','Document Management System','SharePoint, VPN','IP theft, data leakage','1','Remote','2024-03-18 13:20','2024-03-18 14:00','Closed',rid),
              ('INC-007','Malware','Keylogger found on shared reception computer. Installed via unknown USB device left at front desk.','Medium','Reception Computer','Windows PC','Keystroke capture, data theft','0','Mumbai HQ','2024-03-20 10:10','2024-03-20 10:30','Closed',rid2),
              ('INC-008','Data Breach','Employee accidentally emailed confidential project file with client financials to wrong external recipient.','Low','Email System, Project Files','Outlook, OneDrive','Confidential data exposed to external party','1','Mumbai HQ','2024-03-22 15:00','2024-03-22 15:10','Reported',rid),
            ]
            for i in incs:
                db.execute('''INSERT INTO incidents (incident_id,type,description,severity,affected_resources,
                    affected_systems,estimated_impact,no_of_users_affected,location,occurred_at,discovered_at,status,reported_by)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''', i)
            db.commit()

            for row in db.execute('SELECT id,severity,status FROM incidents').fetchall():
                if row['status'] != 'Reported':
                    p = 'P1 - Critical' if row['severity']=='Critical' else 'P2 - High' if row['severity']=='High' else 'P3 - Medium' if row['severity']=='Medium' else 'P4 - Low'
                    imp = 'Critical' if row['severity']=='Critical' else 'High' if row['severity']=='High' else 'Moderate'
                    db.execute('INSERT OR IGNORE INTO classifications (incident_id,severity_category,impact_level,priority,classified_by) VALUES (?,?,?,?,?)',
                               (row['id'], row['severity'], imp, p, adm))

            for i,row in enumerate(db.execute("SELECT id FROM incidents WHERE status IN ('Under Investigation','Resolved','Closed')").fetchall()):
                db.execute('INSERT OR IGNORE INTO assignments (incident_id,assigned_to,assigned_by) VALUES (?,?,?)',
                           (row['id'], aid if i%2==0 else aid2, adm))

            inv_data = [
                ('Credentials confirmed compromised via fake portal. Phishing email traced to spoofed domain.','Blocked sender domain, reset all affected passwords, enabled MFA for all users, phishing awareness training conducted.','Incident resolved. MFA now mandatory. Phishing training completed for all staff.'),
                ('LockBit 3.0 ransomware. Entry via phishing attachment 2 days prior. 12 workstations affected.','Isolated all workstations from network, restored from last clean backup, patched OS and AV signatures on all machines.','All files restored. 3 workstations reimaged. Security patches applied organisation-wide.'),
                ('3 HR accounts compromised. Payroll domain spoofed using look-alike domain name.','Disabled 3 compromised accounts, reset passwords, blacklisted domain, notified payroll team, reviewed all recent transactions.','Accounts secured. No payroll fraud detected. Awareness training scheduled for HR.'),
                ('Former employee VPN access not revoked during off-boarding. Accessed SharePoint on 3 occasions.','Disabled account and VPN access immediately, reviewed all documents accessed, notified legal and HR teams.','Access removed. Off-boarding checklist updated. All future exits now include immediate IT access revocation.'),
                ('Ardamax commercial keylogger installed via USB autorun on shared reception PC.','Machine wiped and reimaged, USB autorun disabled via GPO, USB ports restricted on all shared PCs company-wide.','Machine clean. USB policy enforced via Group Policy across all shared computers.'),
            ]
            for i,row in enumerate(db.execute("SELECT id FROM incidents WHERE status IN ('Resolved','Closed')").fetchall()):
                if i < len(inv_data):
                    db.execute('INSERT OR IGNORE INTO investigations (incident_id,findings,actions_taken,resolution_details,updated_by) VALUES (?,?,?,?,?)',
                               (row['id'], inv_data[i][0], inv_data[i][1], inv_data[i][2], aid))
            db.commit()

            audit_seeds = [
                (rid, 'Arjun Mehta','reporter','Incident Submitted','Submitted INC-001 — Phishing — High severity'),
                (adm, 'Neha Kulkarni','admin','Incident Classified','Classified INC-001 — Priority: P2 High | Impact: High'),
                (adm, 'Neha Kulkarni','admin','Incident Assigned','Assigned INC-001 to Priya Sharma'),
                (aid, 'Priya Sharma','analyst','Status Updated','INC-001 changed to Under Investigation'),
                (aid, 'Priya Sharma','analyst','Investigation Filed','Filed investigation findings for INC-001'),
                (aid, 'Priya Sharma','analyst','Status Updated','INC-001 changed to Resolved'),
                (adm, 'Neha Kulkarni','admin','Incident Closed','Formally closed INC-001'),
                (rid2,'Sneha Patil','reporter','Incident Submitted','Submitted INC-003 — Unauthorized Access — Medium severity'),
                (adm, 'Neha Kulkarni','admin','Incident Classified','Classified INC-003 — Priority: P3 Medium | Impact: Moderate'),
                (adm, 'Neha Kulkarni','admin','Incident Assigned','Assigned INC-003 to Rahul Desai'),
            ]
            for l in audit_seeds:
                db.execute('INSERT INTO audit_log (user_id,user_name,user_role,action,details) VALUES (?,?,?,?,?)', l)
            db.commit()

# ── AUTH ─────────────────────────────────────

@app.route('/', methods=['GET','POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for(session['role'] + '_dashboard'))
    error = None
    if request.method == 'POST':
        user = query_db('SELECT * FROM users WHERE email=? AND is_active=1', [request.form['email']], one=True)
        if user and check_password_hash(user['password'], request.form['password']):
            session.update({'user_id':user['id'],'user_name':user['name'],'role':user['role']})
            log_action(user['id'], user['name'], user['role'], 'Login', 'Logged in successfully')
            return redirect(url_for(user['role'] + '_dashboard'))
        error = 'Invalid email or password.'
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET','POST'])
def register():
    error = success = None
    if request.method == 'POST':
        name  = request.form['name'].strip()
        email = request.form['email'].strip()
        pw    = request.form['password']
        cpw   = request.form['confirm_password']
        dept  = request.form.get('department','')
        phone = request.form.get('phone','')
        if pw != cpw:
            error = 'Passwords do not match.'
        elif len(pw) < 6:
            error = 'Password must be at least 6 characters.'
        elif query_db('SELECT id FROM users WHERE email=?', [email], one=True):
            error = 'An account with this email already exists.'
        else:
            execute_db('INSERT INTO users (name,email,password,role,department,phone) VALUES (?,?,?,?,?,?)',
                       (name, email, generate_password_hash(pw), 'reporter', dept, phone))
            success = 'Account created! You can now log in as a Reporter.'
    return render_template('register.html', error=error, success=success)

@app.route('/logout')
def logout():
    if 'user_id' in session:
        log_action(session['user_id'], session['user_name'], session['role'], 'Logout', 'User logged out')
    session.clear()
    return redirect(url_for('login'))

# ── REPORTER ─────────────────────────────────

@app.route('/reporter')
def reporter_dashboard():
    if session.get('role') != 'reporter': return redirect(url_for('login'))
    submitted = request.args.get('submitted','')
    new_inc   = None
    if submitted:
        new_inc = query_db('SELECT * FROM incidents WHERE incident_id=?', [submitted], one=True)

    incidents = query_db('''
        SELECT i.*,
               inv.findings,
               inv.actions_taken,
               inv.resolution_details
        FROM incidents i
        LEFT JOIN investigations inv ON i.id = inv.incident_id
        WHERE i.reported_by=?
        ORDER BY i.created_at DESC
    ''', [session['user_id']])

    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('reporter.html', incidents=incidents, new_inc=new_inc,
                           form_data=None, today=today)

@app.route('/reporter/submit', methods=['POST'])
def submit_incident():
    if session.get('role') != 'reporter': return redirect(url_for('login'))

    # Collect all form data
    inc_type      = request.form.get('type','')
    description   = request.form.get('description','')
    severity      = request.form.get('severity','')
    resources     = request.form.get('affected_resources','')
    occurred_at   = request.form.get('occurred_at','')
    discovered_at = request.form.get('discovered_at','')

    # Validate required fields — if missing, return form with data preserved
    if not inc_type or not description or not severity or not resources or not occurred_at:
        incidents = query_db('''
            SELECT i.*,
                inv.findings,
                inv.actions_taken,
                inv.resolution_details
            FROM incidents i
            LEFT JOIN investigations inv ON i.id = inv.incident_id
            WHERE i.reported_by=?
            ORDER BY i.created_at DESC
        ''', [session['user_id']])
        today = datetime.now().strftime('%Y-%m-%d')
        # Pass all form values back so nothing is lost
        class FormData:
            pass
        fd = FormData()
        fd.type               = inc_type
        fd.description        = description
        fd.severity           = severity
        fd.affected_resources = resources
        fd.affected_systems   = request.form.get('affected_systems','')
        fd.no_of_users_affected = request.form.get('no_of_users_affected','')
        fd.location           = request.form.get('location','')
        fd.estimated_impact   = request.form.get('estimated_impact','')
        fd.occurred_date      = request.form.get('occurred_date','')
        fd.occurred_time      = request.form.get('occurred_time','')
        fd.discovered_date    = request.form.get('discovered_date','')
        fd.discovered_time    = request.form.get('discovered_time','')
        return render_template('reporter.html', incidents=incidents, new_inc=None,
                               form_data=fd, today=today,
                               form_error='Please fill in all required fields.')

    iid = generate_incident_id()
    execute_db('''INSERT INTO incidents
        (incident_id,type,description,severity,affected_resources,affected_systems,
         estimated_impact,no_of_users_affected,location,occurred_at,discovered_at,status,reported_by)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''',
        (iid, inc_type, description, severity, resources,
         request.form.get('affected_systems',''),
         request.form.get('estimated_impact',''),
         request.form.get('no_of_users_affected',''),
         request.form.get('location',''),
         occurred_at, discovered_at, 'Reported', session['user_id']))
    log_action(session['user_id'], session['user_name'], session['role'],
               'Incident Submitted', f"Submitted {iid} — {inc_type} — {severity} severity")
    return redirect(url_for('reporter_dashboard') + f'?submitted={iid}')

@app.route('/reporter/ticket/<incident_id>')
def download_ticket(incident_id):
    if session.get('role') != 'reporter': return redirect(url_for('login'))

    inc = query_db('''
        SELECT i.*,
               u.name as rname,
               u.email as remail,
               u.department as rdept,
               u.phone as rphone,
               inv.findings,
               inv.actions_taken,
               inv.resolution_details
        FROM incidents i
        JOIN users u ON i.reported_by = u.id
        LEFT JOIN investigations inv ON i.id = inv.incident_id
        WHERE i.incident_id=? AND i.reported_by=?
    ''', [incident_id, session['user_id']], one=True)

    if not inc: return redirect(url_for('reporter_dashboard'))

    now = datetime.now().strftime('%d %B %Y, %I:%M %p')
    sc  = {'Critical':'#991b1b','High':'#9a3412','Medium':'#854d0e','Low':'#166534'}.get(inc['severity'],'#374151')
    sb  = {'Critical':'#fee2e2','High':'#ffedd5','Medium':'#fef9c3','Low':'#f0fdf4'}.get(inc['severity'],'#f3f4f6')

    closure_section = ''
    if inc['status'] == 'Closed':
        closure_section = f'''
    <div class="section">
      <div class="sec-title">Closure Details</div>
      <div class="desc-box">
        <strong>Findings:</strong><br>
        {inc['findings'] or 'No findings recorded.'}
        <br><br>

        <strong>Actions Taken:</strong><br>
        {inc['actions_taken'] or 'No actions recorded.'}
        <br><br>

        <strong>Resolution Details:</strong><br>
        {inc['resolution_details'] or 'No resolution details recorded.'}
      </div>
    </div>
'''

    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"/>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',Arial,sans-serif;background:#f1f5f9;padding:20px;color:#1e293b}}
.ticket{{max-width:780px;margin:0 auto;background:white;border-radius:14px;overflow:hidden;box-shadow:0 8px 30px rgba(0,0,0,0.12)}}
.hdr{{background:linear-gradient(135deg,#0f172a,#1e40af);color:white;padding:30px 36px}}
.hdr h1{{font-size:1.3rem;font-weight:800;margin-bottom:4px}}
.hdr p{{opacity:.75;font-size:.82rem}}
.inc-id{{font-family:monospace;font-size:1.5rem;font-weight:900;color:#93c5fd;letter-spacing:2px;margin:14px 0 8px}}
.sev-badge{{display:inline-block;padding:5px 16px;border-radius:20px;font-size:.78rem;font-weight:700;background:{sb};color:{sc}}}
.body{{padding:30px 36px}}
.section{{margin-bottom:22px}}
.sec-title{{font-size:.7rem;text-transform:uppercase;letter-spacing:.1em;color:#64748b;font-weight:800;padding-bottom:6px;border-bottom:2px solid #e2e8f0;margin-bottom:12px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
.grid3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px}}
.field{{background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:10px 14px}}
.field label{{font-size:.7rem;color:#94a3b8;text-transform:uppercase;letter-spacing:.05em;display:block;margin-bottom:4px;font-weight:600}}
.field span{{font-size:.88rem;color:#1e293b;font-weight:600}}
.desc-box{{background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:14px;font-size:.88rem;line-height:1.7;color:#334155}}
.status-row{{display:flex;align-items:center;justify-content:space-between;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:12px 18px;margin-bottom:22px}}
.status-left{{display:flex;align-items:center;gap:10px}}
.dot{{width:12px;height:12px;border-radius:50%;background:#22c55e;box-shadow:0 0 0 3px rgba(34,197,94,.2)}}
.status-label{{font-weight:700;color:#166534;font-size:.92rem}}
.ref{{color:#64748b;font-size:.78rem}}
.ftr{{background:#f8fafc;border-top:2px dashed #e2e8f0;padding:18px 36px;text-align:center}}
.ftr p{{font-size:.75rem;color:#94a3b8;line-height:1.6}}
.ftr strong{{color:#64748b}}
.watermark{{margin-top:8px;font-size:.7rem;color:#cbd5e1;text-transform:uppercase;letter-spacing:.1em}}
@media print{{body{{background:white;padding:0}}.ticket{{box-shadow:none}}}}
</style></head><body>
<div class="ticket">
  <div class="hdr">
    <h1>🛡️ Cyber Incident Report — Official Ticket</h1>
    <p>Cyber Incident Reporting & Analysis Management Information System — Confidential</p>
    <div class="inc-id">{inc['incident_id']}</div>
    <span class="sev-badge">{inc['severity']} Severity</span>
  </div>
  <div class="body">
    <div class="status-row">
      <div class="status-left"><div class="dot"></div><span class="status-label">Status: {inc['status']}</span></div>
      <span class="ref">Submitted: {inc['created_at'][:16]}</span>
    </div>

    <div class="section">
      <div class="sec-title">Incident Information</div>
      <div class="grid3">
        <div class="field"><label>Incident Type</label><span>{inc['type']}</span></div>
        <div class="field"><label>Severity Level</label><span>{inc['severity']}</span></div>
        <div class="field"><label>Location</label><span>{inc['location'] or '—'}</span></div>
        <div class="field"><label>Date & Time Occurred</label><span>{inc['occurred_at']}</span></div>
        <div class="field"><label>Date & Time Discovered</label><span>{inc['discovered_at'] or '—'}</span></div>
        <div class="field"><label>Users Affected</label><span>{inc['no_of_users_affected'] or '—'}</span></div>
      </div>
    </div>

    <div class="section">
      <div class="sec-title">Affected Systems & Impact</div>
      <div class="grid2">
        <div class="field"><label>Affected Resources</label><span>{inc['affected_resources']}</span></div>
        <div class="field"><label>Affected Systems</label><span>{inc['affected_systems'] or '—'}</span></div>
        <div class="field" style="grid-column:1/-1"><label>Estimated Impact</label><span>{inc['estimated_impact'] or '—'}</span></div>
      </div>
    </div>

    <div class="section">
      <div class="sec-title">Incident Description</div>
      <div class="desc-box">{inc['description']}</div>
    </div>

    {closure_section}

    <div class="section">
      <div class="sec-title">Reporter Information</div>
      <div class="grid2">
        <div class="field"><label>Reported By</label><span>{inc['rname']}</span></div>
        <div class="field"><label>Email Address</label><span>{inc['remail']}</span></div>
        <div class="field"><label>Department</label><span>{inc['rdept'] or '—'}</span></div>
        <div class="field"><label>Contact Number</label><span>{inc['rphone'] or '—'}</span></div>
      </div>
    </div>
  </div>

  <div class="ftr">
    <p>This is an officially generated incident ticket. Generated on <strong>{now}</strong></p>
    <p>Please retain this document. Quote Incident ID <strong>{inc['incident_id']}</strong> in all future communications.</p>
    <div class="watermark">Cyber Incident MIS — Internal Use Only — Do Not Distribute</div>
  </div>
</div>
<script>window.onload=function(){{window.print()}}</script>
</body></html>"""

    response = make_response(html)
    response.headers['Content-Type'] = 'text/html'
    return response

# ── ANALYST ──────────────────────────────────

@app.route('/analyst')
def analyst_dashboard():
    if session.get('role') != 'analyst': return redirect(url_for('login'))
    incidents = query_db('''
        SELECT i.*, a.assigned_at,
               inv.findings, inv.actions_taken, inv.resolution_details, inv.updated_at as inv_updated_at,
               u.name as reporter_name, u.department as reporter_dept,
               c.severity_category, c.impact_level, c.priority
        FROM incidents i
        JOIN assignments a ON i.id=a.incident_id
        LEFT JOIN investigations inv ON i.id=inv.incident_id
        LEFT JOIN users u ON i.reported_by=u.id
        LEFT JOIN classifications c ON i.id=c.incident_id
        WHERE a.assigned_to=?
        ORDER BY
          CASE i.status WHEN 'Under Investigation' THEN 1 WHEN 'Reported' THEN 2
                        WHEN 'Resolved' THEN 3 WHEN 'Closed' THEN 4 END,
          i.created_at DESC''', [session['user_id']])
    return render_template('analyst.html', incidents=incidents)

@app.route('/analyst/update/<int:inc_id>', methods=['POST'])
def update_investigation(inc_id):
    if session.get('role') != 'analyst': return redirect(url_for('login'))
    if not query_db('SELECT id FROM assignments WHERE incident_id=? AND assigned_to=?',
                    [inc_id, session['user_id']], one=True):
        return redirect(url_for('analyst_dashboard'))
    status     = request.form['status']
    findings   = request.form.get('findings','')
    actions    = request.form.get('actions_taken','')
    resolution = request.form.get('resolution_details','')
    now        = datetime.now().strftime('%Y-%m-%d %H:%M')
    execute_db('UPDATE incidents SET status=? WHERE id=?', (status, inc_id))
    if query_db('SELECT id FROM investigations WHERE incident_id=?', [inc_id], one=True):
        execute_db('UPDATE investigations SET findings=?,actions_taken=?,resolution_details=?,updated_by=?,updated_at=? WHERE incident_id=?',
                   (findings, actions, resolution, session['user_id'], now, inc_id))
    else:
        execute_db('INSERT INTO investigations (incident_id,findings,actions_taken,resolution_details,updated_by,updated_at) VALUES (?,?,?,?,?,?)',
                   (inc_id, findings, actions, resolution, session['user_id'], now))
    inc = query_db('SELECT incident_id FROM incidents WHERE id=?', [inc_id], one=True)
    log_action(session['user_id'], session['user_name'], session['role'],
               'Investigation Updated', f"Updated {inc['incident_id']} — Status: {status}")
    return redirect(url_for('analyst_dashboard'))

# ── ADMIN ─────────────────────────────────────

@app.route('/admin')
def admin_dashboard():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    incidents = query_db('''
        SELECT i.*, u.name as reporter_name,
               c.severity_category, c.impact_level, c.priority,
               a2.name as assigned_to_name, a.assigned_at
        FROM incidents i JOIN users u ON i.reported_by=u.id
        LEFT JOIN classifications c ON i.id=c.incident_id
        LEFT JOIN assignments a ON i.id=a.incident_id
        LEFT JOIN users a2 ON a.assigned_to=a2.id
        ORDER BY CASE i.status WHEN 'Reported' THEN 1 WHEN 'Under Investigation' THEN 2
                               WHEN 'Resolved' THEN 3 WHEN 'Closed' THEN 4 END, i.created_at DESC''')
    analysts  = query_db("SELECT id,name FROM users WHERE role='analyst' AND is_active=1")
    users     = query_db("SELECT * FROM users ORDER BY role,name")
    logs      = query_db("SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 300")
    log_stats = {
        'total':    query_db("SELECT COUNT(*) as c FROM audit_log", one=True)['c'],
        'reporter': query_db("SELECT COUNT(*) as c FROM audit_log WHERE user_role='reporter'", one=True)['c'],
        'analyst':  query_db("SELECT COUNT(*) as c FROM audit_log WHERE user_role='analyst'", one=True)['c'],
        'admin':    query_db("SELECT COUNT(*) as c FROM audit_log WHERE user_role='admin'", one=True)['c'],
        'mgmt':     query_db("SELECT COUNT(*) as c FROM audit_log WHERE user_role='management'", one=True)['c'],
    }
    return render_template('admin.html', incidents=incidents, analysts=analysts,
                           users=users, logs=logs, log_stats=log_stats)

@app.route('/admin/classify/<int:inc_id>', methods=['POST'])
def classify_incident(inc_id):
    if session.get('role') != 'admin': return redirect(url_for('login'))

    sev_cat  = request.form['severity_category']
    impact   = request.form['impact_level']
    priority = request.form['priority']
    now      = datetime.now().strftime('%Y-%m-%d %H:%M')

    # FIX: keep main incident severity updated also
    execute_db('UPDATE incidents SET severity=? WHERE id=?', (sev_cat, inc_id))

    if query_db('SELECT id FROM classifications WHERE incident_id=?', [inc_id], one=True):
        execute_db('UPDATE classifications SET severity_category=?,impact_level=?,priority=?,classified_by=?,classified_at=? WHERE incident_id=?',
                   (sev_cat, impact, priority, session['user_id'], now, inc_id))
    else:
        execute_db('INSERT INTO classifications (incident_id,severity_category,impact_level,priority,classified_by,classified_at) VALUES (?,?,?,?,?,?)',
                   (inc_id, sev_cat, impact, priority, session['user_id'], now))

    inc = query_db('SELECT incident_id FROM incidents WHERE id=?', [inc_id], one=True)

    log_action(session['user_id'], session['user_name'], session['role'],
               'Incident Classified', f"Classified {inc['incident_id']} — Severity: {sev_cat} | Impact: {impact} | Priority: {priority}")

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/assign/<int:inc_id>', methods=['POST'])
def assign_incident(inc_id):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    analyst_id = request.form['analyst_id']
    now        = datetime.now().strftime('%Y-%m-%d %H:%M')
    if query_db('SELECT id FROM assignments WHERE incident_id=?', [inc_id], one=True):
        execute_db('UPDATE assignments SET assigned_to=?,assigned_by=?,assigned_at=? WHERE incident_id=?',
                   (analyst_id, session['user_id'], now, inc_id))
    else:
        execute_db('INSERT INTO assignments (incident_id,assigned_to,assigned_by,assigned_at) VALUES (?,?,?,?)',
                   (inc_id, analyst_id, session['user_id'], now))
    execute_db("UPDATE incidents SET status='Under Investigation' WHERE id=? AND status='Reported'", [inc_id])
    inc     = query_db('SELECT incident_id FROM incidents WHERE id=?', [inc_id], one=True)
    analyst = query_db('SELECT name FROM users WHERE id=?', [analyst_id], one=True)
    log_action(session['user_id'], session['user_name'], session['role'],
               'Incident Assigned', f"Assigned {inc['incident_id']} to {analyst['name']}")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/close/<int:inc_id>', methods=['POST'])
def close_incident(inc_id):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    execute_db("UPDATE incidents SET status='Closed' WHERE id=?", [inc_id])
    inc = query_db('SELECT incident_id FROM incidents WHERE id=?', [inc_id], one=True)
    log_action(session['user_id'], session['user_name'], session['role'],
               'Incident Closed', f"Formally closed {inc['incident_id']}")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_user', methods=['POST'])
def add_user():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    try:
        name  = request.form['name']
        email = request.form['email']
        role  = request.form['role']
        execute_db('INSERT INTO users (name,email,password,role,department,phone) VALUES (?,?,?,?,?,?)',
                   (name, email, generate_password_hash(request.form['password']),
                    role, request.form.get('department',''), request.form.get('phone','')))
        log_action(session['user_id'], session['user_name'], session['role'],
                   'User Created', f"Created account: {name} — Role: {role}")
    except: pass
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/toggle_user/<int:user_id>', methods=['POST'])
def toggle_user(user_id):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    user = query_db('SELECT * FROM users WHERE id=?', [user_id], one=True)
    new_s = 0 if user['is_active'] else 1
    execute_db('UPDATE users SET is_active=? WHERE id=?', (new_s, user_id))
    action = 'User Activated' if new_s else 'User Deactivated'
    log_action(session['user_id'], session['user_name'], session['role'],
               action, f"{user['name']} ({user['role']}) — {action}")
    return redirect(url_for('admin_dashboard'))

# ── MANAGEMENT ───────────────────────────────

@app.route('/management')
def management_dashboard():
    if session.get('role') != 'management': return redirect(url_for('login'))
    f_type=request.args.get('type',''); f_sev=request.args.get('severity','')
    f_stat=request.args.get('status',''); f_from=request.args.get('date_from',''); f_to=request.args.get('date_to','')
    q = '''SELECT i.*, u.name as reporter_name, u.department,
                  a2.name as assigned_to_name,
                  c.severity_category, c.impact_level, c.priority,
                  inv.findings, inv.actions_taken, inv.resolution_details
           FROM incidents i JOIN users u ON i.reported_by=u.id
           LEFT JOIN assignments a ON i.id=a.incident_id
           LEFT JOIN users a2 ON a.assigned_to=a2.id
           LEFT JOIN classifications c ON i.id=c.incident_id
           LEFT JOIN investigations inv ON i.id=inv.incident_id WHERE 1=1'''
    p=[]
    if f_type:  q+=' AND i.type=?';        p.append(f_type)
    if f_sev:   q+=' AND i.severity=?';    p.append(f_sev)
    if f_stat:  q+=' AND i.status=?';      p.append(f_stat)
    if f_from:  q+=' AND i.occurred_at>=?';p.append(f_from)
    if f_to:    q+=' AND i.occurred_at<=?';p.append(f_to+' 23:59')
    q+=' ORDER BY i.created_at DESC'
    incidents   = query_db(q, p)
    total       = query_db('SELECT COUNT(*) as c FROM incidents', one=True)['c']
    open_inc    = query_db("SELECT COUNT(*) as c FROM incidents WHERE status NOT IN ('Closed','Resolved')", one=True)['c']
    resolved    = query_db("SELECT COUNT(*) as c FROM incidents WHERE status IN ('Resolved','Closed')", one=True)['c']
    critical    = query_db("SELECT COUNT(*) as c FROM incidents WHERE severity='Critical'", one=True)['c']
    type_data   = query_db("SELECT type,COUNT(*) as count FROM incidents GROUP BY type ORDER BY count DESC")
    sev_data    = query_db("SELECT severity,COUNT(*) as count FROM incidents GROUP BY severity")
    month_data  = query_db("SELECT substr(occurred_at,1,7) as month,COUNT(*) as count FROM incidents GROUP BY month ORDER BY month")
    status_data = query_db("SELECT status,COUNT(*) as count FROM incidents GROUP BY status")
    log_action(session['user_id'], session['user_name'], session['role'],
               'Dashboard Viewed', 'Management viewed incident analytics dashboard')
    return render_template('management.html', incidents=incidents,
        total=total, open_inc=open_inc, resolved=resolved, critical=critical,
        type_data=type_data, sev_data=sev_data, month_data=month_data, status_data=status_data,
        filters={'type':f_type,'severity':f_sev,'status':f_stat,'date_from':f_from,'date_to':f_to})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)