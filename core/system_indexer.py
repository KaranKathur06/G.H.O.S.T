"""
24/7 System Indexing & Search Engine for G.H.O.S.T.

This module maintains a live index of all files, folders, applications,
and system resources. Enables instant search and discovery of anything
on the PC without hardcoded paths or limitations.
"""

import os
import sys
import time
import threading
import logging
import sqlite3
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import psutil

# Windows registry support
try:
    import winreg
    WINREG_AVAILABLE = True
except ImportError:
    WINREG_AVAILABLE = False
    winreg = None
from concurrent.futures import ThreadPoolExecutor
import queue

@dataclass
class IndexedItem:
    """Represents any indexed item on the system."""
    id: str                    # Unique identifier
    name: str                  # Display name
    path: str                  # Full path
    type: str                  # file, folder, application, etc.
    size: int = 0             # Size in bytes
    modified: datetime = None  # Last modified
    accessed: datetime = None  # Last accessed
    created: datetime = None   # Created date
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional info
    search_terms: List[str] = field(default_factory=list)   # Search keywords

@dataclass
class SearchResult:
    """Search result with relevance scoring."""
    item: IndexedItem
    relevance_score: float
    match_type: str           # exact, partial, fuzzy, metadata
    matched_terms: List[str]  # Which terms matched

