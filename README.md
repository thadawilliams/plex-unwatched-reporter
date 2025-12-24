# Plex Unwatched Reporter

<p align="center">
  <em>A retro terminal-style web interface for generating CSV reports of unwatched content from your Plex Media Server.</em>
</p>

<p align="center">
  <strong>v2.0</strong> - Now with real-time progress tracking, accurate all-user play counts, and intelligent CSV sorting!
</p>

## Features

- 🎬 **Movie Libraries**: Detailed reports with title, year, play count (across all users), file path, and size
- 📺 **TV Show Libraries**: Season-by-season reporting with episode watch statistics
- 🖥️ **Retro Terminal UI**: Amber CRT-inspired interface with scanlines and glow effects
- 💾 **Persistent Configuration**: Library selections and settings saved between sessions
- ⏱️ **Smart Filtering**: Exclude recently added content (configurable days)
- 📊 **Sorted CSV Reports**: Movies sorted by play count & date; TV shows sorted by watched status
- 🔢 **Accurate Play Counts**: Shows total plays across ALL Plex users, not just the token owner
- 📈 **Real-Time Progress**: Detailed item-level progress tracking ("Processing: Movies - Item 150/500")
- 🎯 **Auto Type Detection**: Automatically selects Movie/TV Show based on Plex library type
- 🗑️ **Report Management**: Clear old reports with one click
- 🔌 **Shutdown Button**: Stop the container when you're done

## Screenshots

![Main Interface](screenshots/main-interface.png)

## Prerequisites

Before installing, you need to obtain your **Plex Token**:

### How to Get Your Plex Token

1. **Log into Plex Web** at https://app.plex.tv
2. **Play any media item** in your library
3. Click the **three dots (...)** → **"Get Info"**
4. Click **"View XML"** at the bottom
5. Look in the URL bar - your token is the part after `X-Plex-Token=`
   - Example URL: `https://app.plex.tv/.../...?X-Plex-Token=ABC123XYZ789`
   - Your token is: `ABC123XYZ789`
6. **Copy the token** - you'll need it during installation

**Alternative method:**
- Follow the official guide: https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/

⚠️ **Security Note:** Keep your Plex token private - it grants full access to your Plex server.

---

## Quick Start

### Docker Compose (Recommended)

1. **Create a project directory:**
```bash
mkdir -p ~/plex-unwatched-reporter
cd ~/plex-unwatched-reporter
```

2. Create a `docker-compose.yml` file:

```yaml
services:
  plex-reporter:
    image: tawilliams/plex-unwatched-reporter:latest
    container_name: plex-unwatched-reporter
    ports:
      - "4080:4080"
    volumes:
      - ./config:/config
      - ./reports:/reports
      - /var/run/docker.sock:/var/run/docker.sock  # Required for shutdown button
    environment:
      - TZ=America/New_York
      - PLEX_URL=http://your-plex-ip:32400
      - PLEX_TOKEN=your-plex-token-here
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

3. Update `PLEX_URL` to your Plex server address...
4. Replace `PLEX_TOKEN` with your actual Plex token...
5. Run: `docker-compose up -d`
6. Access at: `http://your-server-ip:4080`

### Docker Run

```bash
docker run -d \
  --name plex-unwatched-reporter \
  -p 4080:4080 \
  -v ./config:/config \
  -v ./reports:/reports \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e TZ=America/New_York \
  -e PLEX_URL=http://your-plex-ip:32400 \
  -e PLEX_TOKEN=your-plex-token-here \
  tawilliams/plex-unwatched-reporter:latest
```

**Note:** The `/var/run/docker.sock` volume is required for the shutdown button to work properly.

### Unraid

1. Open **Community Applications**
2. Search for "Plex Unwatched Reporter"
3. Click **Install**
4. Configure:
   - **Config**: `/mnt/user/appdata/plex-unwatched-reporter`
   - **Reports**: `/mnt/user/Downloads` (or your preferred location)
   - **Plex URL**: `http://your-plex-ip:32400` (your Plex server address)
   - **Plex Token**: Your Plex authentication token
   - **Timezone**: Your timezone (e.g., `America/New_York`)
5. Click **Apply**

---

## Usage

### 1. Configure Settings

- **Exclusion Period**: Ignore content added within X days (default: 30)
- Click **Save Configuration**

### 2. Scan Libraries

Click **Scan Libraries** to detect all available Plex libraries from your Plex server using the official Plex API. Libraries are automatically categorized as Movie or TV Show based on their type.

### 3. Select Libraries

- ✅ Check boxes next to libraries you want to report on
- Library type (Movie/TV Show) is automatically selected based on Plex's classification
- You can manually change the type if needed

### 4. Generate Reports

Click **Generate Reports** to create CSV files. 

**Real-time progress tracking shows:**
- Current library being processed
- Item-level progress (e.g., "Processing: Movies - Item 150/500")
- Overall library progress (e.g., "Library 2 / 5")

Download links appear when complete.

### 5. Manage Reports

Use **Clear All Reports** button to delete all generated CSV files when you're done with them.

### 6. Shutdown

Use **Shutdown Application and Stop Container** button when finished. This is a run-on-demand tool, not meant to run 24/7.

---

## Volume Mounts

| Container Path | Purpose | Example Host Path | Required |
|---------------|---------|-------------------|----------|
| `/config` | Persistent configuration | `./config` or `/mnt/user/appdata/plex-unwatched-reporter` | Yes |
| `/reports` | Generated CSV files | `./reports` or `/mnt/user/Downloads` | Yes |
| `/var/run/docker.sock` | Docker socket for shutdown | `/var/run/docker.sock` | For shutdown button |

