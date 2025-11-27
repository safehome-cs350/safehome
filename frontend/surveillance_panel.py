"""Surveillance panel for camera management."""

import os
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk

from PIL import Image, ImageTk


class SurveillancePanel(ttk.Frame):
    """Panel for surveillance camera management."""

    def __init__(self, parent, app):
        """Initialize the surveillance panel."""
        super().__init__(parent)
        self.app = app

        self.project_root = Path(__file__).parent.parent.resolve()

        self.cameras = {
            1: {
                "name": "Front Door Camera",
                "enabled": True,
                "password": None,
                "location": "Front Door",
            },
            2: {
                "name": "Living Room Camera",
                "enabled": True,
                "password": None,
                "location": "Living Room",
            },
            3: {
                "name": "Back Door Camera",
                "enabled": False,
                "password": "camera123",
                "location": "Back Door",
            },
        }
        self.current_camera = None
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0

        self.setup_ui()

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

        control_frame = ttk.LabelFrame(
            left_frame, text="Camera Controls", padding=10
        )
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
        right_frame.pack(
            side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5
        )

        view_frame = ttk.Frame(right_frame)
        view_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.camera_canvas = tk.Canvas(
            view_frame, bg="black", width=640, height=480
        )
        self.camera_canvas.pack(fill=tk.BOTH, expand=True)

        self.camera_canvas.create_text(
            320,
            240,
            text="Select a camera to view",
            fill="white",
            font=("Arial", 16),
        )

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
            command=lambda: self.adjust_zoom(1.2),
            width=10,
        )
        zoom_in_btn.pack(side=tk.LEFT, padx=2)
        zoom_out_btn = ttk.Button(
            zoom_frame,
            text="Zoom Out",
            command=lambda: self.adjust_zoom(0.8),
            width=10,
        )
        zoom_out_btn.pack(side=tk.LEFT, padx=2)
        reset_zoom_btn = ttk.Button(
            zoom_frame, text="Reset Zoom", command=self.reset_zoom, width=12
        )
        reset_zoom_btn.pack(side=tk.LEFT, padx=2)

        self.zoom_label = ttk.Label(zoom_frame, text="1.0x")
        self.zoom_label.pack(side=tk.LEFT, padx=10)

        pan_frame = ttk.Frame(pan_zoom_frame)
        pan_frame.pack(fill=tk.X, pady=5)

        ttk.Label(pan_frame, text="Pan:").pack(side=tk.LEFT, padx=5)
        pan_up_btn = ttk.Button(
            pan_frame,
            text="↑",
            command=lambda: self.adjust_pan(0, -10),
            width=5,
        )
        pan_up_btn.pack(side=tk.LEFT, padx=2)
        pan_down_btn = ttk.Button(
            pan_frame, text="↓", command=lambda: self.adjust_pan(0, 10), width=5
        )
        pan_down_btn.pack(side=tk.LEFT, padx=2)
        pan_left_btn = ttk.Button(
            pan_frame,
            text="←",
            command=lambda: self.adjust_pan(-10, 0),
            width=5,
        )
        pan_left_btn.pack(side=tk.LEFT, padx=2)
        pan_right_btn = ttk.Button(
            pan_frame, text="→", command=lambda: self.adjust_pan(10, 0), width=5
        )
        pan_right_btn.pack(side=tk.LEFT, padx=2)
        reset_pan_btn = ttk.Button(
            pan_frame, text="Reset Pan", command=self.reset_pan, width=12
        )
        reset_pan_btn.pack(side=tk.LEFT, padx=2)

        self.refresh_camera_list()

    def refresh_camera_list(self):
        """Refresh the camera list display."""
        for item in self.camera_tree.get_children():
            self.camera_tree.delete(item)

        for cam_id, camera in sorted(self.cameras.items()):
            status = "Enabled" if camera["enabled"] else "Disabled"
            password_status = (
                "Protected" if camera["password"] else "No Password"
            )
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

            if camera["password"]:
                password = simpledialog.askstring(
                    "Camera Password",
                    f"Enter password for {camera['name']}:",
                    show="*",
                )
                if password != camera["password"]:
                    messagebox.showerror("Error", "Incorrect password")
                    self.camera_tree.selection_remove(selected[0])
                    return

            if not camera["enabled"]:
                messagebox.showinfo(
                    "Camera Disabled", "This camera is currently disabled"
                )
                return

            self.current_camera = cam_id
            self.display_camera_view(cam_id)

    def display_camera_view(self, cam_id):
        """Display the camera view."""
        camera = self.cameras[cam_id]

        self.camera_canvas.delete("all")

        image_path = None
        if cam_id == 1:
            image_path = self.project_root / "camera1.jpg"
        elif cam_id == 2:
            image_path = self.project_root / "camera2.jpg"
        elif cam_id == 3:
            image_path = self.project_root / "camera3.jpg"

        if image_path and image_path.exists():
            try:
                img = Image.open(str(image_path))
                img = img.resize((640, 480), Image.Resampling.LANCZOS)
                self.camera_image = ImageTk.PhotoImage(img)
                self.camera_canvas.create_image(
                    320, 240, image=self.camera_image, anchor=tk.CENTER
                )
                self.camera_canvas.create_text(
                    10,
                    10,
                    text=camera["name"],
                    fill="white",
                    font=("Arial", 12, "bold"),
                    anchor=tk.NW,
                )
            except Exception as e:
                self.camera_canvas.create_text(
                    320,
                    240,
                    text=f"Camera View\n{camera['name']}\n(Image load error: {e})",
                    fill="white",
                    font=("Arial", 14),
                )
        else:
            self.camera_canvas.create_text(
                320,
                240,
                text=f"Camera View\n{camera['name']}\n{camera['location']}",
                fill="white",
                font=("Arial", 14),
            )

    def adjust_zoom(self, factor):
        """Adjust zoom level."""
        self.zoom_level *= factor
        self.zoom_level = max(0.5, min(5.0, self.zoom_level))
        self.zoom_label.config(text=f"{self.zoom_level:.1f}x")
        if self.current_camera:
            self.display_camera_view(self.current_camera)

    def reset_zoom(self):
        """Reset zoom to default."""
        self.zoom_level = 1.0
        self.zoom_label.config(text="1.0x")
        if self.current_camera:
            self.display_camera_view(self.current_camera)

    def adjust_pan(self, dx, dy):
        """Adjust pan position."""
        self.pan_x += dx
        self.pan_y += dy
        self.pan_x = max(-100, min(100, self.pan_x))
        self.pan_y = max(-100, min(100, self.pan_y))
        if self.current_camera:
            self.display_camera_view(self.current_camera)

    def reset_pan(self):
        """Reset pan to center."""
        self.pan_x = 0
        self.pan_y = 0
        if self.current_camera:
            self.display_camera_view(self.current_camera)

    def enable_camera(self):
        """Enable the selected camera."""
        selected = self.camera_tree.selection()
        if not selected:
            messagebox.showinfo(
                "No Selection", "Please select a camera to enable"
            )
            return

        item = self.camera_tree.item(selected[0])
        cam_id = int(item["tags"][0])

        if cam_id in self.cameras:
            self.cameras[cam_id]["enabled"] = True
            self.refresh_camera_list()
            messagebox.showinfo(
                "Success", f"Camera '{self.cameras[cam_id]['name']}' enabled"
            )

    def disable_camera(self):
        """Disable the selected camera."""
        selected = self.camera_tree.selection()
        if not selected:
            messagebox.showinfo(
                "No Selection", "Please select a camera to disable"
            )
            return

        item = self.camera_tree.item(selected[0])
        cam_id = int(item["tags"][0])

        if cam_id in self.cameras:
            self.cameras[cam_id]["enabled"] = False
            self.refresh_camera_list()
            messagebox.showinfo(
                "Success", f"Camera '{self.cameras[cam_id]['name']}' disabled"
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

        if cam_id in self.cameras:
            password = simpledialog.askstring(
                "Set Camera Password",
                f"Enter password for {self.cameras[cam_id]['name']}:",
                show="*",
            )
            if password:
                self.cameras[cam_id]["password"] = password
                self.refresh_camera_list()
                messagebox.showinfo("Success", "Camera password set")

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

        if cam_id in self.cameras:
            if not self.cameras[cam_id]["password"]:
                messagebox.showinfo("Info", "Camera has no password set")
                return

            result = messagebox.askyesno(
                "Delete Password",
                f"Are you sure you want to delete the password for "
                f"{self.cameras[cam_id]['name']}?",
            )
            if result:
                self.cameras[cam_id]["password"] = None
                self.refresh_camera_list()
                messagebox.showinfo("Success", "Camera password deleted")

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
                canvas.create_image(
                    400, 300, image=floor_plan_img, anchor=tk.CENTER
                )
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
                color = "green" if camera["enabled"] else "red"
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
        thumbnail_window = tk.Toplevel(self)
        thumbnail_window.title("Camera Thumbnails")
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
        for cam_id, camera in sorted(self.cameras.items()):
            if camera["enabled"]:
                thumb_frame = ttk.LabelFrame(
                    scrollable_frame, text=camera["name"], padding=5
                )
                thumb_frame.grid(row=row, column=col, padx=10, pady=10)

                image_path = None
                if cam_id == 1:
                    image_path = self.project_root / "camera1.jpg"
                elif cam_id == 2:
                    image_path = self.project_root / "camera2.jpg"
                elif cam_id == 3:
                    image_path = self.project_root / "camera3.jpg"

                if image_path and image_path.exists():
                    try:
                        img = Image.open(str(image_path))
                        img = img.resize((200, 150), Image.Resampling.LANCZOS)
                        thumb_img = ImageTk.PhotoImage(img)
                        label = ttk.Label(thumb_frame, image=thumb_img)
                        label.image = thumb_img
                        label.pack()
                    except Exception:
                        ttk.Label(thumb_frame, text="No image").pack()
                else:
                    ttk.Label(thumb_frame, text="Camera View").pack()

                ttk.Button(
                    thumb_frame,
                    text="View",
                    command=lambda cid=cam_id: self.view_camera_from_thumbnail(
                        cid, thumbnail_window
                    ),
                ).pack(pady=5)

                col += 1
                if col >= 3:
                    col = 0
                    row += 1

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
