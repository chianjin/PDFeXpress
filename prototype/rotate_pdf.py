from pathlib import Path

from pikepdf import Pdf


def rotate_pdf(input_file: Path, output_file: Path, rotation_angle: int):
    """Rotates all pages in a PDF by a given angle."""
    with Pdf.open(input_file) as pdf:
        for page in pdf.pages:
            page.rotate(rotation_angle, relative=True)

        pdf.save(output_file)

    print(f"Successfully rotated {input_file} by {rotation_angle}° and saved to {output_file}")


if __name__ == "__main__":
    input_path = Path(r"C:\Users\Chian\Desktop\input.pdf")
    output_path = Path(r"C:\Users\Chian\Desktop\rotated.pdf")

    rotate_pdf(input_path, output_path, rotation_angle=90)