## Report Formats

### Movie Reports Include:
- Title (left-aligned, even for numeric titles like "1959")
- Year
- Date Added to Plex
- **Play Count** (total across ALL users)
- File Path
- File Size

**Sorting:** Reports are sorted by play count (low to high), then by date added (oldest first). This means unwatched content appears first.

### TV Show Reports Include:
- Show Title (left-aligned, even for numeric titles like "1899")
- Season Number
- Watched Status (Yes/No - based on any episode watched by any user)
- Total Episodes in Season
- Episodes Watched Count (across ALL users)
- Date Added to Plex

**Sorting:** Reports are sorted by watched status (No first), then show title (A-Z), then season number. This means unwatched shows appear first.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TZ` | `UTC` | Timezone for date/time display |
| `PLEX_URL` | *Required* | Plex server URL (e.g., `http://192.168.1.100:32400`) |
| `PLEX_TOKEN` | *Required* | Plex authentication token |

---

## Key Features Explained

### Accurate All-User Play Counts

Unlike some tools that only show the token owner's watch history, this reporter uses Plex's history API to count plays from **ALL users** on your server. If you've watched a movie once but your family has watched it 27 more times, you'll see the accurate total of 28 plays.

### Real-Time Progress Tracking

When generating reports, you'll see detailed progress including:
- Which library is currently being processed
- How many items have been processed in that library
- Which library number you're on out of the total

This is especially helpful for large libraries where processing can take several minutes.

### Intelligent CSV Sorting

Reports are automatically sorted to make unwatched content easy to find:
- **Movies**: Sorted by play count (0 plays first), then by date added (oldest first)
- **TV Shows**: Sorted by watched status (unwatched first), then alphabetically

This saves you from having to manually sort in Excel/Sheets.

---

## Performance Notes

**Processing Speed:** This tool queries Plex's API for accurate all-user play counts, which is more thorough but slower than database access. Large libraries may take several minutes to process. The real-time progress tracker helps you monitor the process.

**Recommended Use:** This is a run-on-demand tool. Generate your reports, download them, and shut down the container when finished.

---

## Troubleshooting

### Cannot Connect to Plex

**Error**: "Failed to connect" or "Connection refused"

**Solution**: 
- Verify `PLEX_URL` is correct and includes the port (usually `32400`)
- If Plex is on the same server, try `http://localhost:32400`
- If on a different server, use the server's IP address
- Ensure Plex is running and accessible from the Docker container

### Invalid Plex Token

**Error**: "Unauthorized" or "Invalid token"

**Solution**:
- Double-check your Plex token is correct
- Generate a new token following the Prerequisites section
- Ensure there are no extra spaces when copying the token

### Shutdown Button Not Working

**Error**: Button shows "shutting down" but container keeps running

**Solution**:
- Ensure you've mounted the Docker socket: `-v /var/run/docker.sock:/var/run/docker.sock`
- Check that Docker CLI is installed in the container (should be automatic with latest image)
- Verify the container name is exactly `plex-unwatched-reporter`

### Port Already in Use

**Error**: Port 4080 conflict

**Solution**: Change the host port (first number) in docker-compose.yml:
```yaml
ports:
  - "8090:4080"  # Changed to 8090
```
Then access via `http://your-ip:8090`

### Reports Not Generating

**Symptoms**: No errors but reports don't appear

**Solution**:
- Check Docker logs: `docker logs plex-unwatched-reporter`
- Verify at least one library is selected
- Ensure reports directory has write permissions
- Verify your Plex token has access to the selected libraries

### No Libraries Showing

**Symptoms**: Scan Libraries returns empty or shows error

**Solution**:
- Verify `PLEX_URL` and `PLEX_TOKEN` are set correctly
- Check Docker logs for connection errors
- Ensure your Plex token has access to your Plex libraries
- Try restarting the container: `docker restart plex-unwatched-reporter`

### Slow Report Generation

**Symptoms**: Report generation takes a long time

**Explanation**: This is normal! The tool queries Plex's API for each item to get accurate all-user play counts. Large libraries with thousands of items will take several minutes. Watch the real-time progress tracker to monitor the process.

**Tips:**
- Let it run - the progress tracker shows it's working
- Consider excluding recently added content to reduce the number of items processed
- This is why it's a run-on-demand tool rather than a continuously running service

---

## Building from Source

```bash
git clone https://github.com/thadawilliams/plex-unwatched-reporter.git
cd plex-unwatched-reporter
docker build -t plex-unwatched-reporter .
docker-compose up -d
```

---

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

This means:
- ✅ You can use, modify, and distribute this software
- ✅ You can use it commercially
- ⚠️ You must disclose source code of any modifications
- ⚠️ You must license derivative works under AGPL-3.0
- ⚠️ Network use counts as distribution (must share modifications)

---

## Support

- 🐛 [Report Issues](https://github.com/thadawilliams/plex-unwatched-reporter/issues)
- 💡 [Request Features](https://github.com/thadawilliams/plex-unwatched-reporter/issues/new)
- 📖 [Documentation](https://github.com/thadawilliams/plex-unwatched-reporter/wiki)

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-yellow?style=for-the-badge&logo=buy-me-a-coffee)](https://www.buymeacoffee.com/thadawilliams)
---

## Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/), Python, and [PlexAPI](https://github.com/pkkid/python-plexapi)
- Uses the official Plex API for safe, non-invasive access to your Plex server
- Inspired by retro computing and CRT terminal aesthetics
- Special thanks to the Plex community

---

**Made with ❤️ for all beings in the universe.**
