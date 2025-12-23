#!/usr/bin/env python3
"""
Plex Unwatched Reporter
Copyright (C) 2025 Thad A. Williams

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

from flask import Flask, render_template_string, request, jsonify, send_file
from plexapi.server import PlexServer
import csv
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)

CONFIG_FILE = '/config/config.json'
REPORTS_DIR = '/reports'

# Get Plex connection info from environment variables
PLEX_URL = os.environ.get('PLEX_URL', '')
PLEX_TOKEN = os.environ.get('PLEX_TOKEN', '')

# Global progress tracking
progress_data = {
    'current': 0,
    'total': 0,
    'current_library': '',
    'libraries_order': []
}

HTML_TEMPLATE = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Plex Unwatched Reporter</title><style>@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Share Tech Mono','Courier New',monospace;background:#000;color:#ffb000;padding:2rem;min-height:100vh;position:relative;overflow-x:hidden;background-image:linear-gradient(rgba(255,176,0,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(255,176,0,0.03) 1px,transparent 1px);background-size:50px 50px}body::before{content:"";position:fixed;top:0;left:0;width:100%;height:100%;background:repeating-linear-gradient(0deg,rgba(0,0,0,0.15),rgba(0,0,0,0.15) 1px,transparent 1px,transparent 2px);pointer-events:none;z-index:1000}body::after{content:"";position:fixed;top:0;left:0;width:100%;height:100%;background:radial-gradient(ellipse at center,rgba(255,176,0,0.1) 0%,transparent 70%);pointer-events:none;z-index:999}.container{max-width:1200px;margin:0 auto;position:relative;z-index:1}.header{margin-bottom:2rem;text-align:center;border:2px solid #ffb000;padding:1.5rem;background:rgba(255,176,0,0.05);box-shadow:0 0 20px rgba(255,176,0,0.3),inset 0 0 20px rgba(255,176,0,0.1);position:relative}.header::before{content:"▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲";position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:#000;padding:0 10px;font-size:0.5rem;letter-spacing:2px}.header h1{font-size:2.5rem;margin-bottom:0.5rem;text-shadow:0 0 10px rgba(255,176,0,0.8),0 0 20px rgba(255,176,0,0.6),0 0 30px rgba(255,176,0,0.4);letter-spacing:3px;animation:flicker 3s infinite alternate}@keyframes flicker{0%,100%{opacity:1}41.99%{opacity:1}42%{opacity:0.8}43%{opacity:1}45.99%{opacity:1}46%{opacity:0.85}46.5%{opacity:1}}.header p{color:#cc8800;text-transform:uppercase;letter-spacing:2px;font-size:0.9rem}.card{background:rgba(0,0,0,0.8);border:2px solid #ffb000;padding:1.5rem;margin-bottom:1.5rem;box-shadow:0 0 20px rgba(255,176,0,0.3),inset 0 0 40px rgba(255,176,0,0.05);position:relative}.card::before{content:"";position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,#ffb000,transparent);opacity:0.5}.card h2{font-size:1.5rem;margin-bottom:1rem;text-transform:uppercase;letter-spacing:3px;text-shadow:0 0 10px rgba(255,176,0,0.8);border-bottom:1px solid #ffb000;padding-bottom:0.5rem}.info-box{background:rgba(255,176,0,0.05);border-left:3px solid #ffb000;padding:0.75rem 1rem;margin-bottom:1.5rem;font-size:0.875rem;letter-spacing:1px;line-height:1.6}.form-group{margin-bottom:1rem}label{display:block;font-size:0.875rem;font-weight:500;margin-bottom:0.5rem;text-transform:uppercase;letter-spacing:1px;color:#ffb000}input[type="text"],input[type="number"]{width:100%;background:#000;border:2px solid #ffb000;color:#ffb000;padding:0.75rem 1rem;font-size:1rem;font-family:'Share Tech Mono',monospace;box-shadow:inset 0 0 10px rgba(255,176,0,0.2)}input[type="text"]:focus,input[type="number"]:focus{outline:none;box-shadow:inset 0 0 10px rgba(255,176,0,0.3),0 0 15px rgba(255,176,0,0.5);animation:pulse 1.5s infinite}@keyframes pulse{0%,100%{border-color:#ffb000}50%{border-color:#ffcc44}}.button-group{display:flex;gap:0.75rem;flex-wrap:wrap}button{padding:0.75rem 1.5rem;border:2px solid #ffb000;font-weight:500;cursor:pointer;font-size:1rem;font-family:'Share Tech Mono',monospace;transition:all 0.2s;display:flex;align-items:center;gap:0.5rem;text-transform:uppercase;letter-spacing:2px;position:relative;overflow:hidden}button::before{content:"";position:absolute;top:50%;left:50%;width:0;height:0;border-radius:50%;background:rgba(255,176,0,0.3);transform:translate(-50%,-50%);transition:width 0.6s,height 0.6s}button:hover::before{width:300px;height:300px}button>*{position:relative;z-index:1}.btn-primary{background:rgba(255,176,0,0.1);color:#ffb000;box-shadow:0 0 10px rgba(255,176,0,0.3)}.btn-primary:hover{background:rgba(255,176,0,0.2);box-shadow:0 0 20px rgba(255,176,0,0.6);text-shadow:0 0 10px rgba(255,176,0,0.8)}.btn-secondary{background:rgba(0,0,0,0.8);color:#ffb000;box-shadow:0 0 10px rgba(255,176,0,0.2)}.btn-secondary:hover{background:rgba(255,176,0,0.1);box-shadow:0 0 20px rgba(255,176,0,0.5)}.btn-success{background:rgba(255,176,0,0.2);color:#ffb000;width:100%;justify-content:center;padding:1rem 1.5rem;font-size:1.25rem;box-shadow:0 0 20px rgba(255,176,0,0.4);border:3px solid #ffb000}.btn-success:hover{background:rgba(255,176,0,0.3);box-shadow:0 0 30px rgba(255,176,0,0.7);text-shadow:0 0 15px rgba(255,176,0,1);transform:translateY(-2px)}.btn-download{background:rgba(255,176,0,0.15);color:#ffb000;padding:0.5rem 1rem;font-size:0.875rem}.btn-download:hover{background:rgba(255,176,0,0.25);box-shadow:0 0 15px rgba(255,176,0,0.6)}button:disabled{opacity:0.3;cursor:not-allowed}.library-item{background:rgba(0,0,0,0.6);border:1px solid #ffb000;padding:1rem;margin-bottom:0.75rem;display:flex;align-items:center;gap:1rem;box-shadow:inset 0 0 20px rgba(255,176,0,0.1);transition:all 0.3s}.library-item:hover{box-shadow:inset 0 0 20px rgba(255,176,0,0.2),0 0 15px rgba(255,176,0,0.4);border-color:#ffcc44}.library-item input[type="checkbox"]{width:1.5rem;height:1.5rem;cursor:pointer;accent-color:#ffb000;filter:brightness(1.2) contrast(1.3)}.library-info{flex:1}.library-name{font-weight:500;text-shadow:0 0 5px rgba(255,176,0,0.5);font-size:1.1rem}.library-id{color:#cc8800;font-size:0.8rem;letter-spacing:1px}.type-buttons{display:flex;gap:0.5rem}.type-btn{padding:0.5rem 1.25rem;font-size:0.875rem;background:rgba(0,0,0,0.8);color:#cc8800;border:1px solid #cc8800;transition:all 0.3s}.type-btn.active{background:rgba(255,176,0,0.2);color:#ffb000;border-color:#ffb000;box-shadow:0 0 15px rgba(255,176,0,0.5);text-shadow:0 0 10px rgba(255,176,0,0.8)}.type-btn:hover{border-color:#ffb000;color:#ffb000}.message{padding:1rem;margin-bottom:1.5rem;display:flex;align-items:center;gap:0.75rem;border:2px solid;font-family:'Share Tech Mono',monospace;text-transform:uppercase;letter-spacing:1px}.message.success{background:rgba(255,176,0,0.1);border-color:#ffb000;color:#ffb000;box-shadow:0 0 20px rgba(255,176,0,0.3)}.message.error{background:rgba(255,68,0,0.1);border-color:#ff4400;color:#ff4400;box-shadow:0 0 20px rgba(255,68,0,0.3)}.progress-bar{width:100%;height:1.5rem;background:#000;border:2px solid #ffb000;overflow:hidden;margin-top:0.5rem;box-shadow:inset 0 0 10px rgba(255,176,0,0.2);position:relative}.progress-bar::after{content:"";position:absolute;top:0;left:0;right:0;bottom:0;background:repeating-linear-gradient(90deg,transparent,transparent 10px,rgba(255,176,0,0.1) 10px,rgba(255,176,0,0.1) 20px);pointer-events:none}.progress-fill{height:100%;background:linear-gradient(90deg,#ffb000,#ffcc44,#ffb000);transition:width 0.3s;box-shadow:0 0 20px rgba(255,176,0,0.8);animation:progressGlow 2s infinite}@keyframes progressGlow{0%,100%{box-shadow:0 0 20px rgba(255,176,0,0.8)}50%{box-shadow:0 0 30px rgba(255,176,0,1)}}.progress-text{display:flex;justify-content:space-between;font-size:0.875rem;margin-bottom:0.5rem;text-transform:uppercase;letter-spacing:1px;text-shadow:0 0 5px rgba(255,176,0,0.5)}.report-item{background:rgba(0,0,0,0.6);border:1px solid #ffb000;padding:1rem;margin-bottom:0.75rem;display:flex;align-items:center;justify-content:space-between;box-shadow:inset 0 0 15px rgba(255,176,0,0.1);transition:all 0.3s}.report-item:hover{box-shadow:inset 0 0 20px rgba(255,176,0,0.2),0 0 15px rgba(255,176,0,0.4)}.report-info .name{font-weight:500;font-size:1.1rem;text-shadow:0 0 5px rgba(255,176,0,0.5)}.report-info .details{color:#cc8800;font-size:0.875rem;letter-spacing:1px}.hidden{display:none}.spinner{display:inline-block;width:1rem;height:1rem;border:2px solid rgba(255,176,0,0.3);border-top-color:#ffb000;border-radius:50%;animation:spin 0.6s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}</style></head><body><div class="container"><div class="header"><h1>PLEX UNWATCHED REPORTER</h1><p>[ v2.0 ]</p></div><div id="message" class="message hidden"></div><div class="card"><h2>[ CONFIGURATION ]</h2><div class="form-group"><label>Exclude Content Added Within (days)</label><input type="number" id="excludeDays" value="30" min="0"></div><div class="button-group"><button class="btn-primary" onclick="saveConfig()">Save Configuration</button><button class="btn-secondary" onclick="scanLibraries()" id="scanBtn"><span id="scanIcon">⟳</span><span id="scanText">Scan Libraries</span></button></div></div><div id="librariesCard" class="card hidden"><h2>[ SELECT LIBRARIES ]</h2><div class="info-box"><strong>TYPE SELECTION:</strong> Choose <strong>MOVIE</strong> for single video files (shows title, year, play count). Choose <strong>TV SHOW</strong> for series (shows by season with episode counts).</div><div id="librariesList"></div><button class="btn-success" onclick="generateReports()" id="generateBtn">Generate Reports</button></div><div id="progressCard" class="card hidden"><h2>[ PROCESSING ]</h2><div class="progress-text"><span id="progressLibrary"></span><span id="progressCount"></span></div><div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div></div><div id="reportsCard" class="card hidden"><h2>[ GENERATED REPORTS ]</h2><div id="reportsList"></div><button class="btn-secondary" onclick="clearReports()" id="clearBtn" style="margin-top:1rem;width:100%">Clear All Reports</button></div><div class="card"><h2>[ POWER MANAGEMENT ]</h2><div class="info-box"><strong>WARNING:</strong> Shutting down will stop the container. You will need to restart it from your Docker/Unraid interface to use it again.</div><button class="btn-secondary" onclick="shutdownContainer()" id="shutdownBtn" style="width:100%;background:rgba(255,68,0,0.2);border-color:#ff4400;color:#ff4400">SHUTDOWN APPLICATION AND STOP CONTAINER</button></div></div><script>let config={};let libraries=[];let selectedLibraries={};let libraryTypes={};let progressInterval=null;window.onload=async()=>{await loadConfig()};async function loadConfig(){try{const r=await fetch('/api/config');const d=await r.json();document.getElementById('excludeDays').value=d.excludeDays||30;selectedLibraries=d.selectedLibraries||{};libraryTypes=d.libraryTypes||{}}catch(e){console.error('Failed:',e)}}async function saveConfig(){config={excludeDays:parseInt(document.getElementById('excludeDays').value),selectedLibraries:selectedLibraries,libraryTypes:libraryTypes};try{await fetch('/api/config',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(config)});showMessage('success','Configuration saved!')}catch(e){showMessage('error','Failed to save')}}async function scanLibraries(){const btn=document.getElementById('scanBtn');const icon=document.getElementById('scanIcon');const text=document.getElementById('scanText');btn.disabled=true;icon.innerHTML='<span class="spinner"></span>';text.textContent='Scanning...';try{await saveConfig();const r=await fetch('/api/libraries');const d=await r.json();if(d.error){showMessage('error',d.error);return}libraries=d.libraries;libraries.forEach(lib=>{if(!(lib.key in selectedLibraries)){selectedLibraries[lib.key]=false;libraryTypes[lib.key]='movie'}});renderLibraries();document.getElementById('librariesCard').classList.remove('hidden');showMessage('success',`Found ${libraries.length} libraries`)}catch(e){showMessage('error','Failed to scan')}finally{btn.disabled=false;icon.textContent='⟳';text.textContent='Scan Libraries'}}function renderLibraries(){const list=document.getElementById('librariesList');list.innerHTML=libraries.map(lib=>`<div class="library-item"><input type="checkbox" id="lib_${lib.key}" ${selectedLibraries[lib.key]?'checked':''} onchange="toggleLibrary('${lib.key}')"><div class="library-info"><div class="library-name">${lib.title}</div><div class="library-id">Type: ${lib.type}</div></div><div class="type-buttons"><button class="type-btn ${libraryTypes[lib.key]==='movie'?'active':''}" onclick="setLibraryType('${lib.key}','movie')">Movie</button><button class="type-btn ${libraryTypes[lib.key]==='tv'?'active':''}" onclick="setLibraryType('${lib.key}','tv')">TV Show</button></div></div>`).join('')}function toggleLibrary(key){selectedLibraries[key]=!selectedLibraries[key]}function setLibraryType(key,type){libraryTypes[key]=type;renderLibraries()}async function pollProgress(){try{const r=await fetch('/api/progress');const data=await r.json();document.getElementById('progressLibrary').textContent=data.current_library?`Processing: ${data.current_library}`:'Initializing...';document.getElementById('progressCount').textContent=`${data.current} / ${data.total}`;const percent=data.total>0?(data.current/data.total)*100:0;document.getElementById('progressFill').style.width=`${percent}%`}catch(e){console.error('Progress poll failed:',e)}}async function generateReports(){const selectedCount=Object.values(selectedLibraries).filter(Boolean).length;if(selectedCount===0){showMessage('error','Select at least one library');return}await saveConfig();const btn=document.getElementById('generateBtn');btn.disabled=true;document.getElementById('progressCard').classList.remove('hidden');document.getElementById('reportsCard').classList.add('hidden');document.getElementById('progressLibrary').textContent='Initializing...';document.getElementById('progressCount').textContent='0 / 0';document.getElementById('progressFill').style.width='0%';const librariesOrder=libraries.map(lib=>lib.key);progressInterval=setInterval(pollProgress,500);try{const r=await fetch('/api/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({selectedLibraries:selectedLibraries,libraryTypes:libraryTypes,librariesOrder:librariesOrder})});const d=await r.json();if(progressInterval){clearInterval(progressInterval);progressInterval=null}if(d.error){showMessage('error',d.error);return}renderReports(d.reports);document.getElementById('progressCard').classList.add('hidden');document.getElementById('reportsCard').classList.remove('hidden');showMessage('success',`Generated ${d.reports.length} reports!`)}catch(e){if(progressInterval){clearInterval(progressInterval);progressInterval=null}showMessage('error','Generation failed')}finally{btn.disabled=false}}function renderReports(reports){const list=document.getElementById('reportsList');list.innerHTML=reports.map(report=>`<div class="report-item"><div class="report-info"><div class="name">${report.library}</div><div class="details">${report.filename} • ${report.itemCount} items</div></div><button class="btn-download" onclick="downloadReport('${report.filename}')">[ DOWNLOAD ]</button></div>`).join('')}function downloadReport(filename){window.location.href=`/api/download/${filename}`}function showMessage(type,text){const msg=document.getElementById('message');msg.className=`message ${type}`;msg.innerHTML=`<span>${type==='success'?'[OK]':'[ERROR]'}</span><span>${text}</span>`;msg.classList.remove('hidden');setTimeout(()=>{msg.classList.add('hidden')},5000)}async function clearReports(){if(!confirm('Delete all report files? This cannot be undone.')){return}const btn=document.getElementById('clearBtn');btn.disabled=true;btn.textContent='Clearing...';try{const r=await fetch('/api/clear-reports',{method:'POST'});const d=await r.json();if(d.error){showMessage('error',d.error)}else{showMessage('success',`Deleted ${d.deleted} report files`);document.getElementById('reportsCard').classList.add('hidden')}}catch(e){showMessage('error','Failed to clear reports')}finally{btn.disabled=false;btn.textContent='Clear All Reports'}}async function shutdownContainer(){if(!confirm('Really shutdown the container? You will need to restart it manually.')){return}const btn=document.getElementById('shutdownBtn');btn.disabled=true;btn.textContent='Shutting down...';try{await fetch('/api/shutdown',{method:'POST'});showMessage('success','Container shutting down...')}catch(e){showMessage('error','Shutdown failed')}}</script></body></html>
"""

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE,'r') as f:
            return json.load(f)
    return {'excludeDays':30,'selectedLibraries':{},'libraryTypes':{}}

