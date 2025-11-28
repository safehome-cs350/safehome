"""Surveillance panel for camera management."""

import base64
import io
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk

from PIL import Image, ImageTk

from .api_client import APIClient


class SurveillancePanel(ttk.Frame):
    """Panel for surveillance camera management."""

    def __init__(self, parent, app):
        """Initialize the surveillance panel."""
        super().__init__(parent)
        self.app = app
        self.api_client = APIClient()

        self.project_root = Path(__file__).parent.parent.resolve()

        self.cameras = {}
        self.current_camera = None
        self.current_pan = 0
        self.current_zoom = 2

        self.setup_ui()
        self.load_cameras()

    def setup_ui(self):
        """Set up the user interface."""
        left_frame = ttk.LabelFrame(self, text="Cameras", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5, ipadx=5)

        camera_list_frame = ttk.Frame(left_frame)
        camera_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.camera_tree = ttk.Treeview(
            camera_list_frame,
            columns=("name", "status", "password"),
            show="headings",
            height=10,
        )
        self.camera_tree.heading("name", text="Camera")
        self.camera_tree.heading("status", text="Status")
        self.camera_tree.heading("password", text="Password")

        self.camera_tree.column("name", width=150)
        self.camera_tree.column("status", width=80)
        self.camera_tree.column("password", width=100)

        scrollbar_cameras = ttk.Scrollbar(
            camera_list_frame,
            orient=tk.VERTICAL,
            command=self.camera_tree.yview,
        )
        self.camera_tree.configure(yscrollcommand=scrollbar_cameras.set)

        self.camera_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_cameras.pack(side=tk.RIGHT, fill=tk.Y)

        self.camera_tree.bind("<<TreeviewSelect>>", self.on_camera_select)

        control_frame = ttk.LabelFrame(left_frame, text="Camera Controls", padding=10)
        control_frame.pack(fill=tk.X, pady=5)

        enable_btn = ttk.Button(
            control_frame,
            text="Enable Camera",
            command=self.enable_camera,
            width=18,
        )
        enable_btn.pack(pady=2)
        disable_btn = ttk.Button(
            control_frame,
            text="Disable Camera",
            command=self.disable_camera,
            width=18,
        )
        disable_btn.pack(pady=2)
        set_pwd_btn = ttk.Button(
            control_frame,
            text="Set Password",
            command=self.set_camera_password,
            width=18,
        )
        set_pwd_btn.pack(pady=2)
        del_pwd_btn = ttk.Button(
            control_frame,
            text="Delete Password",
            command=self.delete_camera_password,
            width=18,
        )
        del_pwd_btn.pack(pady=2)

        refresh_btn = ttk.Button(
            control_frame,
            text="Refresh List",
            command=self.load_cameras,
            width=18,
        )
        refresh_btn.pack(pady=2)

        floor_plan_btn = ttk.Button(
            control_frame,
            text="View Floor Plan",
            command=self.show_floor_plan,
            width=18,
        )
        floor_plan_btn.pack(pady=5)

        thumbnail_btn = ttk.Button(
            control_frame,
            text="View Thumbnails",
            command=self.show_thumbnails,
            width=18,
        )
        thumbnail_btn.pack(pady=2)

        right_frame = ttk.LabelFrame(self, text="Camera View", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        view_frame = ttk.Frame(right_frame)
        view_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.camera_canvas = tk.Canvas(view_frame, bg="black", width=640, height=480)
        self.camera_canvas.pack(fill=tk.BOTH, expand=True)

        self.camera_canvas.create_text(
            320,
            240,
            text="Select a camera to view",
            fill="white",
            font=("Arial", 16),
        )

        # Bind canvas resize to update camera view
        self.camera_canvas.bind("<Configure>", self.on_canvas_resize)

        pan_zoom_frame = ttk.LabelFrame(
            right_frame, text="Pan/Zoom Controls", padding=10
        )
        pan_zoom_frame.pack(fill=tk.X, pady=5)

        zoom_frame = ttk.Frame(pan_zoom_frame)
        zoom_frame.pack(fill=tk.X, pady=5)

        ttk.Label(zoom_frame, text="Zoom:").pack(side=tk.LEFT, padx=5)
        zoom_in_btn = ttk.Button(
            zoom_frame,
            text="Zoom In",
            command=lambda: self.adjust_zoom(1),
            width=10,
        )
        zoom_in_btn.pack(side=tk.LEFT, padx=2)
        zoom_out_btn = ttk.Button(
            zoom_frame,
            text="Zoom Out",
            command=lambda: self.adjust_zoom(-1),
            width=10,
        )
        zoom_out_btn.pack(side=tk.LEFT, padx=2)
        reset_zoom_btn = ttk.Button(
            zoom_frame, text="Reset Zoom", command=self.reset_zoom, width=12
        )
        reset_zoom_btn.pack(side=tk.LEFT, padx=2)

        self.zoom_label = ttk.Label(zoom_frame, text="2")
        self.zoom_label.pack(side=tk.LEFT, padx=10)

        pan_frame = ttk.Frame(pan_zoom_frame)
        pan_frame.pack(fill=tk.X, pady=5)

        ttk.Label(pan_frame, text="Pan:").pack(side=tk.LEFT, padx=5)
        pan_left_btn = ttk.Button(
            pan_frame,
            text="←",
            command=lambda: self.adjust_pan(-1),
            width=5,
        )
        pan_left_btn.pack(side=tk.LEFT, padx=2)
        pan_right_btn = ttk.Button(
            pan_frame, text="→", command=lambda: self.adjust_pan(1), width=5
        )
        pan_right_btn.pack(side=tk.LEFT, padx=2)
        reset_pan_btn = ttk.Button(
            pan_frame, text="Reset Pan", command=self.reset_pan, width=12
        )
        reset_pan_btn.pack(side=tk.LEFT, padx=2)

        self.pan_label = ttk.Label(pan_frame, text="0")
        self.pan_label.pack(side=tk.LEFT, padx=10)

    def on_canvas_resize(self, event):
        """Handle canvas resize event."""
        if self.current_camera:
            self.load_camera_view(self.current_camera)

    def load_cameras(self):
        """Load cameras from the API."""
        try:
            response = self.api_client.list_cameras()
            self.cameras = {}
            for camera in response.get("cameras", []):
                self.cameras[camera["camera_id"]] = {
                    "name": camera["name"],
                    "location": camera["location"],
                    "is_enabled": camera["is_enabled"],
                    "is_online": camera["is_online"],
                    "has_password": camera["has_password"],
                }
            self.refresh_camera_list()
        except Exception as e:
            error_message = str(e)
            if "Connection" in error_message or "refused" in error_message.lower():
                messagebox.showerror(
                    "Error",
                    "Cannot connect to backend server. "
                    "Please ensure the backend is running.",
                )
            else:
                messagebox.showerror(
                    "Error", f"Failed to load cameras: {error_message}"
                )

    def refresh_camera_list(self):
        """Refresh the camera list display."""
        for item in self.camera_tree.get_children():
            self.camera_tree.delete(item)

        for cam_id, camera in sorted(self.cameras.items()):
            status = "Enabled" if camera["is_enabled"] else "Disabled"
            if not camera["is_online"]:
                status = "Offline"
            password_status = "Protected" if camera["has_password"] else "No Password"
            self.camera_tree.insert(
                "",
                tk.END,
                values=(camera["name"], status, password_status),
                tags=(cam_id,),
            )

    def on_camera_select(self, event):
        """Handle camera selection event."""
        selected = self.camera_tree.selection()
        if not selected:
            return

        item = self.camera_tree.item(selected[0])
        cam_id = int(item["tags"][0])

        if cam_id in self.cameras:
            camera = self.cameras[cam_id]

            if camera["has_password"]:
                password = simpledialog.askstring(
                    "Camera Password",
                    f"Enter password for {camera['name']}:",
                    show="*",
                )
                if not password:
                    self.camera_tree.selection_remove(selected[0])
                    return
                # Note: Backend doesn't validate password on view,
                # so we just proceed if password is entered

            if not camera["is_enabled"]:
                messagebox.showinfo(
                    "Camera Disabled", "This camera is currently disabled"
                )
                return

            if not camera["is_online"]:
                messagebox.showwarning(
                    "Camera Offline", "This camera is currently offline"
                )
                return

            self.current_camera = cam_id
            self.load_camera_view(cam_id)

    def load_camera_view(self, cam_id):
        """Load and display the camera view from API."""
        try:
            response = self.api_client.get_camera_view(cam_id)
            camera = self.cameras[cam_id]

            self.current_pan = response.get("pan_position", 0)
            self.current_zoom = response.get("zoom_level", 2)
            self.zoom_label.config(text=str(self.current_zoom))
            self.pan_label.config(text=str(self.current_pan))

            self.camera_canvas.delete("all")

            # Decode base64 image if available
            base64_image = response.get("current_view_base64")
            if base64_image:
                try:
                    image_data = base64.b64decode(base64_image)
                    img = Image.open(io.BytesIO(image_data))
                    # Resize to fit canvas
                    canvas_width = self.camera_canvas.winfo_width()
                    canvas_height = self.camera_canvas.winfo_height()
                    if canvas_width > 1 and canvas_height > 1:
                        img = img.resize(
                            (canvas_width, canvas_height), Image.Resampling.LANCZOS
                        )
                    else:
                        img = img.resize((640, 480), Image.Resampling.LANCZOS)
                    self.camera_image = ImageTk.PhotoImage(img)
                    self.camera_canvas.create_image(
                        canvas_width // 2 if canvas_width > 1 else 320,
                        canvas_height // 2 if canvas_height > 1 else 240,
                        image=self.camera_image,
                        anchor=tk.CENTER,
                    )
                except Exception as e:
                    self.camera_canvas.create_text(
                        320,
                        240,
                        text=f"Image decode error: {e}",
                        fill="white",
                        font=("Arial", 14),
                    )

            # Display camera info
            self.camera_canvas.create_text(
                10,
                10,
                text=f"{camera['name']} - {camera['location']}",
                fill="white",
                font=("Arial", 12, "bold"),
                anchor=tk.NW,
            )
            info_text = (
                f"Pan: {self.current_pan}, Zoom: {self.current_zoom}, "
                f"Time: {response.get('current_time', 0)}"
            )
            self.camera_canvas.create_text(
                10,
                30,
                text=info_text,
                fill="white",
                font=("Arial", 10),
                anchor=tk.NW,
            )

        except Exception as e:
            error_message = str(e)
            if "400" in error_message:
                messagebox.showerror("Error", "Camera is disabled")
            elif "404" in error_message:
                messagebox.showerror("Error", "Camera not found")
            elif "Connection" in error_message or "refused" in error_message.lower():
                messagebox.showerror(
                    "Error",
                    "Cannot connect to backend server. "
                    "Please ensure the backend is running.",
                )
            else:
                messagebox.showerror(
                    "Error", f"Failed to load camera view: {error_message}"
                )
            self.camera_canvas.delete("all")
            self.camera_canvas.create_text(
                320,
                240,
                text="Failed to load camera view",
                fill="white",
                font=("Arial", 14),
            )

    def adjust_zoom(self, direction):
        """Adjust zoom level (1 = zoom in, -1 = zoom out)."""
        if not self.current_camera:
            return

        # Calculate new zoom level
        new_zoom = self.current_zoom
        if direction > 0:
            new_zoom = min(9, self.current_zoom + 1)
        else:
            new_zoom = max(1, self.current_zoom - 1)

        try:
            response = self.api_client.control_camera_ptz(
                self.current_camera, zoom=new_zoom
            )
            self.current_zoom = response.get("zoom_level", self.current_zoom)
            self.zoom_label.config(text=str(self.current_zoom))
            if response.get("success"):
                self.load_camera_view(self.current_camera)
            else:
                messagebox.showwarning(
                    "Warning", response.get("message", "Zoom limit reached")
                )
        except Exception as e:
            error_message = str(e)
            if "Connection" in error_message or "refused" in error_message.lower():
                messagebox.showerror(
                    "Error",
                    "Cannot connect to backend server. "
                    "Please ensure the backend is running.",
                )
            else:
                messagebox.showerror("Error", f"Failed to adjust zoom: {error_message}")

    def reset_zoom(self):
        """Reset zoom to default."""
        if not self.current_camera:
            return

        try:
            response = self.api_client.control_camera_ptz(self.current_camera, zoom=2)
            self.current_zoom = response.get("zoom_level", 2)
            self.zoom_label.config(text=str(self.current_zoom))
            if response.get("success"):
                self.load_camera_view(self.current_camera)
        except Exception as e:
            error_message = str(e)
            if "Connection" in error_message or "refused" in error_message.lower():
                messagebox.showerror(
                    "Error",
                    "Cannot connect to backend server. "
                    "Please ensure the backend is running.",
                )
            else:
                messagebox.showerror("Error", f"Failed to reset zoom: {error_message}")

    def adjust_pan(self, direction):
        """Adjust pan position (left = -1, right = 1)."""
        if not self.current_camera:
            return

        new_pan = self.current_pan + direction
        new_pan = max(-5, min(5, new_pan))

        try:
            response = self.api_client.control_camera_ptz(
                self.current_camera, pan=new_pan
            )
            self.current_pan = response.get("pan_position", self.current_pan)
            self.pan_label.config(text=str(self.current_pan))
            if response.get("success"):
                self.load_camera_view(self.current_camera)
            else:
                messagebox.showwarning(
                    "Warning", response.get("message", "Pan limit reached")
                )
        except Exception as e:
            error_message = str(e)
            if "Connection" in error_message or "refused" in error_message.lower():
                messagebox.showerror(
                    "Error",
                    "Cannot connect to backend server. "
                    "Please ensure the backend is running.",
                )
            else:
                messagebox.showerror("Error", f"Failed to adjust pan: {error_message}")

    def reset_pan(self):
        """Reset pan to center."""
        if not self.current_camera:
            return

        try:
            response = self.api_client.control_camera_ptz(self.current_camera, pan=0)
            self.current_pan = response.get("pan_position", 0)
            self.pan_label.config(text=str(self.current_pan))
            if response.get("success"):
                self.load_camera_view(self.current_camera)
        except Exception as e:
            error_message = str(e)
            if "Connection" in error_message or "refused" in error_message.lower():
                messagebox.showerror(
                    "Error",
                    "Cannot connect to backend server. "
                    "Please ensure the backend is running.",
                )
            else:
                messagebox.showerror("Error", f"Failed to reset pan: {error_message}")

    def enable_camera(self):
        """Enable the selected camera."""
        selected = self.camera_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a camera to enable")
            return

        item = self.camera_tree.item(selected[0])
        cam_id = int(item["tags"][0])

        try:
            self.api_client.enable_camera(cam_id)
            self.load_cameras()
            messagebox.showinfo("Success", "Camera enabled")
        except Exception as e:
            error_message = str(e)
            if "404" in error_message:
                messagebox.showerror("Error", "Camera not found")
            elif "Connection" in error_message or "refused" in error_message.lower():
                messagebox.showerror(
                    "Error",
                    "Cannot connect to backend server. "
                    "Please ensure the backend is running.",
                )
            else:
                messagebox.showerror(
                    "Error", f"Failed to enable camera: {error_message}"
                )

    def disable_camera(self):
        """Disable the selected camera."""
        selected = self.camera_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a camera to disable")
            return

        item = self.camera_tree.item(selected[0])
        cam_id = int(item["tags"][0])

        try:
            self.api_client.disable_camera(cam_id)
            self.load_cameras()
            messagebox.showinfo("Success", "Camera disabled")
        except Exception as e:
            error_message = str(e)
            if "404" in error_message:
                messagebox.showerror("Error", "Camera not found")
            elif "Connection" in error_message or "refused" in error_message.lower():
                messagebox.showerror(
                    "Error",
                    "Cannot connect to backend server. "
                    "Please ensure the backend is running.",
                )
            else:
                messagebox.showerror(
                    "Error", f"Failed to disable camera: {error_message}"
                )

    def set_camera_password(self):
        """Set password for the selected camera."""
        selected = self.camera_tree.selection()
        if not selected:
            messagebox.showinfo(
                "No Selection", "Please select a camera to set password"
            )
            return

        item = self.camera_tree.item(selected[0])
        cam_id = int(item["tags"][0])

        if cam_id not in self.cameras:
            return

        password = simpledialog.askstring(
            "Set Camera Password",
            f"Enter password for {self.cameras[cam_id]['name']}:",
            show="*",
        )
        if password:
            try:
                self.api_client.set_camera_password(cam_id, password)
                self.load_cameras()
                messagebox.showinfo("Success", "Camera password set")
            except Exception as e:
                error_message = str(e)
                if "404" in error_message:
                    messagebox.showerror("Error", "Camera not found")
                elif (
                    "Connection" in error_message or "refused" in error_message.lower()
                ):
                    messagebox.showerror(
                        "Error",
                        "Cannot connect to backend server. "
                        "Please ensure the backend is running.",
                    )
                else:
                    messagebox.showerror(
                        "Error", f"Failed to set password: {error_message}"
                    )

    def delete_camera_password(self):
        """Delete password for the selected camera."""
        selected = self.camera_tree.selection()
        if not selected:
            messagebox.showinfo(
                "No Selection", "Please select a camera to delete password"
            )
            return

        item = self.camera_tree.item(selected[0])
        cam_id = int(item["tags"][0])

        if cam_id not in self.cameras:
            return

        if not self.cameras[cam_id]["has_password"]:
            messagebox.showinfo("Info", "Camera has no password set")
            return

        result = messagebox.askyesno(
            "Delete Password",
            f"Are you sure you want to delete the password for "
            f"{self.cameras[cam_id]['name']}?",
        )
        if result:
            try:
                self.api_client.delete_camera_password(cam_id)
                self.load_cameras()
                messagebox.showinfo("Success", "Camera password deleted")
            except Exception as e:
                error_message = str(e)
                if "404" in error_message:
                    messagebox.showerror("Error", "Camera not found")
                elif (
                    "Connection" in error_message or "refused" in error_message.lower()
                ):
                    messagebox.showerror(
                        "Error",
                        "Cannot connect to backend server. "
                        "Please ensure the backend is running.",
                    )
                else:
                    messagebox.showerror(
                        "Error", f"Failed to delete password: {error_message}"
                    )

    def show_floor_plan(self):
        """Show the floor plan with camera locations."""
        floor_plan_window = tk.Toplevel(self)
        floor_plan_window.title("Floor Plan")
        floor_plan_window.geometry("800x600")

        canvas = tk.Canvas(floor_plan_window, bg="white")
        canvas.pack(fill=tk.BOTH, expand=True)

        floor_plan_path = self.project_root / "floorplan.png"
        if floor_plan_path.exists():
            try:
                img = Image.open(str(floor_plan_path))
                img = img.resize((800, 600), Image.Resampling.LANCZOS)
                floor_plan_img = ImageTk.PhotoImage(img)
                canvas.create_image(400, 300, image=floor_plan_img, anchor=tk.CENTER)
                canvas.image = floor_plan_img
            except Exception:
                canvas.create_text(
                    400,
                    300,
                    text="Floor Plan\n(Camera locations would be shown here)",
                    font=("Arial", 16),
                )
        else:
            canvas.create_text(
                400,
                300,
                text="Floor Plan\n(Camera locations would be shown here)",
                font=("Arial", 16),
            )

        camera_positions = {
            1: (200, 150),
            2: (400, 300),
            3: (600, 450),
        }

        for cam_id, (x, y) in camera_positions.items():
            if cam_id in self.cameras:
                camera = self.cameras[cam_id]
                if not camera["is_online"]:
                    color = "gray"
                elif camera["is_enabled"]:
                    color = "green"
                else:
                    color = "red"
                canvas.create_oval(
                    x - 10, y - 10, x + 10, y + 10, fill=color, outline="black"
                )
                canvas.create_text(
                    x,
                    y - 20,
                    text=camera["name"],
                    font=("Arial", 10),
                    anchor=tk.CENTER,
                )

                def make_click_handler(cid):
                    def handler(event):
                        self.select_camera_from_floor_plan(cid)
                        floor_plan_window.destroy()

                    return handler

                canvas.tag_bind(
                    f"camera_{cam_id}",
                    "<Button-1>",
                    make_click_handler(cam_id),
                )

    def select_camera_from_floor_plan(self, cam_id):
        """Select camera from floor plan."""
        for item in self.camera_tree.get_children():
            if int(self.camera_tree.item(item)["tags"][0]) == cam_id:
                self.camera_tree.selection_set(item)
                self.on_camera_select(None)
                break

    def show_thumbnails(self):
        """Show camera thumbnails."""
        selected = self.camera_tree.selection()
        if not selected:
            messagebox.showinfo(
                "No Selection", "Please select a camera to view thumbnails"
            )
            return

        item = self.camera_tree.item(selected[0])
        cam_id = int(item["tags"][0])

        try:
            thumbnails = self.api_client.get_camera_thumbnails(cam_id)
        except Exception as e:
            error_message = str(e)
            if "404" in error_message:
                messagebox.showerror("Error", "Camera not found")
            elif "Connection" in error_message or "refused" in error_message.lower():
                messagebox.showerror(
                    "Error",
                    "Cannot connect to backend server. "
                    "Please ensure the backend is running.",
                )
            else:
                messagebox.showerror(
                    "Error", f"Failed to load thumbnails: {error_message}"
                )
            return

        thumbnail_window = tk.Toplevel(self)
        thumbnail_window.title(f"Camera Thumbnails - {self.cameras[cam_id]['name']}")
        thumbnail_window.geometry("900x600")

        canvas_frame = ttk.Frame(thumbnail_window)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(canvas_frame, bg="white")
        scrollbar = ttk.Scrollbar(
            canvas_frame, orient=tk.VERTICAL, command=canvas.yview
        )
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        row = 0
        col = 0
        for thumb in thumbnails:
            thumb_frame = ttk.LabelFrame(
                scrollable_frame,
                text=f"Captured: {thumb.get('captured_at', 'Unknown')}",
                padding=5,
            )
            thumb_frame.grid(row=row, column=col, padx=10, pady=10)

            # Display thumbnail URL or placeholder
            image_url = thumb.get("image_url", "")
            if image_url:
                ttk.Label(thumb_frame, text=f"Image: {image_url}").pack()
            else:
                ttk.Label(thumb_frame, text="No thumbnail available").pack()

            ttk.Label(thumb_frame, text=f"ID: {thumb.get('id', 'N/A')}").pack()

            col += 1
            if col >= 3:
                col = 0
                row += 1

        if not thumbnails:
            ttk.Label(
                scrollable_frame, text="No thumbnails available for this camera"
            ).pack(pady=20)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def view_camera_from_thumbnail(self, cam_id, window):
        """View camera from thumbnail selection."""
        window.destroy()
        for item in self.camera_tree.get_children():
            if int(self.camera_tree.item(item)["tags"][0]) == cam_id:
                self.camera_tree.selection_set(item)
                self.on_camera_select(None)
                break
