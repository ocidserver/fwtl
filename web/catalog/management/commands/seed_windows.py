import sys
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from catalog.models import Alternative, App, Category, WindowsApp

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from package_classifier import PackageClassifier  # noqa: E402

# (windows, slug_kategori, [(app_slug, kompatibilitas, catatan_id, catatan_en)])
CURATED = [
    ("Google Chrome", "web-browser", [("chromium", 100, "Basis open-source Chrome, sinkronisasi akun Google.", "Open-source Chrome base with Google account sync.")]),
    ("Firefox", "web-browser", [("firefox", 100, "Versi Linux resmi, profil bisa dipindah.", "Official Linux build, profiles carry over.")]),
    ("Microsoft Edge", "web-browser", [("microsoft-edge-stable", 100, "Edge resmi untuk Linux dari Microsoft.", "Official Microsoft Edge for Linux.")]),
    ("Opera", "web-browser", [("opera", 100, "Opera resmi tersedia di AUR.", "Official Opera available in AUR.")]),
    ("Brave", "web-browser", [("brave", 100, "Brave resmi, sinkronisasi dompet dan bookmark.", "Official Brave with wallet and bookmark sync.")]),
    ("Microsoft Office", "office-productivity", [("libreoffice-fresh", 95, "Gratis, buka/simpan docx xlsx pptx.", "Free, opens/saves docx xlsx pptx."), ("onlyoffice", 90, "Tampilan mirip MS Office.", "Interface close to MS Office.")]),
    ("Adobe Acrobat", "office-productivity", [("okular", 90, "Pembaca dan anotasi PDF.", "PDF reader and annotator."), ("evince", 85, "Pembaca PDF ringan.", "Lightweight PDF reader.")]),
    ("Notepad++", "text-editor-ide", [("kate", 100, "Fitur setara, sesi dan plugin.", "Equal features with sessions and plugins."), ("notepadqq", 90, "Klon tampilan Notepad++.", "Notepad++ look-alike clone.")]),
    ("OneNote", "office-productivity", [("xournalpp", 80, "Catatan tulisan tangan dan PDF.", "Handwritten notes and PDF annotation."), ("joplin", 85, "Catatan Markdown dengan sinkronisasi.", "Markdown notes with sync.")]),
    ("Evernote", "office-productivity", [("joplin", 90, "Impor langsung dari Evernote.", "Direct import from Evernote."), ("tutanota-desktop", 60, "Fokus privasi.", "Privacy focused.")]),
    ("VLC", "media-player-video", [("vlc", 100, "Aplikasi yang sama di Linux.", "Same app on Linux.")]),
    ("Windows Media Player", "media-player-video", [("vlc", 100, "Memutar semua format WMP dan lebih.", "Plays everything WMP does and more.")]),
    ("Plex", "media-player-video", [("vlc", 80, "Untuk putar lokal; server Plex juga ada di AUR.", "For local playback; Plex server is also in AUR.")]),
    ("Kodi", "media-player-video", [("kodi", 100, "Aplikasi yang sama di Linux.", "Same app on Linux.")]),
    ("PotPlayer", "media-player-video", [("mpv", 85, "Ringan, kualitas tinggi via konfigurasi.", "Lightweight with high quality via config.")]),
    ("MPC-HC", "media-player-video", [("mpv", 85, "Pengganti ringan sekelas MPC.", "Lightweight MPC-class replacement.")]),
    ("Spotify", "audio-music", [("spotify", 100, "Klien resmi Spotify.", "Official Spotify client.")]),
    ("iTunes", "audio-music", [("clementine", 70, "Kelola koleksi musik lokal.", "Manage local music collection."), ("lollypop", 70, "Pemutar modern untuk GNOME.", "Modern player for GNOME.")]),
    ("Audacity", "audio-music", [("audacity", 100, "Aplikasi yang sama di Linux.", "Same app on Linux.")]),
    ("Foobar2000", "audio-music", [("deadbeef", 85, "Ringan dan modular seperti Foobar.", "Light and modular like Foobar.")]),
    ("MusicBee", "audio-music", [("lollypop", 75, "Manajemen koleksi yang rapi.", "Tidy collection management."), ("clementine", 75, "Fitur koleksi lengkap.", "Full collection features.")]),
    ("AIMP", "audio-music", [("audacious", 75, "Antarmuka klasik mirip Winamp/AIMP.", "Classic Winamp/AIMP-like interface.")]),
    ("Adobe Photoshop", "graphics-image-editing", [("gimp", 75, "Gratis; buka file PSD.", "Free; opens PSD files."), ("krita", 70, "Unggul untuk lukis digital.", "Best for digital painting.")]),
    ("GIMP", "graphics-image-editing", [("gimp", 100, "Aplikasi yang sama di Linux.", "Same app on Linux.")]),
    ("Paint.NET", "graphics-image-editing", [("pinta", 80, "Klon Paint.NET untuk Linux.", "Paint.NET clone for Linux.")]),
    ("CorelDRAW", "graphics-image-editing", [("inkscape", 75, "Vektor profesional open-source.", "Professional open-source vector editor.")]),
    ("Affinity Photo", "graphics-image-editing", [("krita", 65, "Alternatif lukis dan foto.", "Painting and photo alternative."), ("gimp", 65, "Olah foto umum.", "General photo editing.")]),
    ("Adobe Premiere", "video-editing", [("kdenlive", 75, "Editor multitrack open-source.", "Open-source multitrack editor."), ("davinci-resolve", 85, "Versi Linux resmi, gratis.", "Official Linux version, free.")]),
    ("DaVinci Resolve", "video-editing", [("davinci-resolve", 100, "Aplikasi yang sama di Linux.", "Same app on Linux.")]),
    ("Vegas Pro", "video-editing", [("shotcut", 70, "Editor lintas platform.", "Cross-platform editor."), ("kdenlive", 70, "Multitrack open-source.", "Open-source multitrack.")]),
    ("Filmora", "video-editing", [("openshot", 70, "Mudah untuk pemula.", "Easy for beginners."), ("shotcut", 70, "Filter dan mudah dipakai.", "Filters and easy to use.")]),
    ("VS Code", "development-tools", [("visual-studio-code", 100, "Build resmi Microsoft.", "Official Microsoft build."), ("vscodium", 95, "Build bebas telemetri.", "Telemetry-free build."), ("code", 100, "Paket repo resmi.", "Official repo package.")]),
    ("Visual Studio", "development-tools", [("qtcreator", 70, "IDE C++ lintas platform.", "Cross-platform C++ IDE."), ("code", 70, "Untuk banyak bahasa via ekstensi.", "Many languages via extensions.")]),
    ("IntelliJ IDEA", "development-tools", [("intellij-idea-community-edition", 100, "Edisi Community resmi.", "Official Community edition.")]),
    ("Eclipse", "development-tools", [("eclipse-java", 100, "Eclipse resmi untuk Java.", "Official Eclipse for Java.")]),
    ("PyCharm", "development-tools", [("pycharm-community-edition", 100, "Edisi Community resmi.", "Official Community edition.")]),
    ("Sublime Text", "text-editor-ide", [("sublime-text-4", 100, "Build resmi.", "Official build.")]),
    ("Vim", "text-editor-ide", [("neovim", 100, "Penerus modern Vim.", "Modern Vim successor."), ("vim", 100, "Vim klasik.", "Classic Vim.")]),
    ("Steam", "gaming", [("steam", 100, "Steam + Proton untuk gim Windows.", "Steam plus Proton for Windows games.")]),
    ("Epic Games", "gaming", [("heroic-games-launcher", 90, "Launcher Epic/GOG open-source.", "Open-source Epic/GOG launcher.")]),
    ("GOG Galaxy", "gaming", [("heroic-games-launcher", 90, "Dukungan GOG.", "GOG support."), ("lutris", 85, "Semua toko dalam satu launcher.", "All stores in one launcher.")]),
    ("Microsoft Outlook", "email-client", [("thunderbird", 90, "IMAP/Exchange via Owl.", "IMAP/Exchange via Owl."), ("evolution", 85, "Integrasi GNOME/Exchange.", "GNOME/Exchange integration.")]),
    ("Thunderbird", "email-client", [("thunderbird", 100, "Aplikasi yang sama di Linux.", "Same app on Linux.")]),
    ("Windows Explorer", "file-manager", [("dolphin", 90, "Manajer berkas KDE yang kuat.", "Powerful KDE file manager."), ("nemo", 85, "Ringan ala Cinnamon.", "Lightweight Cinnamon-style.")]),
    ("Total Commander", "file-manager", [("doublecmd-qt5", 85, "Komandan dua panel.", "Twin-panel commander."), ("krusader", 80, "Fitur lanjutan KDE.", "Advanced KDE features.")]),
    ("WinRAR", "archive-compression", [("7zip", 100, "Buka/buat RAR dan ZIP.", "Open/create RAR and ZIP."), ("peazip", 90, "GUI arsip lengkap.", "Full archive GUI.")]),
    ("7-Zip", "archive-compression", [("7zip", 100, "Aplikasi yang sama (CLI) + PeaZip untuk GUI.", "Same app CLI plus PeaZip for GUI.")]),
    ("WinZip", "archive-compression", [("ark", 85, "Manajer arsip KDE.", "KDE archive manager.")]),
    ("PeaZip", "archive-compression", [("peazip", 100, "Aplikasi yang sama di Linux.", "Same app on Linux.")]),
    ("uTorrent", "download-manager", [("qbittorrent", 95, "Bebas iklan, fitur setara.", "Ad-free with equal features."), ("transmission-qt", 85, "Sangat ringan.", "Very lightweight.")]),
    ("qBittorrent", "download-manager", [("qbittorrent", 100, "Aplikasi yang sama di Linux.", "Same app on Linux.")]),
    ("Internet Download Manager", "download-manager", [("aria2", 70, "Unduhan paralel via CLI/GUI.", "Parallel downloads via CLI/GUI."), ("fragments", 70, "GUI sederhana berbasis aria2.", "Simple aria2-based GUI.")]),
    ("TeamViewer", "remote-desktop-vnc", [("teamviewer", 100, "Klien resmi.", "Official client.")]),
    ("AnyDesk", "remote-desktop-vnc", [("anydesk", 100, "Klien resmi.", "Official client.")]),
    ("Microsoft Remote Desktop", "remote-desktop-vnc", [("remmina", 90, "RDP/VNC/SSH satu aplikasi.", "RDP/VNC/SSH in one app."), ("freerdp", 85, "Klien RDP bebas.", "Free RDP client.")]),
    ("Discord", "communication-chat", [("discord", 100, "Klien resmi.", "Official client.")]),
    ("Slack", "communication-chat", [("slack-desktop", 100, "Klien resmi.", "Official client.")]),
    ("Zoom", "communication-chat", [("zoom", 100, "Klien resmi.", "Official client.")]),
    ("Skype", "communication-chat", [("signal-desktop", 60, "Skype pensiun; Signal untuk panggilan.", "Skype retired; Signal for calls."), ("telegram-desktop", 60, "Panggilan dan pesan.", "Calls and messages.")]),
    ("WhatsApp", "communication-chat", [("signal-desktop", 70, "Enkripsi ujung-ke-ujung.", "End-to-end encryption."), ("telegram-desktop", 75, "Fitur mirip WA.", "WA-like features.")]),
    ("KeePass", "security-privacy", [("keepassxc", 100, "Kompatibel database KeePass.", "KeePass database compatible.")]),
    ("Bitwarden", "security-privacy", [("bitwarden", 100, "Aplikasi yang sama di Linux.", "Same app on Linux.")]),
    ("NordVPN", "security-privacy", [("mullvad-vpn", 70, "VPN resmi dengan GUI.", "Official VPN with GUI.")]),
    ("CCleaner", "system-utilities", [("bleachbit", 80, "Pembersih sistem open-source.", "Open-source system cleaner.")]),
    ("Task Manager", "system-utilities", [("mission-center", 90, "Monitor modern mirip Task Manager.", "Modern Task-Manager-like monitor.")]),
    ("MySQL Workbench", "database", [("mysql-workbench", 100, "Aplikasi yang sama di Linux.", "Same app on Linux."), ("dbeaver", 90, "Universal multi-database.", "Universal multi-database tool.")]),
    ("VMware Workstation", "virtualization", [("virtualbox", 85, "Virtualisasi desktop gratis.", "Free desktop virtualization."), ("qemu-desktop", 80, "Performa KVM penuh.", "Full KVM performance.")]),
    ("VirtualBox", "virtualization", [("virtualbox", 100, "Aplikasi yang sama di Linux.", "Same app on Linux.")]),
    ("Docker Desktop", "virtualization", [("docker", 95, "Docker engine native lebih ringan.", "Native Docker engine, lighter.")]),
    ("Windows Terminal", "terminal-shell", [("alacritty", 90, "GPU-accelerated minimalis.", "Minimal GPU-accelerated."), ("kitty", 90, "Fitur kaya dan cepat.", "Feature-rich and fast."), ("konsole", 85, "Terminal bawaan KDE.", "Default KDE terminal.")]),
    ("PuTTY", "terminal-shell", [("putty", 100, "Aplikasi yang sama di Linux.", "Same app on Linux."), ("remmina", 85, "SSH + RDP sekaligus.", "SSH plus RDP together.")]),
    ("Wireshark", "networking", [("wireshark-qt", 100, "Aplikasi yang sama di Linux.", "Same app on Linux.")]),
    ("Dropbox", "cloud-sync", [("dropbox", 100, "Klien resmi.", "Official client.")]),
    ("Google Drive", "cloud-sync", [("rclone", 75, "Sinkronisasi CLI multicloud.", "Multicloud CLI sync."), ("nextcloud-client", 60, "Jika pindah ke Nextcloud.", "If moving to Nextcloud.")]),
    ("OneDrive", "cloud-sync", [("onedrive-abraunegg", 80, "Klien OneDrive populer.", "Popular OneDrive client.")]),
    ("AutoCAD", "cad-3d-modeling", [("freecad", 70, "CAD parametrik open-source.", "Open-source parametric CAD.")]),
    ("SolidWorks", "cad-3d-modeling", [("freecad", 65, "Untuk hobi dan edukasi.", "For hobby and education.")]),
    ("Blender", "cad-3d-modeling", [("blender", 100, "Aplikasi yang sama di Linux.", "Same app on Linux.")]),
    ("MATLAB", "scientific-math", [("octave", 80, "Kompatibel sintaks MATLAB.", "MATLAB-syntax compatible.")]),
]