class SystemIndexer:
    """
    24/7 System Indexing & Search Engine.
    
    Maintains a live, searchable index of everything on the PC:
    - All files and folders
    - Installed applications
    - System resources
    - Media content
    - Recent items
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the system indexer."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Database for persistent storage
        self.db_path = self.config.get('db_path', 'data/system_index.db')
        self.db_connection = None
        
        # Indexing configuration
        self.index_paths = self.config.get('index_paths', self._get_default_paths())
        self.excluded_paths = self.config.get('excluded_paths', self._get_excluded_paths())
        self.file_extensions = self.config.get('file_extensions', self._get_supported_extensions())
        
        # Performance settings
        self.max_workers = self.config.get('max_workers', 4)
        self.batch_size = self.config.get('batch_size', 1000)
        self.update_interval = self.config.get('update_interval', 300)  # 5 minutes
        
        # Runtime state
        self.is_indexing = False
        self.is_running = False
        self.index_thread = None
        self.update_queue = queue.Queue()
        
        # In-memory cache for fast searches
        self.item_cache = {}
        self.search_cache = {}
        self.cache_expiry = timedelta(minutes=30)
        
        # Initialize database
        self._init_database()
        
        self.logger.info("System Indexer initialized")
    
    def _get_default_paths(self) -> List[str]:
        """Get default paths to index."""
        paths = []
        
        # User directories
        user_home = Path.home()
        paths.extend([
            str(user_home / "Desktop"),
            str(user_home / "Documents"),
            str(user_home / "Downloads"),
            str(user_home / "Pictures"),
            str(user_home / "Music"),
            str(user_home / "Videos")
        ])
        
        # System directories
        if sys.platform == "win32":
            paths.extend([
                "C:\\Program Files",
                "C:\\Program Files (x86)",
                str(user_home / "AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs")
            ])
        
        return [p for p in paths if os.path.exists(p)]
    
    def _get_excluded_paths(self) -> List[str]:
        """Get paths to exclude from indexing."""
        excluded = [
            "System Volume Information",
            "$Recycle.Bin",
            "Windows\\System32",
            "Windows\\SysWOW64",
            "AppData\\Local\\Temp",
            "node_modules",
            ".git",
            "__pycache__"
        ]
        
        return excluded
    
    def _get_supported_extensions(self) -> Set[str]:
        """Get supported file extensions."""
        return {
            # Documents
            '.txt', '.doc', '.docx', '.pdf', '.rtf', '.odt',
            # Spreadsheets
            '.xls', '.xlsx', '.csv', '.ods',
            # Presentations
            '.ppt', '.pptx', '.odp',
            # Images
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg',
            # Audio
            '.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a',
            # Video
            '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv',
            # Code
            '.py', '.js', '.html', '.css', '.cpp', '.java', '.cs',
            # Archives
            '.zip', '.rar', '.7z', '.tar', '.gz',
            # Executables
            '.exe', '.msi', '.app', '.deb', '.rpm'
        }
    
    def _init_database(self):
        """Initialize SQLite database for persistent storage."""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            self.db_connection = sqlite3.connect(self.db_path, check_same_thread=False)
            
            # Create tables
            cursor = self.db_connection.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS indexed_items (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    path TEXT UNIQUE NOT NULL,
                    type TEXT NOT NULL,
                    size INTEGER DEFAULT 0,
                    modified TIMESTAMP,
                    accessed TIMESTAMP,
                    created TIMESTAMP,
                    metadata TEXT,
                    search_terms TEXT,
                    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_name ON indexed_items(name)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_type ON indexed_items(type)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_path ON indexed_items(path)
            ''')
            
            cursor.execute('''
                CREATE VIRTUAL TABLE IF NOT EXISTS search_index 
                USING fts5(name, path, search_terms, content='indexed_items', content_rowid='rowid')
            ''')
            
            self.db_connection.commit()
            self.logger.info("Database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def start_indexing(self):
        """Start 24/7 indexing process."""
        if self.is_running:
            self.logger.warning("Indexing already running")
            return
        
        self.is_running = True
        self.index_thread = threading.Thread(target=self._indexing_loop, daemon=True)
        self.index_thread.start()
        
        self.logger.info("24/7 indexing started")
    
    def stop_indexing(self):
        """Stop indexing process."""
        self.is_running = False
        if self.index_thread:
            self.index_thread.join(timeout=5)
        
        self.logger.info("Indexing stopped")
    
    def _indexing_loop(self):
        """Main indexing loop that runs 24/7."""
        try:
            # Initial full index
            self.logger.info("Starting initial system indexing...")
            self._full_index()
            
            # Continuous monitoring
            while self.is_running:
                try:
                    # Process update queue
                    self._process_update_queue()
                    
                    # Periodic re-indexing
                    if time.time() % self.update_interval < 1:
                        self._incremental_index()
                    
                    # Update applications list
                    if time.time() % (self.update_interval * 4) < 1:  # Every 20 minutes
                        self._index_applications()
                    
                    time.sleep(1)
                    
                except Exception as e:
                    self.logger.error(f"Error in indexing loop: {e}")
                    time.sleep(5)
        
        except Exception as e:
            self.logger.error(f"Fatal error in indexing loop: {e}")
        
        finally:
            self.is_running = False
    
    def _full_index(self):
        """Perform full system indexing."""
        self.is_indexing = True
        start_time = time.time()
        
        try:
            # Clear existing index
            cursor = self.db_connection.cursor()
            cursor.execute("DELETE FROM indexed_items")
            cursor.execute("DELETE FROM search_index")
            self.db_connection.commit()
            
            # Index all paths
            total_items = 0
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = []
                
                for path in self.index_paths:
                    if os.path.exists(path):
                        future = executor.submit(self._index_directory, path)
                        futures.append(future)
                
                for future in futures:
                    try:
                        items_count = future.result()
                        total_items += items_count
                    except Exception as e:
                        self.logger.error(f"Error indexing directory: {e}")
            
            # Index applications
            app_count = self._index_applications()
            total_items += app_count
            
            # Update search index
            self._rebuild_search_index()
            
            elapsed = time.time() - start_time
            self.logger.info(f"Full indexing completed: {total_items} items in {elapsed:.2f}s")
            
        except Exception as e:
            self.logger.error(f"Error in full indexing: {e}")
        
        finally:
            self.is_indexing = False
    
    def _index_directory(self, directory_path: str) -> int:
        """Index a specific directory."""
        items_indexed = 0
        batch_items = []
        
        try:
            for root, dirs, files in os.walk(directory_path):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if not self._is_excluded(os.path.join(root, d))]
                
                # Index directory itself
                if not self._is_excluded(root):
                    dir_item = self._create_indexed_item(root, "folder")
                    if dir_item:
                        batch_items.append(dir_item)
                
                # Index files
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    if not self._is_excluded(file_path):
                        file_item = self._create_indexed_item(file_path, "file")
                        if file_item:
                            batch_items.append(file_item)
                    
                    # Process batch
                    if len(batch_items) >= self.batch_size:
                        self._save_batch(batch_items)
                        items_indexed += len(batch_items)
                        batch_items = []
            
            # Save remaining items
            if batch_items:
                self._save_batch(batch_items)
                items_indexed += len(batch_items)
        
        except Exception as e:
            self.logger.error(f"Error indexing directory {directory_path}: {e}")
        
        return items_indexed
    
    def _create_indexed_item(self, path: str, item_type: str) -> Optional[IndexedItem]:
        """Create an indexed item from a file/folder path."""
        try:
            path_obj = Path(path)
            
            if not path_obj.exists():
                return None
            
            stat = path_obj.stat()
            
            # Generate unique ID
            item_id = hashlib.md5(path.encode()).hexdigest()
            
            # Extract metadata
            metadata = {}
            search_terms = []
            
            if item_type == "file":
                metadata['extension'] = path_obj.suffix.lower()
                metadata['is_executable'] = path_obj.suffix.lower() in {'.exe', '.msi', '.app'}
                
                # Add extension to search terms
                if metadata['extension']:
                    search_terms.append(metadata['extension'][1:])  # Remove dot
            
            # Add name parts to search terms
            name_parts = path_obj.stem.replace('_', ' ').replace('-', ' ').split()
            search_terms.extend(name_parts)
            
            return IndexedItem(
                id=item_id,
                name=path_obj.name,
                path=str(path_obj),
                type=item_type,
                size=stat.st_size if item_type == "file" else 0,
                modified=datetime.fromtimestamp(stat.st_mtime),
                accessed=datetime.fromtimestamp(stat.st_atime),
                created=datetime.fromtimestamp(stat.st_ctime),
                metadata=metadata,
                search_terms=search_terms
            )
            
        except Exception as e:
            self.logger.debug(f"Error creating indexed item for {path}: {e}")
            return None
    
    def _index_applications(self) -> int:
        """Index installed applications."""
        apps_indexed = 0
        
        try:
            if sys.platform == "win32":
                apps_indexed = self._index_windows_applications()
            # Add support for other platforms as needed
            
        except Exception as e:
            self.logger.error(f"Error indexing applications: {e}")
        
        return apps_indexed
    
    def _index_windows_applications(self) -> int:
        """Index Windows applications from registry and start menu."""
        apps = []
        
        try:
            if WINREG_AVAILABLE:
                # Registry locations for installed programs
                registry_paths = [
                    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall"),
                    (winreg.HKEY_CURRENT_USER, r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall"),
                    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall")
                ]
                
                for hkey, subkey_path in registry_paths:
                    try:
                        with winreg.OpenKey(hkey, subkey_path) as key:
                            for i in range(winreg.QueryInfoKey(key)[0]):
                                try:
                                    subkey_name = winreg.EnumKey(key, i)
                                    with winreg.OpenKey(key, subkey_name) as subkey:
                                        app_info = self._extract_app_info(subkey)
                                        if app_info:
                                            apps.append(app_info)
                                except Exception:
                                    continue
                    except Exception:
                        continue
            
            # Save applications to database
            self._save_batch(apps)
            
        except Exception as e:
            self.logger.error(f"Error indexing Windows applications: {e}")
        
        return len(apps)
    
    def _extract_app_info(self, registry_key) -> Optional[IndexedItem]:
        """Extract application info from registry key."""
        try:
            display_name = None
            install_location = None
            
            try:
                display_name = winreg.QueryValueEx(registry_key, "DisplayName")[0]
            except FileNotFoundError:
                return None
            
            try:
                install_location = winreg.QueryValueEx(registry_key, "InstallLocation")[0]
            except FileNotFoundError:
                pass
            
            if not display_name:
                return None
            
            # Generate unique ID
            item_id = hashlib.md5(f"app_{display_name}".encode()).hexdigest()
            
            # Create search terms
            search_terms = display_name.replace('_', ' ').replace('-', ' ').split()
            
            return IndexedItem(
                id=item_id,
                name=display_name,
                path=install_location or "",
                type="application",
                metadata={"source": "registry"},
                search_terms=search_terms
            )
            
        except Exception as e:
            self.logger.debug(f"Error extracting app info: {e}")
            return None
    
    def _save_batch(self, items: List[IndexedItem]):
        """Save a batch of items to database."""
        try:
            cursor = self.db_connection.cursor()
            
            for item in items:
                cursor.execute('''
                    INSERT OR REPLACE INTO indexed_items 
                    (id, name, path, type, size, modified, accessed, created, metadata, search_terms)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item.id,
                    item.name,
                    item.path,
                    item.type,
                    item.size,
                    item.modified,
                    item.accessed,
                    item.created,
                    json.dumps(item.metadata),
                    ' '.join(item.search_terms)
                ))
            
            self.db_connection.commit()
            
        except Exception as e:
            self.logger.error(f"Error saving batch to database: {e}")
    
    def _rebuild_search_index(self):
        """Rebuild the full-text search index."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("DELETE FROM search_index")
            cursor.execute('''
                INSERT INTO search_index(name, path, search_terms)
                SELECT name, path, search_terms FROM indexed_items
            ''')
            self.db_connection.commit()
            
        except Exception as e:
            self.logger.error(f"Error rebuilding search index: {e}")
    
    def _is_excluded(self, path: str) -> bool:
        """Check if path should be excluded from indexing."""
        path_lower = path.lower()
        
        for excluded in self.excluded_paths:
            if excluded.lower() in path_lower:
                return True
        
        return False
    
    def _process_update_queue(self):
        """Process pending updates from the queue."""
        try:
            while not self.update_queue.empty():
                update_item = self.update_queue.get_nowait()
                # Process update (re-index specific path)
                self._update_item(update_item)
        except queue.Empty:
            pass
    
    def _incremental_index(self):
        """Perform incremental indexing of recently changed items."""
        # This would monitor file system changes and update only modified items
        # For now, we'll skip this to keep the implementation focused
        pass
    
    def _update_item(self, path: str):
        """Update a specific item in the index."""
        try:
            if os.path.exists(path):
                item_type = "folder" if os.path.isdir(path) else "file"
                item = self._create_indexed_item(path, item_type)
                if item:
                    self._save_batch([item])
            else:
                # Remove from index if file no longer exists
                cursor = self.db_connection.cursor()
                cursor.execute("DELETE FROM indexed_items WHERE path = ?", (path,))
                self.db_connection.commit()
                
        except Exception as e:
            self.logger.error(f"Error updating item {path}: {e}")
    
    def search(self, query: str, item_type: str = None, limit: int = 20) -> List[SearchResult]:
        """
        Search for items in the index.
        
        Args:
            query: Search query
            item_type: Filter by type (file, folder, application)
            limit: Maximum results to return
            
        Returns:
            List of SearchResult objects sorted by relevance
        """
        try:
            # Check cache first
            cache_key = f"{query}_{item_type}_{limit}"
            if cache_key in self.search_cache:
                cached_result, timestamp = self.search_cache[cache_key]
                if datetime.now() - timestamp < self.cache_expiry:
                    return cached_result
            
            results = []
            cursor = self.db_connection.cursor()
            
            # Prepare query
            search_query = query.lower().strip()
            
            # Build SQL query
            sql_conditions = []
            params = []
            
            if item_type:
                sql_conditions.append("type = ?")
                params.append(item_type)
            
            # Full-text search
            fts_query = f'''
                SELECT indexed_items.*, 
                       bm25(search_index) as rank
                FROM search_index 
                JOIN indexed_items ON indexed_items.rowid = search_index.rowid
                WHERE search_index MATCH ?
            '''
            
            if sql_conditions:
                fts_query += f" AND {' AND '.join(sql_conditions)}"
            
            fts_query += " ORDER BY rank LIMIT ?"
            
            params.insert(0, search_query)
            params.append(limit)
            
            cursor.execute(fts_query, params)
            rows = cursor.fetchall()
            
            # Convert to SearchResult objects
            for row in rows:
                item = IndexedItem(
                    id=row[0],
                    name=row[1],
                    path=row[2],
                    type=row[3],
                    size=row[4],
                    modified=datetime.fromisoformat(row[5]) if row[5] else None,
                    accessed=datetime.fromisoformat(row[6]) if row[6] else None,
                    created=datetime.fromisoformat(row[7]) if row[7] else None,
                    metadata=json.loads(row[8]) if row[8] else {},
                    search_terms=row[9].split() if row[9] else []
                )
                
                # Calculate relevance score
                relevance_score = self._calculate_relevance(query, item)
                
                # Determine match type
                match_type = self._determine_match_type(query, item)
                
                # Find matched terms
                matched_terms = self._find_matched_terms(query, item)
                
                result = SearchResult(
                    item=item,
                    relevance_score=relevance_score,
                    match_type=match_type,
                    matched_terms=matched_terms
                )
                
                results.append(result)
            
            # Sort by relevance score
            results.sort(key=lambda x: x.relevance_score, reverse=True)
            
            # Cache results
            self.search_cache[cache_key] = (results, datetime.now())
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching for '{query}': {e}")
            return []
    
    def _calculate_relevance(self, query: str, item: IndexedItem) -> float:
        """Calculate relevance score for search result."""
        score = 0.0
        query_lower = query.lower()
        name_lower = item.name.lower()
        
        # Exact name match
        if query_lower == name_lower:
            score += 100.0
        
        # Name starts with query
        elif name_lower.startswith(query_lower):
            score += 80.0
        
        # Name contains query
        elif query_lower in name_lower:
            score += 60.0
        
        # Search terms match
        for term in item.search_terms:
            if query_lower in term.lower():
                score += 40.0
        
        # Path contains query
        if query_lower in item.path.lower():
            score += 20.0
        
        # Boost for certain types
        if item.type == "application":
            score += 10.0
        
        return score
    
    def _determine_match_type(self, query: str, item: IndexedItem) -> str:
        """Determine how the query matched the item."""
        query_lower = query.lower()
        name_lower = item.name.lower()
        
        if query_lower == name_lower:
            return "exact"
        elif name_lower.startswith(query_lower):
            return "prefix"
        elif query_lower in name_lower:
            return "partial"
        else:
            return "fuzzy"
    
    def _find_matched_terms(self, query: str, item: IndexedItem) -> List[str]:
        """Find which terms matched in the search."""
        matched = []
        query_lower = query.lower()
        
        if query_lower in item.name.lower():
            matched.append("name")
        
        for term in item.search_terms:
            if query_lower in term.lower():
                matched.append(term)
        
        if query_lower in item.path.lower():
            matched.append("path")
        
        return matched
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get indexing statistics."""
        try:
            cursor = self.db_connection.cursor()
            
            # Total items
            cursor.execute("SELECT COUNT(*) FROM indexed_items")
            total_items = cursor.fetchone()[0]
            
            # Items by type
            cursor.execute("SELECT type, COUNT(*) FROM indexed_items GROUP BY type")
            by_type = dict(cursor.fetchall())
            
            # Database size
            db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            
            return {
                'total_items': total_items,
                'by_type': by_type,
                'database_size': db_size,
                'is_indexing': self.is_indexing,
                'is_running': self.is_running,
                'cache_size': len(self.search_cache)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {}
    
    def cleanup(self):
        """Clean up resources."""
        self.stop_indexing()
        
        if self.db_connection:
            self.db_connection.close()
        
        self.logger.info("System indexer cleaned up")
