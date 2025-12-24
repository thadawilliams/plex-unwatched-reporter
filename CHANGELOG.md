# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-12-24

### 🎉 Major Features

#### Accurate All-User Play Counts
- Play counts now reflect activity across **ALL Plex users**, not just the token owner
- Uses Plex's history API instead of viewCount for comprehensive reporting
- Finally see the true popularity of your content!

#### Real-Time Progress Tracking
- Detailed item-level progress during report generation
- Shows "Processing: Library Name - Item 150/500"
- Track overall progress across multiple libraries
- No more wondering if it's still working on large libraries

#### Intelligent CSV Sorting
- **Movies**: Automatically sorted by play count (unwatched first), then by date added
- **TV Shows**: Sorted by watched status (unwatched first), then show title, then season number
- No manual sorting needed in Excel/Sheets!

#### Auto Library Type Detection
- Automatically selects Movie or TV Show based on Plex's library type
- Fewer clicks to get started
- Still manually adjustable if needed

#### Working Shutdown Button
- Properly stops the container when you're done
- No more manually stopping from Docker/Unraid interface
- Requires Docker socket mount (see README)

### 🐛 Bug Fixes

- Fixed numeric-only titles (like "1959", "1899") being right-aligned in CSVs
- Fixed progress bar starting full instead of empty
- Fixed libraries processing in reverse order
- Fixed shutdown button not actually stopping the container

### 🔧 Technical Changes

- **BREAKING**: Switched from database access to Plex API
  - Safer and officially supported by Plex
  - More accurate cross-user data
  - Slower but more thorough
- Removed database volume mount requirement
- Added Docker CLI to container for shutdown functionality
- Updated to Python 3.11-slim base image
- Added Docker socket support for proper container shutdown

### 📚 Documentation

- Completely updated README with all new features
- Added performance notes explaining processing speed
- Added troubleshooting for common issues
- Updated Docker Compose examples with Docker socket mount
- Added "Key Features Explained" section
- Added Buy Me a Coffee support

### ⚠️ Migration from v1.x

If upgrading from v1.x:

1. **Remove** the Plex database volume mount from your docker-compose.yml
2. **Add** the Docker socket volume: `/var/run/docker.sock:/var/run/docker.sock`
3. **Add** required environment variables:
   - `PLEX_URL=http://your-plex-ip:32400`
   - `PLEX_TOKEN=your-plex-token-here`
4. **Update** your configuration - library scanning now uses Plex API

See the [README](README.md) for complete installation instructions.

### 🙏 Acknowledgments

Special thanks to everyone who tested and provided feedback during development!

---

## [1.0.0] - 2024-12-23

### Initial Release

- Movie library reporting with play counts
- TV show library reporting with season breakdowns
- Retro terminal-style web interface
- Persistent configuration
- CSV export functionality
- Direct Plex database access
- Report management (clear reports)
- Configurable exclusion period

---

[2.0.0]: https://github.com/thadawilliams/plex-unwatched-reporter/releases/tag/v2.0.0
[1.0.0]: https://github.com/thadawilliams/plex-unwatched-reporter/releases/tag/v1.0.0
