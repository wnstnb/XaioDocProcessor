import tkinter as tk
from tkinter import simpledialog, filedialog
import json


class FieldMappingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Field Mapping Tool")

        # Add toolbar buttons at the top of the window
        toolbar = tk.Frame(root)
        toolbar.pack(side="top", fill="x")

        add_text_btn = tk.Button(toolbar, text="Add Text Field", command=self.add_text_field)
        add_text_btn.pack(side="left", padx=5, pady=5)

        copy_field_btn = tk.Button(toolbar, text="Copy", command=self.copy_field)
        copy_field_btn.pack(side="left", padx=5, pady=5)

        save_config_btn = tk.Button(toolbar, text="Save Configuration", command=self.save_configuration)
        save_config_btn.pack(side="left", padx=5, pady=5)

        load_image_btn = tk.Button(toolbar, text="Load Form Image", command=self.load_image)
        load_image_btn.pack(side="left", padx=5, pady=5)

        load_config_btn = tk.Button(toolbar, text="Load Configuration", command=self.load_configuration)
        load_config_btn.pack(side="left", padx=5, pady=5)

        # Create the canvas below the toolbar
        self.canvas = tk.Canvas(root, width=800, height=1000, bg="white")
        self.canvas.pack(fill="both", expand=True)

        # Store field data
        self.fields = []
        self.current_field_id = None
        self.undo_stack = []  # Stack for undo functionality
        self.index_counter = 0  # Counter for unique field indices

        # Background image placeholder
        self.background_image = None

        # Key bindings for adjustments and actions
        self.root.bind("<Up>", lambda e: self.move_selected_field(0, -1))
        self.root.bind("<Down>", lambda e: self.move_selected_field(0, 1))
        self.root.bind("<Left>", lambda e: self.move_selected_field(-1, 0))
        self.root.bind("<Right>", lambda e: self.move_selected_field(1, 0))
        self.root.bind("<Control-v>", lambda e: self.copy_field())
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Delete>", lambda e: self.delete_selected_field())
        self.root.bind("<Control-s>", lambda e: self.save_configuration())


        # Info label to display current field details
        self.info_label = tk.Label(root, text="", anchor="w")
        self.info_label.pack(fill="x", padx=5, pady=2)

    def add_text_field(self):
        # Create a draggable text field
        field_id = f"Field {len(self.fields) + 1}"
        x, y = 50, 50  # Default position
        label = self.canvas.create_text(x, y, text=field_id, anchor="nw", font=("Arial", 10), fill="black")
        self.fields.append({"id": field_id, "x": x, "y": y, "index": self.index_counter})
        self.index_counter += 1

        # Enable dragging
        self.make_draggable(label)

    def copy_field(self):
        if self.current_field_id is None:
            return

        # Get the currently selected field
        for field in self.fields:
            if field["id"] == self.canvas.itemcget(self.current_field_id, "text"):
                self.index_counter += 1
                field_id = f'Field{self.index_counter:02d}' 
                x, y = field["x"], field["y"] + 20  # Offset new field 20 pixels lower
                label = self.canvas.create_text(x, y, text=field_id, anchor="nw", font=("Arial", 10), fill="black")
                new_field = {"id": field_id, "x": x, "y": y, "index": self.index_counter}
                self.fields.append(new_field)
                self.undo_stack.append(("add", new_field))  # Add to undo stack

                # Enable dragging and set as active field
                self.make_draggable(label)
                self.set_active_field(label)
                break

    def delete_selected_field(self):
        if self.current_field_id is None:
            return

        # Find and remove the selected field
        for field in self.fields:
            if field["id"] == self.canvas.itemcget(self.current_field_id, "text"):
                self.fields.remove(field)
                self.undo_stack.append(("delete", field))  # Add to undo stack
                break

        self.canvas.delete(self.current_field_id)
        self.current_field_id = None
        self.info_label.config(text="")  # Clear info label

    def undo(self):
        if not self.undo_stack:
            return

        action, field = self.undo_stack.pop()
        if action == "add":
            # Undo an add action
            self.fields.remove(field)
            for item in self.canvas.find_all():
                if self.canvas.itemcget(item, "text") == field["id"]:
                    self.canvas.delete(item)
                    break
        elif action == "delete":
            # Undo a delete action
            self.fields.append(field)
            label = self.canvas.create_text(field["x"], field["y"], text=field["id"], anchor="nw", font=("Arial", 10), fill="black")
            self.make_draggable(label)

    def make_draggable(self, widget_id):
        def on_drag_start(event):
            self.set_active_field(widget_id)

        def on_drag_move(event):
            self.canvas.coords(self.current_field_id, event.x, event.y)
            # Update field position
            for field in self.fields:
                if field["id"] == self.canvas.itemcget(widget_id, "text"):
                    field["x"], field["y"] = event.x, event.y
                    self.update_info_label(field)
                    break

        def on_double_click(event):
            # Rename the field on double-click
            for field in self.fields:
                if field["id"] == self.canvas.itemcget(widget_id, "text"):
                    new_name = simpledialog.askstring("Rename Field", "Enter new field name:", initialvalue=field["id"])
                    if new_name:
                        field["id"] = new_name
                        self.canvas.itemconfig(widget_id, text=new_name)
                        self.update_info_label(field)
                    break

        self.canvas.tag_bind(widget_id, "<ButtonPress-1>", on_drag_start)
        self.canvas.tag_bind(widget_id, "<B1-Motion>", on_drag_move)
        self.canvas.tag_bind(widget_id, "<Double-1>", on_double_click)

    def set_active_field(self, widget_id):
        if self.current_field_id is not None:
            self.canvas.itemconfig(self.current_field_id, fill="black")  # Reset previous active field to black
        self.current_field_id = widget_id
        self.canvas.itemconfig(self.current_field_id, fill="red")  # Highlight the current field in red

        # Update info label with details of the active field
        for field in self.fields:
            if field["id"] == self.canvas.itemcget(widget_id, "text"):
                self.update_info_label(field)
                break

    def update_info_label(self, field):
        if self.background_image:
            image_width = self.background_image.width()
            image_height = self.background_image.height()
            normalized_x = field["x"] / image_width
            normalized_y = field["y"] / image_height
        else:
            normalized_x = normalized_y = 0

        self.info_label.config(
            text=(
                f"ID: {field['id']} | Index: {field.get('index', 'N/A')} | X: {field['x']}, Y: {field['y']} | "
                f"Normalized X: {normalized_x:.4f}, Normalized Y: {normalized_y:.4f}"
            )
        )

    def move_selected_field(self, dx, dy):
        if self.current_field_id is None:
            return
        self.canvas.move(self.current_field_id, dx, dy)

        # Update field position
        for field in self.fields:
            if field["id"] == self.canvas.itemcget(self.current_field_id, "text"):
                field["x"] += dx
                field["y"] += dy
                self.update_info_label(field)
                break

    def save_configuration(self):
        # Save fields as JSON with normalized coordinates
        if not self.background_image:
            print("No background image loaded.")
            return

        field_config = []
        image_width = self.background_image.width()
        image_height = self.background_image.height()

        for field in self.fields:
            normalized_x = field["x"] / image_width
            normalized_y = field["y"] / image_height
            field_config.append({
                "id": field["id"],
                "coords": (normalized_x, normalized_y),
                "index": field["index"]
            })

        json_config = json.dumps(field_config, indent=2)

        # Save to file
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, "w") as f:
                f.write(json_config)
            print(f"Configuration saved to {file_path}")

    def load_configuration(self):
        # Load fields from a JSON file
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, "r") as f:
                field_config = json.load(f)

            # Clear existing fields
            self.fields = []
            self.canvas.delete("all")

            # Reload background image if it exists
            if self.background_image:
                self.canvas.create_image(0, 0, anchor="nw", image=self.background_image)

            # Reload fields
            image_width = self.background_image.width()
            image_height = self.background_image.height()

            for field in field_config:
                x = field["coords"][0] * image_width
                y = field["coords"][1] * image_height
                field_index = field.get("index", self.index_counter)  # Use existing index or assign a new one
                label = self.canvas.create_text(x, y, text=field["id"], anchor="nw", font=("Arial", 10), fill="black")
                self.fields.append({"id": field["id"], "x": x, "y": y, "index": field_index})
                self.index_counter = max(self.index_counter, field_index + 1)  # Keep index_counter updated
                self.make_draggable(label)

            print(f"Loaded configuration from {file_path}")

    def load_image(self):
        # Load an image as the form template
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.background_image = tk.PhotoImage(file=file_path)
            self.canvas.config(width=self.background_image.width(), height=self.background_image.height())
            self.canvas.create_image(0, 0, anchor="nw", image=self.background_image)
            print(f"Loaded image: {file_path}")


# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = FieldMappingApp(root)
    root.mainloop()
