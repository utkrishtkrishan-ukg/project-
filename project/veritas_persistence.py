#!/usr/bin/env python3
"""
VERITAS Persistence Layer
Handles storage and retrieval of trust certificates and audit trails
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import os


class VeritasDatabase:
    """SQLite database for storing VERITAS trust certificates and audit trails"""

    def __init__(self, db_path: str = "veritas_audit.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create trust certificates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trust_certificates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                certificate_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                user_input TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                overall_trust_score REAL NOT NULL,
                decision TEXT NOT NULL,
                privacy_score REAL NOT NULL,
                bias_score REAL NOT NULL,
                transparency_score REAL NOT NULL,
                ethics_score REAL NOT NULL,
                alerts TEXT,
                recommendations TEXT,
                agent_analysis TEXT,
                trust_level TEXT,
                ollama_enabled BOOLEAN DEFAULT FALSE
            )
        """)

        # Create audit trail table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_trail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                certificate_id TEXT,
                agent_name TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                processing_time_ms INTEGER,
                confidence_level INTEGER
            )
        """)

        # Create statistics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE NOT NULL,
                total_certificates INTEGER DEFAULT 0,
                average_trust_score REAL DEFAULT 0,
                blocked_count INTEGER DEFAULT 0,
                warned_count INTEGER DEFAULT 0,
                proceed_count INTEGER DEFAULT 0,
                most_common_alerts TEXT
            )
        """)

        # Create system health table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_health (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                ollama_connected BOOLEAN DEFAULT FALSE,
                ollama_model TEXT,
                processing_time_avg_ms REAL,
                error_count INTEGER DEFAULT 0,
                uptime_minutes INTEGER
            )
        """)

        conn.commit()
        conn.close()

    def store_certificate(self, certificate: Dict[str, Any]) -> str:
        """Store trust certificate in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO trust_certificates (
                    certificate_id, timestamp, user_input, ai_response,
                    overall_trust_score, decision, privacy_score, bias_score,
                    transparency_score, ethics_score, alerts, recommendations,
                    agent_analysis, trust_level, ollama_enabled
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    certificate["metadata"]["certificate_id"],
                    certificate["metadata"]["timestamp"],
                    certificate["content"]["user_input"],
                    certificate["content"]["ai_response"],
                    certificate["scoring"]["overall_trust_score"],
                    certificate["scoring"]["decision"],
                    certificate["scoring"]["individual_scores"]["privacy"],
                    certificate["scoring"]["individual_scores"]["bias"],
                    certificate["scoring"]["individual_scores"]["transparency"],
                    certificate["scoring"]["individual_scores"]["ethics"],
                    json.dumps(certificate["alerts"]),
                    json.dumps(certificate["recommendations"]),
                    json.dumps(certificate["agent_analysis"]),
                    certificate["trust_level"],
                    certificate["metadata"].get("ollama_enabled", False),
                ),
            )

            # Log audit trail
            self._log_audit_trail(
                certificate["metadata"]["certificate_id"],
                "CONCORDIA",
                "CERTIFICATE_STORED",
                f"Trust score: {certificate['scoring']['overall_trust_score']}",
            )

            conn.commit()
            return certificate["metadata"]["certificate_id"]

        except sqlite3.IntegrityError:
            print(
                f"Certificate {certificate['metadata']['certificate_id']} already exists"
            )
            return None
        finally:
            conn.close()

    def get_certificate(self, certificate_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve specific certificate by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM trust_certificates WHERE certificate_id = ?
        """,
            (certificate_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return self._row_to_certificate(row)
        return None

    def get_recent_certificates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent trust certificates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM trust_certificates 
            ORDER BY timestamp DESC 
            LIMIT ?
        """,
            (limit,),
        )

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_certificate(row) for row in rows]

    def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get system statistics for specified period"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Date range
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # Overall stats
        cursor.execute(
            """
            SELECT 
                COUNT(*) as total,
                AVG(overall_trust_score) as avg_score,
                SUM(CASE WHEN decision = 'block' THEN 1 ELSE 0 END) as blocked,
                SUM(CASE WHEN decision = 'warn' THEN 1 ELSE 0 END) as warned,
                SUM(CASE WHEN decision = 'proceed' THEN 1 ELSE 0 END) as proceed
            FROM trust_certificates 
            WHERE timestamp >= ?
        """,
            (start_date,),
        )

        stats_row = cursor.fetchone()

        # Agent performance
        cursor.execute(
            """
            SELECT 
                agent_name,
                COUNT(*) as action_count,
                AVG(processing_time_ms) as avg_time,
                AVG(confidence_level) as avg_confidence
            FROM audit_trail 
            WHERE timestamp >= ?
            GROUP BY agent_name
        """,
            (start_date,),
        )

        agent_rows = cursor.fetchall()

        # Daily breakdown
        cursor.execute(
            """
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as certificates,
                AVG(overall_trust_score) as avg_score
            FROM trust_certificates 
            WHERE timestamp >= ?
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        """,
            (start_date,),
        )

        daily_rows = cursor.fetchall()

        conn.close()

        return {
            "period_days": days,
            "overall": {
                "total_certificates": stats_row[0] or 0,
                "average_trust_score": round(stats_row[1] or 0, 2),
                "blocked_count": stats_row[2] or 0,
                "warned_count": stats_row[3] or 0,
                "proceed_count": stats_row[4] or 0,
                "block_rate": round((stats_row[2] or 0) / max(1, stats_row[0]) * 100, 1)
                if stats_row[0] > 0
                else 0,
                "proceed_rate": round(
                    (stats_row[4] or 0) / max(1, stats_row[0]) * 100, 1
                )
                if stats_row[0] > 0
                else 0,
            },
            "agent_performance": [
                {
                    "agent": row[0],
                    "actions": row[1],
                    "avg_processing_time_ms": round(row[2] or 0, 2),
                    "avg_confidence": round(row[3] or 0, 1),
                }
                for row in agent_rows
            ],
            "daily_breakdown": [
                {
                    "date": row[0],
                    "certificates": row[1],
                    "avg_score": round(row[2] or 0, 2),
                }
                for row in daily_rows
            ],
        }

    def _log_audit_trail(
        self,
        certificate_id: str,
        agent_name: str,
        action: str,
        details: str,
        processing_time_ms: int = None,
        confidence_level: int = None,
    ):
        """Log agent action to audit trail"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO audit_trail (
                timestamp, certificate_id, agent_name, action, details, processing_time_ms, confidence_level
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                datetime.now().isoformat(),
                certificate_id,
                agent_name,
                action,
                details,
                processing_time_ms,
                confidence_level,
            ),
        )

        conn.commit()
        conn.close()

    def _row_to_certificate(self, row: tuple) -> Dict[str, Any]:
        """Convert database row to certificate format"""
        return {
            "id": row[0],
            "certificate_id": row[1],
            "timestamp": row[2],
            "user_input": row[3],
            "ai_response": row[4],
            "overall_trust_score": row[5],
            "decision": row[6],
            "individual_scores": {
                "privacy": row[7],
                "bias": row[8],
                "transparency": row[9],
                "ethics": row[10],
            },
            "alerts": json.loads(row[11]) if row[11] else [],
            "recommendations": json.loads(row[12]) if row[12] else [],
            "agent_analysis": json.loads(row[13]) if row[13] else {},
            "trust_level": row[14],
            "ollama_enabled": bool(row[15]),
        }

    def export_certificates(self, output_file: str, format_type: str = "json") -> bool:
        """Export certificates to file"""
        try:
            certificates = self.get_recent_certificates(1000)  # Get all certificates

            if format_type.lower() == "json":
                with open(output_file, "w") as f:
                    json.dump(certificates, f, indent=2, default=str)

            elif format_type.lower() == "csv":
                import csv

                with open(output_file, "w", newline="") as f:
                    if certificates:
                        writer = csv.DictWriter(f, fieldnames=certificates[0].keys())
                        writer.writeheader()
                        writer.writerows(certificates)

            return True

        except Exception as e:
            print(f"Export failed: {e}")
            return False

    def cleanup_old_records(self, days: int = 90):
        """Clean up old records to manage database size"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # Delete old certificates and audit records
        cursor.execute(
            "DELETE FROM trust_certificates WHERE timestamp < ?", (cutoff_date,)
        )
        cursor.execute("DELETE FROM audit_trail WHERE timestamp < ?", (cutoff_date,))

        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()

        print(f"Cleaned up {deleted_count} old records from before {cutoff_date}")