def save_config(config):
    os.makedirs('/config',exist_ok=True)
    with open(CONFIG_FILE,'w') as f:
        json.dump(config,f,indent=2)

def get_plex_connection():
    """Connect to Plex server using PlexAPI - SAFE, no database access"""
    if not PLEX_URL or not PLEX_TOKEN:
        raise ValueError('PLEX_URL and PLEX_TOKEN environment variables are required')
    return PlexServer(PLEX_URL, PLEX_TOKEN)

def format_file_size(size_bytes):
    if size_bytes is None:
        return "Unknown"
    for unit in ['B','KB','MB','GB','TB']:
        if size_bytes<1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes/=1024.0
    return f"{size_bytes:.2f} PB"

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/config',methods=['GET'])
def get_config():
    return jsonify(load_config())

@app.route('/api/config',methods=['POST'])
def update_config():
    save_config(request.json)
    return jsonify({'success':True})

@app.route('/api/libraries',methods=['GET'])
def scan_libraries():
    """Scan Plex libraries using PlexAPI - SAFE"""
    try:
        plex = get_plex_connection()
        sections = plex.library.sections()
        libraries = [{'key': section.key, 'title': section.title, 'type': section.type} for section in sections]
        return jsonify({'libraries': libraries})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate',methods=['POST'])
