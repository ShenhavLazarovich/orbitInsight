import sqlite3
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import threading
import queue

class OfflineManager:
    def __init__(self):
        self.cache_dir = "offline_cache"
        self.db_path = os.path.join(self.cache_dir, "offline_data.db")
        os.makedirs(self.cache_dir, exist_ok=True)
        self._init_db()
        self.sync_queue = queue.Queue()
        self.sync_thread = None
        
    def _init_db(self):
        """Initialize SQLite database for offline storage"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Create tables for different data types
        c.execute('''CREATE TABLE IF NOT EXISTS satellite_data
                    (id TEXT PRIMARY KEY, data TEXT, timestamp TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS trajectory_data
                    (satellite_id TEXT, data TEXT, start_date TEXT, 
                     end_date TEXT, timestamp TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS sync_queue
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                     operation TEXT, data TEXT, timestamp TEXT)''')
        
        conn.commit()
        conn.close()
        
    def cache_satellite_data(self, satellite_id: str, data: Dict[str, Any]):
        """Cache satellite data for offline use"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute('''INSERT OR REPLACE INTO satellite_data 
                        (id, data, timestamp) VALUES (?, ?, ?)''',
                     (satellite_id, json.dumps(data), 
                      datetime.now().isoformat()))
            conn.commit()
        finally:
            conn.close()
            
    def cache_trajectory_data(self, satellite_id: str, data: pd.DataFrame,
                            start_date: datetime, end_date: datetime):
        """Cache trajectory data for offline use"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute('''INSERT OR REPLACE INTO trajectory_data 
                        (satellite_id, data, start_date, end_date, timestamp) 
                        VALUES (?, ?, ?, ?, ?)''',
                     (satellite_id, data.to_json(), 
                      start_date.isoformat(),
                      end_date.isoformat(),
                      datetime.now().isoformat()))
            conn.commit()
        finally:
            conn.close()
            
    def get_cached_satellite_data(self, satellite_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached satellite data"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute('SELECT data FROM satellite_data WHERE id = ?', 
                     (satellite_id,))
            result = c.fetchone()
            if result:
                return json.loads(result[0])
            return None
        finally:
            conn.close()
            
    def get_cached_trajectory_data(self, satellite_id: str,
                                 start_date: datetime,
                                 end_date: datetime) -> Optional[pd.DataFrame]:
        """Retrieve cached trajectory data"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute('''SELECT data FROM trajectory_data 
                        WHERE satellite_id = ? AND 
                        start_date <= ? AND end_date >= ?''',
                     (satellite_id, end_date.isoformat(), 
                      start_date.isoformat()))
            result = c.fetchone()
            if result:
                return pd.read_json(result[0])
            return None
        finally:
            conn.close()
            
    def queue_sync_operation(self, operation: str, data: Dict[str, Any]):
        """Queue an operation for synchronization when online"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute('''INSERT INTO sync_queue 
                        (operation, data, timestamp) VALUES (?, ?, ?)''',
                     (operation, json.dumps(data), 
                      datetime.now().isoformat()))
            conn.commit()
            self.sync_queue.put((operation, data))
        finally:
            conn.close()
            
    def start_sync_thread(self, sync_callback):
        """Start background thread for data synchronization"""
        if self.sync_thread is None or not self.sync_thread.is_alive():
            self.sync_thread = threading.Thread(
                target=self._sync_worker,
                args=(sync_callback,),
                daemon=True
            )
            self.sync_thread.start()
            
    def _sync_worker(self, sync_callback):
        """Worker thread for processing sync queue"""
        while True:
            try:
                operation, data = self.sync_queue.get(timeout=1)
                sync_callback(operation, data)
                
                # Remove from database queue after successful sync
                conn = sqlite3.connect(self.db_path)
                c = conn.cursor()
                try:
                    c.execute('''DELETE FROM sync_queue 
                                WHERE operation = ? AND data = ?''',
                             (operation, json.dumps(data)))
                    conn.commit()
                finally:
                    conn.close()
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Sync error: {str(e)}")
                
    def clear_old_cache(self, days: int = 7):
        """Clear cache entries older than specified days"""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute('''DELETE FROM satellite_data 
                        WHERE timestamp < ?''', (cutoff_date,))
            c.execute('''DELETE FROM trajectory_data 
                        WHERE timestamp < ?''', (cutoff_date,))
            conn.commit()
        finally:
            conn.close()
            
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about cached data"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            stats = {
                "satellite_count": c.execute(
                    'SELECT COUNT(*) FROM satellite_data').fetchone()[0],
                "trajectory_count": c.execute(
                    'SELECT COUNT(*) FROM trajectory_data').fetchone()[0],
                "pending_syncs": c.execute(
                    'SELECT COUNT(*) FROM sync_queue').fetchone()[0],
                "oldest_entry": c.execute(
                    '''SELECT MIN(timestamp) FROM 
                       (SELECT timestamp FROM satellite_data 
                        UNION ALL 
                        SELECT timestamp FROM trajectory_data)'''
                ).fetchone()[0],
                "newest_entry": c.execute(
                    '''SELECT MAX(timestamp) FROM 
                       (SELECT timestamp FROM satellite_data 
                        UNION ALL 
                        SELECT timestamp FROM trajectory_data)'''
                ).fetchone()[0]
            }
            return stats
        finally:
            conn.close() 