class Command(BaseCommand):
    help = "Seed WindowsApp + Alternative kurasi (ID/EN)"

    def handle(self, *args, **opts):
        clf = PackageClassifier()
        cat_by_slug = {c.slug: c for c in Category.objects.all()}
        n_win = 0
        for cat_en, info in clf.categories.items():
            from django.utils.text import slugify as slugify_
            cat = cat_by_slug.get(slugify_(cat_en))
            for w in info.get("windows_alt", []):
                _, created = WindowsApp.objects.get_or_create(
                    slug=slugify_(w), defaults={"name": w, "category": cat})
                n_win += created

        apps = {a.slug: a for a in App.objects.all().only("id", "slug")}
        wins = {w.slug: w for w in WindowsApp.objects.all()}
        n_alt, skipped = 0, []
        for wname, cslug, alts in CURATED:
            w = wins.get(slugify(wname))
            if not w:
                skipped.append((wname, "-", "windowsapp hilang"))
                continue
            for aslug, compat, nid, nen in alts:
                a = apps.get(aslug)
                if not a:
                    skipped.append((wname, aslug, "app hilang"))
                    continue
                pkgs = a.packages.all().only("source", "name")
                inst = {"install_cachyos": "", "install_aur": "", "install_flathub": ""}
                for p in pkgs:
                    if p.source == "cachyos" and not inst["install_cachyos"]:
                        inst["install_cachyos"] = f"sudo pacman -S {p.name}"
                    elif p.source == "aur" and not inst["install_aur"]:
                        inst["install_aur"] = f"yay -S {p.name}"
                    elif p.source == "flathub" and not inst["install_flathub"]:
                        inst["install_flathub"] = f"flatpak install {p.name}"
                _, created = Alternative.objects.update_or_create(
                    windows_app=w, app=a,
                    defaults={"compatibility": compat, "notes_id": nid, "notes_en": nen, **inst})
                n_alt += created

        self.stdout.write(self.style.SUCCESS(
            f"selesai: {WindowsApp.objects.count()} windows app (+{n_win}), "
            f"{Alternative.objects.count()} alternative (+{n_alt})"))
        if skipped:
            self.stdout.write(f"terlewat {len(skipped)}:")
            for s in skipped[:20]:
                self.stdout.write(f"  - {s[0]} -> {s[1]} ({s[2]})")
