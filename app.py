from flask import Flask, request, send_file, render_template
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import tempfile
import os

app = Flask(__name__)

def epub_to_pdf(epub_path, pdf_path):
    book = epub.read_epub(epub_path)
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(pdf_path)
    story = []

    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), "html.parser")
            for paragraph in soup.find_all(['p', 'h1', 'h2', 'h3']):
                text = paragraph.get_text().strip()
                if text:
                    story.append(Paragraph(text, styles["Normal"]))
                    story.append(Spacer(1, 12))

    doc.build(story)

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        if file and file.filename.endswith(".epub"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".epub") as tmp_epub:
                file.save(tmp_epub.name)
                pdf_path = tmp_epub.name.replace(".epub", ".pdf")
                epub_to_pdf(tmp_epub.name, pdf_path)
                return send_file(pdf_path, as_attachment=True, download_name="converted.pdf")
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
