from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from main_app.models import PG
import random
from pathlib import Path

DEFAULT_IMAGE_URLS = [
    # Replace these with your own; or pass --url-file path/to/urls.txt
    "https://images.unsplash.com/photo-1501183638710-841dd1904471",
    "https://images.unsplash.com/photo-1523217582562-09d0def993a6",
    "https://images.unsplash.com/photo-1505692794403-34d4982ae6b4",
    "https://images.unsplash.com/photo-1501045661006-fcebe0257c3f",
    "https://images.unsplash.com/photo-1494526585095-c41746248156",
    "https://images.unsplash.com/photo-1433838552652-f9a46b332c40",
    "https://images.unsplash.com/photo-1494526585095-00b4ae3f12d3",
    "https://images.unsplash.com/photo-1479839672679-a46483c0e7c8",
    "https://images.unsplash.com/photo-1484154218962-a197022b5858",
    "https://images.unsplash.com/photo-1460317442991-0ec209397118",
]

class Command(BaseCommand):
    help = (
        "Assign random image URLs to PGs that don't have an image. "
        "Uses image_url field; won't overwrite existing image_file or image_url."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--url-file",
            dest="url_file",
            help="Path to a file containing one image URL per line.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Maximum number of PGs to update (useful for testing).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Don't save changes; just show what would be updated.",
        )
        parser.add_argument(
            "--shuffle",
            action="store_true",
            help="Shuffle URL list before assigning (default: true)",
        )

    def handle(self, *args, **options):
        url_file = options.get("url_file")
        limit = options.get("limit")
        dry_run = options.get("dry_run")
        shuffle = options.get("shuffle", True)

        urls = self._load_urls(url_file)
        if not urls:
            raise CommandError("No image URLs available. Provide --url-file or edit DEFAULT_IMAGE_URLS.")

        if shuffle:
            random.shuffle(urls)

        qs = PG.objects.filter(
            Q(image_file__isnull=True),
            Q(image_url__isnull=True) | Q(image_url="")
        ).order_by("id")

        if limit:
            qs = qs[:limit]

        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.WARNING("No PGs need images (all have image_url/image_file)."))
            return

        updated = 0
        for i, pg in enumerate(qs):
            url = urls[i % len(urls)]
            if dry_run:
                self.stdout.write(f"Would set PG id={pg.id} '{pg.title}' -> {url}")
            else:
                pg.image_url = url
                pg.save(update_fields=["image_url"])
                updated += 1
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"Dry-run complete. {total} PGs would be updated."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Assigned images to {updated} PGs"))

    def _load_urls(self, url_file):
        if not url_file:
            return [u.strip() for u in DEFAULT_IMAGE_URLS if u.strip()]
        p = Path(url_file)
        if not p.exists():
            raise CommandError(f"URL file not found: {url_file}")
        urls = []
        with p.open("r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if s and not s.startswith("#"):
                    urls.append(s)
        return urls
