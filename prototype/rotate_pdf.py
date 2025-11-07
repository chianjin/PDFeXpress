from pikepdf import Pdf
from pathlib import Path


def rotate_pdf(input_file, output_file, rotation_angle):
    """
    Rotate all pages in a PDF file by a given angle.
    
    Args:
        input_file: Path to the input PDF file
        output_file: Path to save the rotated PDF file
        rotation_angle: Angle to rotate the pages (in degrees, typically 90, 180, or 270)
    """
    with Pdf.open(input_file) as pdf:
        for page in pdf.pages:
            # Use relative rotation to add the rotation angle to the current rotation
            page.rotate(rotation_angle, relative=True)

        pdf.save(output_file)

    print(f"Successfully rotated {input_file} by {rotation_angle}° and saved to {output_file}")


if __name__ == "__main__":
    # Example usage
    input_file = Path(r"C:\Users\Chian\Desktop\input.pdf")
    output_file = Path(r"C:\Users\Chian\Desktop\rotated.pdf")
    
    rotate_pdf(input_file, output_file, rotation_angle=90)