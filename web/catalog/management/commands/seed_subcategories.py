"""Taksonomi subkategori: (slug, name_en, name_id, [keywords])."""
from django.core.management.base import BaseCommand
from catalog.models import Category, SubCategory

TAXONOMY = {
"web-browser": [
    ("chromium-based", "Chromium-based", "Berbasis Chromium", ["chrome", "chromium", "brave", "edge", "opera", "vivaldi"]),
    ("firefox-based", "Firefox-based", "Berbasis Firefox", ["firefox", "librewolf", "waterfox", "tor browser", "mullvad browser"]),
    ("lightweight", "Lightweight", "Ringan", ["falkon", "qutebrowser", "nyxt", "luakit", "dillo", "links", "lynx", "netsurf", "badwolf"]),
],
"office-productivity": [
    ("office-suites", "Office Suites", "Paket Office", ["libreoffice", "onlyoffice", "wps", "calligra"]),
    ("pdf-tools", "PDF Tools", "Perkakas PDF", ["pdf", "okular", "evince", "mupdf", "zathura", "xournal", "masterpdf"]),
    ("notes", "Notes", "Catatan", ["joplin", "obsidian", "logseq", "xournalpp", "cherrytree", "zim", "tutanota", "standardnotes"]),
    ("document-tools", "Document Tools", "Perkakas Dokumen", ["calibre", "pandoc", "tex", "dict", "translate"]),
],
"media-player-video": [
    ("players", "Players", "Pemutar", ["vlc", "mpv", "celluloid", "haruna", "parole", "totem", "dragonplayer", "smplayer"]),
    ("streaming", "Streaming & TV", "Streaming & TV", ["kodi", "plex", "stremio", "jellyfin", "hypnotix"]),
    ("video-tools", "Video Tools", "Perkakas Video", ["ffmpeg", "handbrake", "mkvtoolnix", "avidemux", "subtitle", "yt-dlp", "parabolic", "clapper"]),
],
"audio-music": [
    ("players", "Players", "Pemutar", ["spotify", "lollypop", "audacious", "deadbeef", "clementine", "strawberry", "elisa", "amberol", "rhythmbox", "tauon", "cantata", "mpd", "ncmpcpp"]),
    ("editors", "Editors & DAW", "Editor & DAW", ["audacity", "ardour", "lmms", "reaper", "rosegarden", "qtractor", "zrythm", "ocenaudio", "tenacity", "mixxx"]),
    ("audio-system", "Audio System", "Sistem Audio", ["pulseaudio", "pipewire", "pavucontrol", "alsa", "jack", "easyeffects", "helvum", "qpwgraph"]),
],
"graphics-image-editing": [
    ("raster", "Raster Editors", "Editor Raster", ["gimp", "krita", "pinta", "mypaint", "photoflare", "pixelitor", "azpainter"]),
    ("vector", "Vector", "Vektor", ["inkscape", "sodipodi", "libreoffice-draw"]),
    ("viewers", "Viewers & Managers", "Penampil & Manajer", ["gwenview", "eog", "shotwell", "digikam", "loupe", "nomacs", "ristretto", "pix", "gthumb"]),
    ("screenshot", "Screenshot", "Tangkapan Layar", ["flameshot", "spectacle", "gnome-screenshot", "grim", "slurp", "shutter"]),
],
"video-editing": [
    ("editors", "Editors", "Editor", ["kdenlive", "shotcut", "openshot", "flowblade", "pitivi", "olive", "vidcutter", "losslesscut"]),
    ("professional", "Professional", "Profesional", ["davinci-resolve", "davinci", "lightworks"]),
    ("screen-recording", "Screen Recording", "Rekam Layar", ["obs-studio", "obs", "simplescreenrecorder", "vokoscreen", "peek", "kooha", "gpu-screen-recorder"]),
],
"development-tools": [
    ("ides", "IDEs", "IDE", ["vscode", "vscodium", "code", "eclipse", "qtcreator", "geany", "kdevelop", "anjuta", "codeblocks", "clion", "android-studio"]),
    ("compilers", "Compilers & Runtimes", "Kompiler & Runtime", ["gcc", "clang", "llvm", "rust", "go", "jdk", "openjdk", "python", "nodejs", "deno", "bun", "perl", "ruby", "mono", "dotnet"]),
    ("version-control", "Version Control", "Kontrol Versi", ["gitkraken", "lazygit", "gitg", "git-cola", "sublime-merge", "tig", "mercurial", "svn", "gitahead", "gitui", "gitify"]),
    ("build-tools", "Build Tools", "Perkakas Build", ["cmake", "make", "meson", "ninja", "maven", "gradle", "cargo", "npm", "yarn", "pnpm", "pip", "poetry"]),
],
"text-editor-ide": [
    ("terminal-editors", "Terminal Editors", "Editor Terminal", ["vim", "neovim", "emacs", "nano", "micro", "kakoune", "helix", "joe", "jed"]),
    ("gui-editors", "GUI Editors", "Editor GUI", ["kate", "gedit", "mousepad", "notepadqq", "xed", "pluma", "leafpad", "featherpad", "gnome-text", "sublime"]),
],
"gaming": [
    ("launchers", "Launchers", "Launcher", ["steam", "lutris", "heroic", "bottles", "playonlinux", "minigalaxy", "gamehub"]),
    ("compatibility", "Compatibility", "Kompatibilitas", ["wine", "proton", "protontricks", "protonup", "dxvk", "vkd3d"]),
    ("emulators", "Emulators", "Emulator", ["retroarch", "dolphin-emu", "dolphin", "pcsx2", "rpcs3", "ppsspp", "yuzu", "ryujinx", "cemu", "duckstation", "mupen", "dosbox", "scummvm"]),
    ("gaming-tools", "Gaming Tools", "Perkakas Gim", ["gamemode", "mangohud", "goverlay", "gamescope", "discord", "teamspeak", "mumble"]),
],
"email-client": [
    ("desktop", "Desktop", "Desktop", ["thunderbird", "evolution", "kmail", "claws", "sylpheed", "betterbird", "blue-mail", "mailspring", "tutanota"]),
    ("terminal", "Terminal", "Terminal", ["mutt", "neomutt", "alpine", "aerc", "himalaya"]),
],
"file-manager": [
    ("gui", "GUI", "GUI", ["dolphin", "nautilus", "nemo", "thunar", "pcmanfm", "krusader", "doublecmd", "konqueror", "caja", "spacefm", "sunflower"]),
    ("terminal", "Terminal", "Terminal", ["ranger", "nnn", "midnight-commander", "mc", "lf", "yazi", "vifm", "joshuto"]),
],
"archive-compression": [
    ("gui", "GUI", "GUI", ["ark", "file-roller", "peazip", "xarchiver", "engrampa"]),
    ("cli", "CLI", "CLI", ["7zip", "p7zip", "unrar", "unzip", "zip", "tar", "atool", "dtrx"]),
],
"download-manager": [
    ("torrent", "Torrent", "Torrent", ["qbittorrent", "transmission", "deluge", "ktorrent", "tixati", "fragments", "torrent"]),
    ("direct", "Direct & Tools", "Langsung & Perkakas", ["aria2", "wget", "curl", "persepolis", "uget", "kget", "motrix", "free-download"]),
],
"remote-desktop-vnc": [
    ("clients", "Clients", "Klien", ["remmina", "teamviewer", "anydesk", "rustdesk", "vinagre", "krdc", "thincast", "nomachine"]),
    ("servers-protocols", "Servers & Protocols", "Server & Protokol", ["tigervnc", "x11vnc", "freerdp", "xrdp", "wayvnc", "krfb", "vnc", "rdp"]),
],
"communication-chat": [
    ("messaging", "Messaging", "Pesan", ["discord", "telegram", "signal", "whatsapp", "slack", "element", "nheko", "gajim", "dino", "hexchat", "weechat", "mattermost", " Zulip".strip(), "rambox", "ferdium", "teams-for-linux"]),
    ("video-calls", "Video Calls", "Panggilan Video", ["zoom", "teams", "skype", "jitsi", "linphone", "jami", "webex", "gotomeeting"]),
],
"security-privacy": [
    ("vpn", "VPN", "VPN", ["mullvad", "nordvpn", "openvpn", "wireguard", "protonvpn", "windscribe", "ivpn", "riseup", "tailscale", "zerotier"]),
    ("passwords", "Password Managers", "Manajer Kata Sandi", ["keepassxc", "keepass", "bitwarden", "1password", "enpass", "gnome-password", "pass", "gopass"]),
    ("encryption", "Encryption", "Enkripsi", ["gpg", "gnupg", "veracrypt", "cryptsetup", "luks", "age", "seahorse", "kleopatra"]),
    ("antivirus", "Antivirus", "Antivirus", ["clamav", "clamtk", "sophos"]),
],
"system-utilities": [
    ("monitoring", "Monitoring", "Monitor", ["htop", "btop", "mission-center", "gnome-system-monitor", "mate-system-monitor", "xfce4-taskmanager", "lxtask", "nvtop", "glances", "bpytop", "gotop"]),
    ("disks", "Disks", "Diska", ["gparted", "baobab", "ncdu", "dust", "gnome-disks", "kde-partitionmanager", "qdirstat", "filelight", "duc"]),
    ("cleaning", "Cleaning", "Pembersih", ["bleachbit", "stacer", "sweeper", "fslint", "czkawka"]),
    ("sysinfo", "System Info", "Info Sistem", ["neofetch", "fastfetch", "screenfetch", "inxi", "hardinfo", "cpuid", "lshw", "dmidecode"]),
],
"database": [
    ("servers", "Servers", "Server", ["mysql", "mariadb", "postgresql", "postgres", "sqlite", "mongodb", "redis", "cockroach", "cassandra", "influxdb", "couchdb", "firebird"]),
    ("gui-tools", "GUI Tools", "Perkakas GUI", ["dbeaver", "mysql-workbench", "pgadmin", "beekeeper", "datagrip", "sequel", "heidisql", "mongodb-compass", "redisinsight", "antares", "dbgate"]),
],
"virtualization": [
    ("desktop-vms", "Desktop VMs", "VM Desktop", ["virtualbox", "virt-manager", "gnome-boxes", "qemu", "vmware", "kvm", "looking-glass"]),
    ("containers", "Containers", "Kontainer", ["docker", "podman", "distrobox", "lxc", "incus", "toolbox", "buildah", "rancher", "k3s", "minikube", "kind"]),
],
"terminal-shell": [
    ("terminals", "Terminals", "Terminal", ["alacritty", "kitty", "konsole", "gnome-terminal", "wezterm", "foot", "terminator", "tilix", "guake", "yakuake", "tilda", "xterm", "rxvt", "st", "blackbox", "ptyxis", "xfce4-terminal", "mate-terminal", "lxterminal", "qterminal", "cool-retro"]),
    ("shells", "Shells & Multiplexers", "Shell & Multiplekser", ["bash", "zsh", "fish", "nushell", "elvish", "starship", "tmux", "screen", "zellij", "byobu", "powerline", "oh-my-posh"]),
],
"desktop-environment": [
    ("desktops", "Desktops", "Desktop", ["plasma", "gnome", "xfce4", "xfce", "lxqt", "lxde", "mate", "cinnamon", "budgie", "pantheon", "deepin", "ukui", "enlightenment", "cosmic"]),
    ("window-managers", "Window Managers", "Manajer Jendela", ["i3", "sway", "hyprland", "awesome", "bspwm", "dwm", "qtile", "xmonad", "openbox", "fluxbox", "icewm", "jwm", "spectrwm", "herbstluftwm", "leftwm", "river"]),
    ("login-display", "Login & Display", "Login & Tampilan", ["sddm", "gdm", "lightdm", "lxdm", "ly", "greetd", "xorg", "wayland", "arandr", "wdisplays", "kanshi"]),
],
"libraries-dependencies": [
    ("system-libs", "System Libs", "Pustaka Sistem", ["glibc", "gcc-libs", "libstdc", "zlib", "openssl", "libffi", "expat", "pcre", "libx11", "mesa-lib", "systemd-libs", "util-linux-libs"]),
    ("python-libs", "Python Libs", "Pustaka Python", ["python-", "python2", "python3"]),
    ("multimedia-libs", "Multimedia Libs", "Pustaka Multimedia", ["ffmpeg", "gstreamer", "sdl", "alsa-lib", "pulseaudio", "pipewire", "libvpx", "x264", "x265", "opus", "flac", "libvorbis", "libpng", "libjpeg", "freetype", "harfbuzz"]),
    ("gui-libs", "GUI Libs", "Pustaka GUI", ["gtk", "qt5", "qt6", "wxwidgets", "fltk", "tk", "cairo", "pango", "at-spi", "libadwaita", "kirigami"]),
],
"networking": [
    ("analysis", "Analysis", "Analisis", ["wireshark", "nmap", "tcpdump", "tshark", "ettercap", "kismet", "aircrack", "mtr", "traceroute", "ping", "netstat", "ss", "iftop", "nethogs", "jnettop", "wireshark-qt"]),
    ("remote-access", "Remote Access", "Akses Jauh", ["openssh", "ssh", "putty", "mosh", "telnet", "netcat", "socat", "proxychains", "tor", "torsocks"]),
    ("wifi", "WiFi & Connection", "WiFi & Koneksi", ["networkmanager", "iwd", "iw", "wpa_supplicant", "wicd", "connman", "wavemon", "nm-connection"]),
],
"web-development": [
    ("servers", "Servers", "Server", ["apache", "nginx", "caddy", "lighttpd", "tomcat", "gunicorn", "uwsgi"]),
    ("languages", "Languages", "Bahasa", ["php", "node", "composer", "python", "ruby", "perl"]),
    ("cms-tools", "CMS & Tools", "CMS & Perkakas", ["wordpress", "drupal", "joomla", "postman", "insomnia", "filezilla", "mariadb", "adminer", "jekyll", "hugo"]),
],
"cloud-sync": [
    ("clients", "Clients", "Klien", ["dropbox", "nextcloud-client", "nextcloud", "syncthing", "rclone", "onedrive", "insync", "megasync", "pcloud", "seafile", "owncloud", "gdrive", "s3cmd", "restic", "duplicity", "deja-dup", "backintime", "timeshift", "grsync"]),
],
"cad-3d-modeling": [
    ("cad", "CAD", "CAD", ["freecad", "librecad", "openscad", "qcad", "solvespace", "cad"]),
    ("3d-printing", "3D Printing", "Cetak 3D", ["cura", "prusa-slicer", "prusa", "orca-slicer", "orca", "slic3r", "superslicer", "bambu"]),
],
"scientific-math": [
    ("math", "Math", "Matematika", ["octave", "maxima", "scilab", "sage", "r", "r-studio", "rstudio", "julia", "numpy", "scipy", "sympy", "bc", "qalculate", "speedcrunch", "galculator", "gnome-calculator", "kcalc"]),
    ("latex", "LaTeX", "LaTeX", ["texlive", "texstudio", "texmaker", "texworks", "lyx", "kile", "latex", "biber", "bibtex", "auctex"]),
    ("plotting", "Plotting", "Plot", ["gnuplot", "matplotlib", "veusz", "labplot", "paraview", "visit"]),
],
"fonts-typography": [
    ("fonts", "Fonts", "Fonta", ["ttf-", "otf-", "noto", "liberation", "dejavu", "fira", "jetbrains-mono", "hack", "cantarell", "inter-", "roboto-", "ubuntu-", "adobe-source", "font-", "gsfonts", "wqy", "terminus-font"]),
    ("font-tools", "Font Tools", "Perkakas Fonta", ["fontconfig", "font-manager", "gnome-font", "fontforge", "birdfont"]),
],
"printing-scanning": [
    ("printing", "Printing", "Cetak", ["cups", "hplip", "printer", "print", "gutenprint", "foomatic", "system-config-printer"]),
    ("scanning", "Scanning", "Pindai", ["sane", "scan", "simple-scan", "skanpage", "skanlite", "xsane", "vuescan", "gscan2pdf"]),
],
}


class Command(BaseCommand):
    help = "Seed subkategori + rules keyword per kategori"

    def handle(self, *args, **opts):
        cats = {c.slug: c for c in Category.objects.all()}
        n_sub = 0
        for cslug, subs in TAXONOMY.items():
            cat = cats.get(cslug)
            if not cat:
                self.stderr.write(f"kategori hilang: {cslug}")
                continue
            for i, (slug, en, id_, kws) in enumerate(subs):
                _, created = SubCategory.objects.update_or_create(
                    slug=f"{cslug}--{slug}",
                    defaults={"category": cat, "name_en": en, "name_id": id_,
                              "keywords": ",".join(kws), "priority": i})
                n_sub += created
            # penampung Other per kategori
            SubCategory.objects.get_or_create(
                slug=f"{cslug}--other",
                defaults={"category": cat, "name_en": "Other", "name_id": "Lainnya",
                          "keywords": "", "priority": 99})
        self.stdout.write(self.style.SUCCESS(
            f"selesai: {SubCategory.objects.count()} subkategori"))