def generate_reports():
    """Generate reports using PlexAPI - SAFE, no database access"""
    global progress_data
    
    data=request.json
    config=load_config()
    exclude_days=config.get('excludeDays',30)
    selected_libraries=data.get('selectedLibraries',{})
    library_types=data.get('libraryTypes',{})
    libraries_order=data.get('librariesOrder',[])  # Get order from frontend
    
    os.makedirs(REPORTS_DIR,exist_ok=True)
    results=[]
    
    # Initialize progress - get selected libraries in order
    selected_libs = [str(k) for k in libraries_order if selected_libraries.get(str(k))]
    progress_data = {
        'current': 0,
        'total': len(selected_libs),
        'current_library': '',
        'libraries_order': selected_libs
    }
    
    try:
        plex = get_plex_connection()
        cutoff_date = datetime.now() - timedelta(days=exclude_days)
        
        # Process in the order libraries appear in the UI
        for idx, lib_key in enumerate(selected_libs, start=1):
            lib_type=library_types.get(lib_key,'movie')
            section = plex.library.sectionByID(int(lib_key))
            
            # Update progress
            progress_data['current'] = idx
            progress_data['current_library'] = section.title
            
            timestamp=datetime.now().strftime("%Y-%m-%d")
            sanitized_name="".join(c for c in section.title if c.isalnum() or c in(' ','-','_')).rstrip()
            filename=f"{sanitized_name}_{timestamp}.csv"
            output_path=os.path.join(REPORTS_DIR,filename)
            
            if lib_type=='movie':
                item_count=generate_movie_report_plexapi(section, output_path, cutoff_date)
            else:
                item_count=generate_tv_report_plexapi(section, output_path, cutoff_date)
            
            results.append({'library':section.title,'filename':filename,'itemCount':item_count,'path':f'/api/download/{filename}'})
        
        return jsonify({'reports':results})
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/api/progress',methods=['GET'])
def get_progress():
    """Get current progress of report generation"""
    return jsonify(progress_data)

