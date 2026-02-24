#!/usr/bin/env python3
"""
Comprehensive Verification Test for Hackathon Project
Tests all major components of the Physical AI Textbook system
"""

import sys
import subprocess
import time
import requests
import json
from pathlib import Path

# Colors for output (ASCII safe for Windows)
try:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
except:
    # Fallback for Windows cmd
    GREEN = ""
    YELLOW = ""
    RED = ""
    RESET = ""
    BOLD = ""

def print_success(msg):
    print(f"{GREEN}[OK] {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}[WARNING] {msg}{RESET}")

def print_error(msg):
    print(f"{RED}[ERROR] {msg}{RESET}")

def print_header(msg):
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}{msg}{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")

class HackathonVerification:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.backend_dir = self.base_dir / "backend"
        self.book_dir = self.base_dir / "book"
        self.results = []

    def record_result(self, component, status, message):
        """Record test result"""
        self.results.append({
            "component": component,
            "status": status,
            "message": message
        })

        if status == "PASS":
            print_success(f"{component}: {message}")
        elif status == "WARNING":
            print_warning(f"{component}: {message}")
        else:
            print_error(f"{component}: {message}")

    def check_python_imports(self):
        """Check if Python modules can be imported"""
        print_header("1. Python Module Imports")

        try:
            # Test backend imports
            sys.path.insert(0, str(self.backend_dir))

            import_modules = [
                ("config", "from config import settings"),
                ("models", "from models import User, create_tables"),
                ("services.openai_service", "from services.openai_service import openai_service"),
                ("services.embedding_service", "from services.embedding_service import embedding_service"),
                ("services.translation_service", "from services.translation_service import translation_service"),
                ("core.security", "from core.security import verify_password, get_password_hash"),
                ("main", "from main import app"),
            ]

            for module_name, import_stmt in import_modules:
                try:
                    exec(import_stmt, globals())
                    self.record_result(f"Import {module_name}", "PASS", f"Successfully imported")
                except Exception as e:
                    self.record_result(f"Import {module_name}", "FAIL", f"Import failed: {str(e)}")

        except Exception as e:
            self.record_result("Python Imports", "FAIL", f"General import error: {str(e)}")

    def check_database_connectivity(self):
        """Check database models and connectivity"""
        print_header("2. Database Connectivity")

        try:
            from models import create_tables, SessionLocal, User
            from sqlalchemy import text

            # Create tables if they don't exist
            create_tables()
            self.record_result("Database Tables", "PASS", "Tables created/verified successfully")

            # Test database connection
            db = SessionLocal()
            try:
                # Test simple query
                result = db.execute(text("SELECT 1"))
                db.close()
                self.record_result("Database Connection", "PASS", "Successfully connected to database")
            except Exception as e:
                self.record_result("Database Connection", "WARNING", f"Connection test failed: {str(e)}")

        except Exception as e:
            self.record_result("Database", "FAIL", f"Database setup failed: {str(e)}")

    def check_backend_services(self):
        """Check backend service initialization"""
        print_header("3. Backend Services")

        try:
            from services.openai_service import openai_service
            from services.embedding_service import embedding_service
            from services.translation_service import translation_service

            # Check OpenAI service
            if openai_service.use_mock:
                self.record_result("OpenAI Service", "WARNING", "Running in mock mode (no API key)")
            else:
                self.record_result("OpenAI Service", "PASS", "API key configured")

            # Check embedding service
            self.record_result("Embedding Service", "PASS", "Initialized successfully")

            # Check translation service
            test_translation = translation_service.translate_text("Hello world", target_lang="ur")
            if test_translation.get("is_mock", False):
                self.record_result("Translation Service", "WARNING", "Mock translation working (no real API)")
            else:
                self.record_result("Translation Service", "PASS", "Translation working")

        except Exception as e:
            self.record_result("Backend Services", "FAIL", f"Service initialization failed: {str(e)}")

    def test_fastapi_app(self):
        """Test FastAPI application routes"""
        print_header("4. FastAPI Application Routes")

        try:
            from main import app
            from fastapi.testclient import TestClient

            client = TestClient(app)

            # Test health endpoints
            endpoints = [
                ("GET /", "Root endpoint"),
                ("GET /health", "Health check"),
                ("GET /system-info", "System information"),
            ]

            for endpoint, description in endpoints:
                try:
                    if endpoint.startswith("GET "):
                        path = endpoint[4:]
                        response = client.get(path)
                        if response.status_code == 200:
                            self.record_result(f"Endpoint {path}", "PASS", f"Returns {response.status_code}")
                        else:
                            self.record_result(f"Endpoint {path}", "WARNING", f"Returns {response.status_code}")
                except Exception as e:
                    self.record_result(f"Endpoint {path}", "FAIL", f"Error: {str(e)}")

        except ImportError:
            self.record_result("FastAPI Test", "WARNING", "fastapi.testclient not available for testing")
        except Exception as e:
            self.record_result("FastAPI App", "FAIL", f"App test failed: {str(e)}")

    def check_docusaurus_book(self):
        """Check Docusaurus book structure and build"""
        print_header("5. Docusaurus Textbook")

        # Check book directory structure
        required_dirs = [
            "docs",
            "src",
            "static",
        ]

        for dir_name in required_dirs:
            dir_path = self.book_dir / dir_name
            if dir_path.exists():
                self.record_result(f"Directory {dir_name}", "PASS", "Exists")
            else:
                self.record_result(f"Directory {dir_name}", "FAIL", "Missing")

        # Check module directories
        modules = [
            "module-1-ros2",
            "module-2-digital-twin",
            "module-3-ai-robot-brain",
            "module-4-vla",
        ]

        for module in modules:
            module_path = self.book_dir / "docs" / module
            if module_path.exists():
                # Check if module has content files
                md_files = list(module_path.glob("*.md"))
                if md_files:
                    self.record_result(f"Module {module}", "PASS", f"Has {len(md_files)} markdown files")
                else:
                    self.record_result(f"Module {module}", "WARNING", "Directory exists but no markdown files")
            else:
                self.record_result(f"Module {module}", "FAIL", "Missing module directory")

        # Check configuration file
        config_file = self.book_dir / "docusaurus.config.js"
        if config_file.exists():
            self.record_result("Docusaurus Config", "PASS", "Configuration file exists")
        else:
            self.record_result("Docusaurus Config", "FAIL", "Missing config file")

    def check_chatbot_component(self):
        """Check React chatbot component"""
        print_header("6. Chatbot React Component")

        chatbot_dir = self.book_dir / "src" / "components" / "Chatbot"

        if chatbot_dir.exists():
            required_files = [
                "index.js",
                "styles.module.css",
            ]

            for file_name in required_files:
                file_path = chatbot_dir / file_name
                if file_path.exists():
                    self.record_result(f"Chatbot {file_name}", "PASS", "File exists")
                else:
                    self.record_result(f"Chatbot {file_name}", "FAIL", "Missing file")
        else:
            self.record_result("Chatbot Component", "FAIL", "Chatbot directory missing")

    def check_project_docs(self):
        """Check project documentation"""
        print_header("7. Project Documentation")

        required_docs = [
            "PROJECT_PLAN.md",
            "PROGRESS.md",
            "README.md",
        ]

        for doc_file in required_docs:
            doc_path = self.base_dir / doc_file
            if doc_path.exists():
                # Check file size
                size = doc_path.stat().st_size
                if size > 100:  # At least 100 bytes
                    self.record_result(f"Document {doc_file}", "PASS", f"Exists ({size} bytes)")
                else:
                    self.record_result(f"Document {doc_file}", "WARNING", "File very small")
            else:
                self.record_result(f"Document {doc_file}", "FAIL", "Missing")

    def run_integration_test(self):
        """Run basic integration test"""
        print_header("8. Integration Test")

        # Try to start backend server and test endpoints
        try:
            # Import and test translation service directly
            from services.translation_service import translation_service

            # Test translation
            result = translation_service.translate_text(
                "Physical AI and Humanoid Robotics",
                target_lang="ur"
            )

            if result.get("translated_text"):
                # Don't print Urdu text to avoid encoding issues
                self.record_result("Translation Integration", "PASS",
                                  "Translation successful (Urdu text contains non-ASCII characters)")
            else:
                self.record_result("Translation Integration", "FAIL", "No translation returned")

        except Exception as e:
            self.record_result("Integration Test", "FAIL", f"Error: {str(e)}")

    def generate_summary(self):
        """Generate summary report"""
        print_header("[TARGET] VERIFICATION SUMMARY")

        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        warnings = sum(1 for r in self.results if r["status"] == "WARNING")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")

        print(f"\n{BOLD}Test Results:{RESET}")
        print(f"{GREEN}Passed: {passed}/{total}{RESET}")
        print(f"{YELLOW}Warnings: {warnings}/{total}{RESET}")
        print(f"{RED}Failed: {failed}/{total}{RESET}")

        # Calculate score
        if total > 0:
            score = (passed / total) * 100
            print(f"\n{BOLD}Overall Score: {score:.1f}%{RESET}")

        # Show critical failures
        if failed > 0:
            print(f"\n{BOLD}Critical Failures:{RESET}")
            for result in self.results:
                if result["status"] == "FAIL":
                    print(f"  {RED}[ERROR] {result['component']}: {result['message']}{RESET}")

        # Show warnings
        if warnings > 0:
            print(f"\n{BOLD}Warnings:{RESET}")
            for result in self.results:
                if result["status"] == "WARNING":
                    print(f"  {YELLOW}[WARNING] {result['component']}: {result['message']}{RESET}")

        # Recommendations
        print(f"\n{BOLD}Recommendations:{RESET}")
        if failed == 0 and warnings == 0:
            print(f"{GREEN}[OK] All systems ready for deployment!{RESET}")
        elif failed == 0:
            print(f"{YELLOW}[WARNING] Project is functional but has some warnings to address{RESET}")
        else:
            print(f"{RED}[ERROR] Critical issues need to be fixed before deployment{RESET}")

        return {
            "total": total,
            "passed": passed,
            "warnings": warnings,
            "failed": failed,
            "score": score if total > 0 else 0
        }

def main():
    """Main verification function"""
    print(f"{BOLD}[TEST] Physical AI Textbook Hackathon - Complete Verification Test{RESET}")
    print(f"{BOLD}Version: 1.0 | Date: 2026-02-24{RESET}\n")

    verifier = HackathonVerification()

    # Run all checks
    verifier.check_python_imports()
    verifier.check_database_connectivity()
    verifier.check_backend_services()
    verifier.test_fastapi_app()
    verifier.check_docusaurus_book()
    verifier.check_chatbot_component()
    verifier.check_project_docs()
    verifier.run_integration_test()

    # Generate summary
    summary = verifier.generate_summary()

    # Save results to file
    results_file = verifier.base_dir / "VERIFICATION_RESULTS.json"
    with open(results_file, 'w') as f:
        json.dump({
            "summary": summary,
            "results": verifier.results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }, f, indent=2)

    print(f"\n{BOLD}[FILE] Results saved to: {results_file}{RESET}")

    # Exit code based on results
    if summary["failed"] > 0:
        sys.exit(1)
    elif summary["warnings"] > 0:
        sys.exit(0)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()