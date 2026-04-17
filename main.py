import flet as ft
import subprocess

# --- المحرك الداخلي (CoreX Engine) ---
class CoreXEngine:
    def __init__(self):
        self.is_rooted = self.check_root()
        self.root_env = self.detect_root_type()

    def execute(self, command):
        try:
            process = subprocess.run(['su', '-c', command], capture_output=True, text=True, timeout=10)
            return process.stdout.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def check_root(self):
        return "uid=0(root)" in self.execute('id')

    def detect_root_type(self):
        if not self.is_rooted: return "No Root"
        version = self.execute('su -v').lower()
        if 'magisk' in version: return "Magisk"
        if 'ksu' in version: return "KernelSU"
        if 'apatch' in version: return "APatch"
        return "Unknown"

    def verify_root_access(self):
        if not self.is_rooted: return "❌ Root is NOT granted."
        res = self.execute('ls -l /data/adb')
        if "denied" in res or "No such file" in res:
            return "⚠️ Root found, but deep access is restricted!"
        return "✅ Root is fully operational (Deep Access Verified)"

    def check_security_props(self):
        boot_state = self.execute('getprop ro.boot.verifiedbootstate').strip()
        selinux = self.execute('getenforce').strip()
        msg = f"Bootloader: {boot_state}\nSELinux: {selinux}\n"
        if boot_state != 'green' or selinux != 'Enforcing':
            msg += "⚠️ Device may fail Play Integrity."
        else:
            msg += "✅ System appears secure."
        return msg

    def get_system_apps(self):
        # جلب أول 20 تطبيق نظام للتجربة وتجنب تعليق الواجهة
        res = self.execute("pm list packages -s | head -n 20")
        apps = []
        if res and "Error" not in res:
            for line in res.split('\n'):
                if 'package:' in line:
                    apps.append(line.replace('package:', '').strip())
        return apps

    def toggle_app(self, pkg, disable=True):
        cmd = f"pm disable-user --user 0 {pkg}" if disable else f"pm enable {pkg}"
        return self.execute(cmd)

# --- الواجهة الرسومية (UI) ---
def main(page: ft.Page):
    page.title = "CoreX Tool"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000" # خلفية سوداء عميقة كما طلبت
    page.padding = 20
    
    engine = CoreXEngine()

    # --- 1. تبويب لوحة القيادة ---
    dash_text = ft.Text(f"Environment: {engine.root_env}", size=20, color="#00FFCC", weight="bold")
    verify_btn = ft.ElevatedButton("Deep Root Verify", bgcolor="#222222", color="white")
    verify_result = ft.Text("", color="white")
    
    def on_verify(e):
        verify_result.value = engine.verify_root_access()
        page.update()
    verify_btn.on_click = on_verify
    
    tab_dashboard = ft.Column([dash_text, verify_btn, verify_result], spacing=20)

    # --- 2. تبويب الأمان (Security) ---
    sec_btn = ft.ElevatedButton("Check Play Integrity Props", bgcolor="#222222", color="white")
    sec_result = ft.Text("", color="yellow")
    
    def on_sec_check(e):
        sec_result.value = engine.check_security_props()
        page.update()
    sec_btn.on_click = on_sec_check
    
    tab_security = ft.Column([ft.Text("System Integrity Check", size=20, color="#00FFCC"), sec_btn, sec_result], spacing=20)

    # --- 3. تبويب تطبيقات النظام (Debloater) ---
    app_list = ft.ListView(expand=True, spacing=10)
    
    def load_apps(e):
        app_list.controls.clear()
        apps = engine.get_system_apps()
        for app in apps:
            row = ft.Row([
                ft.Text(app, expand=True, color="white", size=12),
                ft.IconButton(ft.icons.BLOCK, icon_color="red", on_click=lambda e, p=app: disable_action(p))
            ])
            app_list.controls.append(row)
        page.update()

    def disable_action(pkg):
        res = engine.toggle_app(pkg, disable=True)
        # إظهار رسالة صغيرة بالأسفل (SnackBar)
        page.snack_bar = ft.SnackBar(ft.Text(f"Result: {res}"))
        page.snack_bar.open = True
        page.update()

    load_apps_btn = ft.ElevatedButton("Load System Apps", on_click=load_apps, bgcolor="#222222", color="white")
    tab_debloater = ft.Column([ft.Text("System App Manager", size=20, color="#00FFCC"), load_apps_btn, app_list], expand=True)

    # --- تجميع التبويبات في الشاشة ---
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        unselected_label_color="grey",
        selected_label_color="#00FFCC",
        tabs=[
            ft.Tab(text="Dashboard", content=ft.Container(content=tab_dashboard, padding=20)),
            ft.Tab(text="Security", content=ft.Container(content=tab_security, padding=20)),
            ft.Tab(text="Debloater", content=ft.Container(content=tab_debloater, padding=20)),
        ],
        expand=1,
    )
    
    page.add(tabs)

if __name__ == "__main__":
    ft.app(target=main)
