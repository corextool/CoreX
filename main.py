import flet as ft
import subprocess
import threading
import os

# --- المحرك الداخلي لـ CoreX ---
class CoreXEngine:
    def __init__(self):
        self.is_rooted = self.check_root()
        self.active_slot = self.get_active_slot()
        self.root_env = self.detect_root_type()

    def execute(self, command):
        try:
            process = subprocess.run(['su', '-c', command], capture_output=True, text=True, timeout=10)
            return process.stdout.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def check_root(self):
        return "uid=0(root)" in self.execute('id')

    def get_active_slot(self):
        slot = self.execute('getprop ro.boot.slot_suffix')
        return slot if slot else "None"

    def detect_root_type(self):
        if not self.is_rooted: return "No Root"
        version = self.execute('su -v').lower()
        if 'magisk' in version: return "Magisk"
        if 'ksu' in version: return "KernelSU"
        if 'apatch' in version: return "APatch"
        return "Unknown"

    def get_installed_apps(self):
        cmd = "pm list packages -U -3"
        result = self.execute(cmd)
        apps = []
        if result and "Error" not in result:
            for line in result.strip().split('\n'):
                if 'package:' in line and 'uid:' in line:
                    p = line.split()
                    apps.append({"pkg": p[0].replace('package:', ''), "uid": p[1].replace('uid:', '')})
        return apps

# --- الواجهة الرسومية ---
def main(page: ft.Page):
    page.title = "CoreX Root Tool"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121212"
    engine = CoreXEngine()

    # شاشة الحالة
    status_text = ft.Text("CoreX Dashboard", size=25, weight="bold", color="#00FFCC")
    info_card = ft.Container(
        content=ft.Column([
            ft.Text(f"Root: {'YES' if engine.is_rooted else 'NO'}", size=16),
            ft.Text(f"Env: {engine.root_env}", size=16),
            ft.Text(f"Slot: {engine.active_slot}", size=16),
        ]),
        padding=20, bgcolor="#1E1E1E", border_radius=10
    )

    app_list = ft.ListView(expand=True, spacing=10)

    def load_apps(e):
        app_list.controls.clear()
        apps = engine.get_installed_apps()
        for app in apps:
            app_list.controls.append(ft.ListTile(title=ft.Text(app['pkg']), subtitle=ft.Text(f"UID: {app['uid']}")))
        page.update()

    page.add(
        status_text,
        info_card,
        ft.ElevatedButton("Fetch Apps", on_click=load_apps, bgcolor="#00FFCC", color="black"),
        app_list
    )

if __name__ == "__main__":
    ft.app(target=main)
