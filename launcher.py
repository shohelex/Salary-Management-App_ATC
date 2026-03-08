"""ATC Management System - Portable Launcher"""
import os
import sys
import time
import socket
import threading
import webbrowser


def get_base_dir():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def get_data_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def find_free_port(start=8000, end=8100):
    for port in range(start, end):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return 8000


def open_browser(port):
    time.sleep(2.5)
    webbrowser.open(f'http://127.0.0.1:{port}')


def main():
    base_dir = get_base_dir()
    data_dir = get_data_dir()

    os.environ['DJANGO_SETTINGS_MODULE'] = 'atc_management.settings'
    os.environ['ATC_BASE_DIR'] = base_dir
    os.environ['ATC_DATA_DIR'] = data_dir

    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)

    import django
    django.setup()

    from django.core.management import call_command

    print("=" * 60)
    print("  Asian Trade Corporation - Management System")
    print("=" * 60)
    print()

    print("[1/2] Setting up database...")
    call_command('migrate', '--run-syncdb', verbosity=0)
    print("      Database ready.")

    # Create default admin if no users exist
    from django.contrib.auth.models import User
    if not User.objects.exists():
        User.objects.create_superuser('admin', '', 'admin123')
        print("      Default admin created (username: admin, password: admin123)")
        print("      *** Please change the password after first login! ***")

    port = find_free_port()
    print(f"[2/2] Starting server on http://127.0.0.1:{port}")
    print()
    print("-" * 60)
    print(f"  Open your browser to: http://127.0.0.1:{port}")
    print("  Press Ctrl+C to stop the server and exit.")
    print("-" * 60)
    print()

    browser_thread = threading.Thread(target=open_browser, args=(port,), daemon=True)
    browser_thread.start()

    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'runserver', f'127.0.0.1:{port}', '--noreload'])
    except KeyboardInterrupt:
        print("\nServer stopped. Goodbye!")
        sys.exit(0)


if __name__ == '__main__':
    main()