class VeritasFileStorage:
    """File-based storage backup for certificates"""

    def __init__(self, storage_dir: str = "veritas_storage"):
        self.storage_dir = storage_dir
        self.certificates_dir = os.path.join(storage_dir, "certificates")
        self.audit_dir = os.path.join(storage_dir, "audit")

        os.makedirs(self.certificates_dir, exist_ok=True)
        os.makedirs(self.audit_dir, exist_ok=True)

    def save_certificate(self, certificate: Dict[str, Any]) -> str:
        """Save certificate to file"""
        cert_id = certificate["metadata"]["certificate_id"]
        filename = os.path.join(self.certificates_dir, f"{cert_id}.json")

        with open(filename, "w") as f:
            json.dump(certificate, f, indent=2, default=str)

        return filename

    def load_certificate(self, cert_id: str) -> Optional[Dict[str, Any]]:
        """Load certificate from file"""
        filename = os.path.join(self.certificates_dir, f"{cert_id}.json")

        if os.path.exists(filename):
            with open(filename, "r") as f:
                return json.load(f)
        return None

    def list_certificates(self) -> List[str]:
        """List all certificate IDs"""
        files = os.listdir(self.certificates_dir)
        return [f.replace(".json", "") for f in files if f.endswith(".json")]


# Test persistence layer
if __name__ == "__main__":
    print("Testing VERITAS Persistence Layer...")

    # Initialize database
    db = VeritasDatabase()
    file_storage = VeritasFileStorage()

    # Create sample certificate
    sample_cert = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "veritas_version": "2.0.0",
            "certificate_id": f"TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}_1234",
            "ollama_enabled": True,
        },
        "content": {
            "user_input": "What is VERITAS?",
            "ai_response": "VERITAS is a self-auditing AI assistant with 4 Guardian Agents.",
        },
        "scoring": {
            "overall_trust_score": 92.4,
            "decision": "proceed",
            "individual_scores": {
                "privacy": 95.0,
                "bias": 88.0,
                "transparency": 91.0,
                "ethics": 94.0,
            },
        },
        "alerts": ["High trust score detected"],
        "recommendations": ["Response is safe to deliver"],
        "trust_level": "Excellent",
        "agent_analysis": {
            "privacy": {"score": 95.0, "issues_found": [], "recommendations": []},
            "bias": {"score": 88.0, "biased_terms": [], "neutral_alternatives": []},
            "transparency": {
                "score": 91.0,
                "confidence_level": 90,
                "sources_cited": True,
                "unverified_claims": [],
            },
            "ethics": {
                "score": 94.0,
                "harm_detected": False,
                "safety_risks": [],
                "misinformation": False,
            },
        },
    }

# Store in database
    cert_id = db.store_certificate(sample_cert)
        if cert_id:
            print(f"Stored certificate: {cert_id}")
        
        # Store in files
        file_path = file_storage.save_certificate(sample_cert)
        print(f"Saved certificate to file: {file_path}")
        
        # Retrieve from database
        retrieved = db.get_certificate(cert_id)
        if retrieved:
            print(f"Retrieved certificate with score: {retrieved['overall_trust_score']}")
        
        # Get statistics
        stats = db.get_statistics(7)  # Last 7 days
        print(f"Statistics (last 7 days): {stats['overall']['total_certificates']} certificates")
        print(f"Average trust score: {stats['overall']['average_trust_score']}")
        print(f"Proceed rate: {stats['overall']['proceed_rate']}%")
        
        # Export certificates
        if db.export_certificates("certificates_export.json"):
            print("Exported certificates to certificates_export.json")
        
        print("Persistence layer test complete!")