def generate_movie_report_plexapi(section, output_path, cutoff_date):
    """Generate movie report using PlexAPI"""
    with open(output_path,'w',newline='',encoding='utf-8') as csvfile:
        writer=csv.writer(csvfile)
        writer.writerow(['Title','Year','Date Added','Play Count','File Path','File Size'])
        
        row_count=0
        for movie in section.all():
            if movie.addedAt > cutoff_date:
                continue
            
            year = movie.year if hasattr(movie, 'year') else 'Unknown'
            date_added = movie.addedAt.strftime('%Y-%m-%d %H:%M:%S') if movie.addedAt else 'Unknown'
            
            # Get total play count across ALL users using history()
            play_count = len(movie.history())
            
            # Get file info
            file_path = 'Unknown'
            file_size = 0
            if movie.media:
                for media in movie.media:
                    if media.parts:
                        file_path = media.parts[0].file
                        file_size = media.parts[0].size or 0
                        break
            
            writer.writerow([movie.title, year, date_added, play_count, file_path, format_file_size(file_size)])
            row_count+=1
    
    return row_count

def generate_tv_report_plexapi(section, output_path, cutoff_date):
    """Generate TV show report using PlexAPI"""
    with open(output_path,'w',newline='',encoding='utf-8') as csvfile:
        writer=csv.writer(csvfile)
        writer.writerow(['Show Title','Season Number','Watched Status','Total Episodes','Episodes Watched','Date Added'])
        
        row_count=0
        for show in section.all():
            for season in show.seasons():
                if season.addedAt and season.addedAt > cutoff_date:
                    continue
                
                episodes = season.episodes()
                total_episodes = len(episodes)
                
                # Get watched count across ALL users using history()
                watched_episodes = sum(1 for ep in episodes if len(ep.history()) > 0)
                watched_status = 'Yes' if watched_episodes > 0 else 'No'
                date_added = season.addedAt.strftime('%Y-%m-%d %H:%M:%S') if season.addedAt else 'Unknown'
                
                writer.writerow([
                    show.title,
                    f"Season {season.seasonNumber}",
                    watched_status,
                    total_episodes,
                    watched_episodes,
                    date_added
                ])
                row_count+=1
    
    return row_count

@app.route('/api/download/<filename>',methods=['GET'])
def download_report(filename):
    file_path=os.path.join(REPORTS_DIR,filename)
    if os.path.exists(file_path):
        return send_file(file_path,as_attachment=True)
    return jsonify({'error':'File not found'}),404

@app.route('/api/clear-reports',methods=['POST'])
def clear_reports():
    try:
        deleted=0
        for filename in os.listdir(REPORTS_DIR):
            if filename.endswith('.csv'):
                os.remove(os.path.join(REPORTS_DIR,filename))
                deleted+=1
        return jsonify({'deleted':deleted})
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/api/shutdown',methods=['POST'])
def shutdown_container():
    """Gracefully shutdown the Flask app and container"""
    import signal
    os.kill(os.getpid(), signal.SIGTERM)
    return jsonify({'status':'shutting down'})

@app.route('/health',methods=['GET'])
def health():
    return jsonify({'status':'healthy'})

if __name__=='__main__':
    os.makedirs('/config',exist_ok=True)
    os.makedirs(REPORTS_DIR,exist_ok=True)
    app.run(host='0.0.0.0',port=4080,debug=False)
