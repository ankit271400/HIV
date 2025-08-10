`python
import sqlite3
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_PATH = Path("data/hiv_assessment.db")

def init_database():
    """Initialize the SQLite database with required tables"""
    try:
        # Create data directory if it doesn't exist
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            # Create assessments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    encrypted_data TEXT NOT NULL,
                    risk_score INTEGER,
                    risk_level TEXT,
                    thermal_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create thermal_analyses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS thermal_analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    max_temperature REAL,
                    average_temperature REAL,
                    fever_detected BOOLEAN,
                    fever_severity TEXT,
                    hotspot_count INTEGER,
                    confidence_score REAL,
                    calibration_offset REAL,
                    raw_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create user_sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    assessments_completed INTEGER DEFAULT 0,
                    thermal_analyses_performed INTEGER DEFAULT 0,
                    user_preferences TEXT,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Create testing_centers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS testing_centers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    address TEXT NOT NULL,
                    phone TEXT,
                    hours TEXT,
                    services TEXT,
                    cost TEXT,
                    accepts_insurance BOOLEAN,
                    walk_ins_accepted BOOLEAN,
                    appointment_required BOOLEAN,
                    languages TEXT,
                    website TEXT,
                    latitude REAL,
                    longitude REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create thermal_calibrations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS thermal_calibrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    reference_temperature REAL NOT NULL,
                    measured_temperature REAL NOT NULL,
                    calibration_offset REAL NOT NULL,
                    ambient_temperature REAL,
                    calibration_method TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_assessments_session ON assessments(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_assessments_created ON assessments(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_thermal_session ON thermal_analyses(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_thermal_created ON thermal_analyses(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_id ON user_sessions(session_id)")
            
            conn.commit()
            logger.info("✅ Database initialized successfully")
            
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

def get_db():
    """Get database connection"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

def store_assessment(session_id: str, assessment_data: Dict[str, Any], encrypted_data: str) -> int:
    """Store assessment data in database"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO assessments (session_id, encrypted_data, risk_score, risk_level, thermal_data)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_id,
                encrypted_data,
                assessment_data.get('risk_score'),
                assessment_data.get('risk_level'),
                assessment_data.get('thermal_data')
            ))
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"Failed to store assessment: {e}")
        raise

def store_thermal_analysis(session_id: str, thermal_data: Dict[str, Any]) -> int:
    """Store thermal analysis data in database"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO thermal_analyses (
                    session_id, max_temperature, average_temperature, fever_detected,
                    fever_severity, hotspot_count, confidence_score, calibration_offset, raw_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                thermal_data.get('max_temperature'),
                thermal_data.get('average_temperature'),
                thermal_data.get('fever_detected'),
                thermal_data.get('fever_severity'),
                thermal_data.get('hotspot_count'),
                thermal_data.get('confidence_score'),
                thermal_data.get('calibration_offset'),
                str(thermal_data.get('raw_data', {}))
            ))
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"Failed to store thermal analysis: {e}")
        raise

def get_session_data(session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve session data"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM user_sessions WHERE session_id = ? AND is_active = 1
            """, (session_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    except Exception as e:
        logger.error(f"Failed to get session data: {e}")
        return None

def update_session_activity(session_id: str):
    """Update session last activity timestamp"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE user_sessions 
                SET last_activity = CURRENT_TIMESTAMP 
                WHERE session_id = ?
            """, (session_id,))
            conn.commit()
    except Exception as e:
        logger.error(f"Failed to update session activity: {e}")

def get_recent_thermal_calibration(session_id: str) -> Optional[Dict[str, Any]]:
    """Get the most recent thermal calibration for a session"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM thermal_calibrations 
                WHERE session_id = ? AND is_active = 1 
                ORDER BY created_at DESC 
                LIMIT 1
            """, (session_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    except Exception as e:
        logger.error(f"Failed to get thermal calibration: {e}")
        return None

def store_thermal_calibration(session_id: str, calibration_data: Dict[str, Any]) -> int:
    """Store thermal calibration data"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO thermal_calibrations (
                    session_id, reference_temperature, measured_temperature,
                    calibration_offset, ambient_temperature, calibration_method
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                calibration_data['reference_temperature'],
                calibration_data['measured_temperature'],
                calibration_data['calibration_offset'],
                calibration_data.get('ambient_temperature'),
                calibration_data.get('calibration_method', 'manual')
            ))
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"Failed to store thermal calibration: {e}")
        raise

def cleanup_old_sessions(days_old: int = 7):
    """Clean up old inactive sessions"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE user_sessions 
                SET is_active = 0 
                WHERE last_activity < datetime('now', '-{} days')
            """.format(days_old))
            conn.commit()
            logger.info(f"Cleaned up sessions older than {days_old} days")
    except Exception as e:
        logger.error(f"Failed to cleanup old sessions: {e}")
```
