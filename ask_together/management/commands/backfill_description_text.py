from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup

from ask_together.models import Question


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html or "", "html.parser")
    return soup.get_text(separator=" ", strip=True)


class Command(BaseCommand):
    help = "Backfill description_text from description HTML"

    def handle(self, *args, **options):
        qs = Question.objects.filter(description_text__isnull=True)

        total = qs.count()
        self.stdout.write(f"Found {total} questions to update")

        for i, q in enumerate(qs.iterator(chunk_size=100), start=1):
            q.description_text = html_to_text(q.description)
            q.save(update_fields=["description_text"])

            if i % 100 == 0:
                self.stdout.write(f"Updated {i}/{total}")

        self.stdout.write(self.style.SUCCESS("Backfill completed"))
