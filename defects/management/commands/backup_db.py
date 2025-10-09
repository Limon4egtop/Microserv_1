from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
import shutil, datetime
class Command(BaseCommand):
    help = "Простой бэкап SQLite-базы в папку backups/"
    def handle(self, *args, **kwargs):
        db_path = Path(settings.DATABASES["default"]["NAME"])
        if not db_path.exists():
            self.stderr.write("Файл базы данных не найден."); return
        dest_dir = Path(settings.BASE_DIR)/"backups"; dest_dir.mkdir(exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = dest_dir / f"db_{ts}.sqlite3"; shutil.copy2(db_path, dest)
        self.stdout.write(self.style.SUCCESS(f"Бэкап выполнен: {dest}"))
