"""Camera device implementation."""

import threading
import time

from PIL import Image, ImageDraw, ImageFont

from .interface_camera import InterfaceCamera


class DeviceCamera(threading.Thread, InterfaceCamera):
    """Camera device that provides pan, zoom, and view capabilities.

    The camera runs in a separate thread and updates its internal time counter.
    """

    RETURN_SIZE = 500
    SOURCE_SIZE = 200

    def __init__(self):
        """Initialize the camera device."""
        super().__init__(daemon=True)

        self.camera_id = 0
        self.time = 0
        self.pan = 0
        self.zoom = 2
        self.img_source = None
        self.center_width = 0
        self.center_height = 0
        self._running = True
        self._lock = threading.Lock()
        # Font was previously missing; using a default PIL font prevents
        # AttributeError in getView
        self.font = ImageFont.load_default()

        self.start()

    def set_id(self, id_):
        """Set the camera ID and load associated image (synchronized).

        Args:
            id_: The camera identifier.
        """
        with self._lock:
            self.camera_id = id_
            file_name = f"camera{id_}.jpg"

            try:
                self.img_source = Image.open(file_name)
                self.center_width = self.img_source.width // 2
                self.center_height = self.img_source.height // 2
            except FileNotFoundError:
                self.img_source = None
                print(f"ERROR: {file_name} file open error")
                return

    def get_id(self):
        """Get the camera ID.

        Returns:
            int: The camera identifier.
        """
        return self.camera_id

    def get_view(self):
        """Get the current camera view as a PIL Image (synchronized).

        Returns:
            PIL.Image: The current camera view image.
        """
        with self._lock:
            view = "Time = "
            if self.time < 10:
                view += "0"
            view += f"{self.time}, zoom x{self.zoom}, "

            if self.pan > 0:
                view += f"right {self.pan}"
            elif self.pan == 0:
                view += "center"
            else:
                view += f"left {-self.pan}"

            # Create the view image (500x500)
            img_view = Image.new("RGB", (self.RETURN_SIZE, self.RETURN_SIZE), "black")

            if self.img_source is not None:
                zoomed = self.SOURCE_SIZE * (10 - self.zoom) // 10
                panned = self.pan * self.SOURCE_SIZE // 5

                left = self.center_width + panned - zoomed
                top = self.center_height - zoomed
                right = self.center_width + panned + zoomed
                bottom = self.center_height + zoomed

                # Crop and resize to fill the view
                try:
                    cropped = self.img_source.crop((left, top, right, bottom))
                    resized = cropped.resize(
                        (self.RETURN_SIZE, self.RETURN_SIZE), Image.LANCZOS
                    )
                    img_view.paste(resized, (0, 0))
                except Exception:
                    # If crop fails, keep black background
                    pass

            draw = ImageDraw.Draw(img_view)

            # Get text size
            bbox = draw.textbbox((0, 0), view, font=self.font)
            w_text = bbox[2] - bbox[0]
            h_text = bbox[3] - bbox[1]

            # Draw rounded rectangle background (gray)
            r_x = 0
            r_y = 0
            draw.rounded_rectangle(
                [(r_x, r_y), (r_x + w_text + 10, r_y + h_text + 5)],
                radius=h_text // 2,
                fill="gray",
            )

            # Draw text (cyan)
            x_text = r_x + 5
            y_text = r_y + 2
            draw.text((x_text, y_text), view, fill="cyan", font=self.font)

            return img_view

    def pan_right(self):
        """Pan camera to the right (synchronized).

        Returns:
            bool: True if pan was successful, False if at maximum.
        """
        with self._lock:
            self.pan += 1
            if self.pan > 5:
                self.pan = 5
                return False
            return True

    def pan_left(self):
        """Pan camera to the left (synchronized).

        Returns:
            bool: True if pan was successful, False if at minimum.
        """
        with self._lock:
            self.pan -= 1
            if self.pan < -5:
                self.pan += 1
                return False
            return True

    def zoom_in(self):
        """Zoom in (synchronized).

        Returns:
            bool: True if zoom was successful, False if at maximum.
        """
        with self._lock:
            self.zoom += 1
            if self.zoom > 9:
                self.zoom -= 1
                return False
            return True

    def zoom_out(self):
        """Zoom out (synchronized).

        Returns:
            bool: True if zoom was successful, False if at minimum.
        """
        with self._lock:
            self.zoom -= 1
            if self.zoom < 1:
                self.zoom += 1
                return False
            return True

    def _tick(self):
        """Increment time counter (synchronized, private)."""
        with self._lock:
            self.time += 1
            if self.time >= 100:
                self.time = 0

    def run(self):
        """Thread run method - updates time every second."""
        while self._running:
            try:
                time.sleep(1.0)
            except InterruptedError:
                pass
            self._tick()

    def stop(self):
        """Stop the camera thread."""
        self._running = False
