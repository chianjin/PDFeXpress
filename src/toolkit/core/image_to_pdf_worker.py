# toolkit/core/image_to_pdf_worker.py

from pathlib import Path
from PIL import Image

from toolkit.i18n import gettext_text as _, ngettext


def image_to_pdf_worker(
    image_files,
    output_pdf_path,
    cancel_event,
    progress_queue,
    result_queue,
    saving_ack_event,
):
    try:
        total_steps = len(image_files)
        progress_queue.put(("INIT", total_steps))

        images = []
        for i, image_file in enumerate(image_files):
            if cancel_event.is_set():
                result_queue.put(("CANCEL", _("Cancelled by user.")))
                return

            if not Path(image_file).exists():
                progress_queue.put(("PROGRESS", i + 1))
                continue

            try:
                img = Image.open(image_file)
                if img.mode == 'RGBA':
                    # 如果图像是 RGBA 模式，转换为 RGB (PDF 不支持透明度)
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split(3))  # 3 是 alpha 通道
                    images.append(rgb_img)
                else:
                    images.append(img.convert('RGB'))
            except Exception as img_e:
                print(f"Error converting image {image_file}: {img_e}")
                result_queue.put(
                    (
                        "ERROR",
                        _("Error converting image {}:\n{}").format(
                            Path(image_file).name, img_e
                        ),
                    )
                )
                return

            progress_queue.put(("PROGRESS", i + 1))

        if not images:
            raise ValueError(_("No image converted to PDF."))

        progress_queue.put(("SAVING", _("Saving PDF...")))
        # Wait for UI thread to confirm SAVING message processed,
        # while periodically checking the cancel event.
        while not saving_ack_event.is_set():
            if cancel_event.is_set():
                result_queue.put(("CANCEL", _("Cancelled by user.")))
                return
            # Wait briefly, then check the cancel event again
            saving_ack_event.wait(timeout=0.1)

        # 保存第一张图片，如果有多张则后续图片作为 append_images 参数附加
        first_img = images[0]
        remaining_images = images[1:]
        first_img.save(output_pdf_path, "PDF", resolution=100.0, save_all=True, append_images=remaining_images)

        success_msg = ngettext(
            "Converted {} image into PDF.", "Converted {} images into PDF.", total_steps
        ).format(total_steps)
        result_queue.put(("SUCCESS", success_msg))

    except Exception as e:
        result_queue.put(("ERROR", _("Unexpected error occurred. {}").format(e)))
