import cv2
import numpy as np
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.img = None
        self.processed_img = None
        self.original_img = None
        
        self.setup_ui()

    def setup_ui(self):
        self.root.title("Enhanced Image Editor")
        self.root.geometry("800x600")

        # Image label
        self.img_label = ctk.CTkLabel(self.root, text="", fg_color="lightgray", corner_radius=10, width=600, height=400)
        self.img_label.pack(pady=10)

        # Button frame
        btn_frame = ctk.CTkFrame(self.root, fg_color="white", corner_radius=10)
        btn_frame.pack(pady=10)

        # Styled buttons
        ctk.CTkButton(
            btn_frame, text="Load Image", command=self.load_image,
            fg_color="#4CAF50", hover_color="#45A049", text_color="white", corner_radius=8
        ).grid(row=0, column=0, padx=10, pady=5)

        ctk.CTkButton(
            btn_frame, text="Crop", command=self.crop_image,
            fg_color="#2196F3", hover_color="#1E88E5", text_color="white", corner_radius=8
        ).grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkButton(
            btn_frame, text="Remove BG", command=self.remove_background,
            fg_color="#FF5722", hover_color="#E64A19", text_color="white", corner_radius=8
        ).grid(row=0, column=2, padx=10, pady=5)

        ctk.CTkButton(
            btn_frame, text="Reset", command=self.reset_image,
            fg_color="#9C27B0", hover_color="#7B1FA2", text_color="white", corner_radius=8
        ).grid(row=0, column=3, padx=10, pady=5)

        ctk.CTkButton(
            btn_frame, text="Save Image", command=self.save_image,
            fg_color="#FF9800", hover_color="#FB8C00", text_color="white", corner_radius=8
        ).grid(row=0, column=4, padx=10, pady=5)

        # Filter frame
        filter_frame = ctk.CTkFrame(self.root, fg_color="white", corner_radius=10)
        filter_frame.pack(pady=10)

        filters = ["Blur", "Sharpen", "Sepia", "Emboss", "Sketch"]
        for i, f in enumerate(filters):
            ctk.CTkButton(
                filter_frame, text=f, command=lambda f=f: self.apply_filter(f),
                fg_color="#FFC107", hover_color="#FFB300", text_color="black", corner_radius=8
            ).grid(row=1, column=i, padx=10, pady=5)

        # Brightness, Contrast, and Saturation sliders
        slider_frame = ctk.CTkFrame(self.root, fg_color="white", corner_radius=10)
        slider_frame.pack(pady=10)

        ctk.CTkLabel(slider_frame, text="Brightness").grid(row=0, column=0, padx=10, pady=5)
        self.brightness_slider = ctk.CTkSlider(slider_frame, from_=-100, to=100, command=self.change_brightness)
        self.brightness_slider.set(0)
        self.brightness_slider.grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkLabel(slider_frame, text="Contrast").grid(row=1, column=0, padx=10, pady=5)
        self.contrast_slider = ctk.CTkSlider(slider_frame, from_=-100, to=100, command=self.change_contrast)
        self.contrast_slider.set(0)
        self.contrast_slider.grid(row=1, column=1, padx=10, pady=5)

        ctk.CTkLabel(slider_frame, text="Saturation").grid(row=2, column=0, padx=10, pady=5)
        self.saturation_slider = ctk.CTkSlider(slider_frame, from_=-100, to=100, command=self.change_saturation)
        self.saturation_slider.set(0)
        self.saturation_slider.grid(row=2, column=1, padx=10, pady=5)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.img = cv2.imread(file_path)
            self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
            self.processed_img = self.img.copy()
            self.original_img = self.img.copy()
            self.display_image(self.img)

    def display_image(self, image):
        image = Image.fromarray(image)
        image = image.resize((600, 400), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(image)
        self.img_label.configure(image=img_tk)
        self.img_label.image = img_tk

    def apply_filter(self, filter_type):
        if self.img is None:
            return
        
        if filter_type == "Blur":
            self.processed_img = cv2.GaussianBlur(self.img, (15, 15), 0)
        elif filter_type == "Sharpen":
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            self.processed_img = cv2.filter2D(self.img, -1, kernel)
        elif filter_type == "Sepia":
            sepia = np.array([[0.272, 0.534, 0.131], [0.349, 0.686, 0.168], [0.393, 0.769, 0.189]])
            self.processed_img = cv2.transform(self.img, sepia)
            self.processed_img = np.clip(self.processed_img, 0, 255)
        elif filter_type == "Emboss":
            kernel = np.array([[2, 0, 0], [0, -1, 0], [0, 0, -1]])
            self.processed_img = cv2.filter2D(self.img, -1, kernel)
        elif filter_type == "Sketch":
            gray = cv2.cvtColor(self.img, cv2.COLOR_RGB2GRAY)
            inv = 255 - gray
            blur = cv2.GaussianBlur(inv, (21, 21), 0)
            self.processed_img = cv2.divide(gray, 255 - blur, scale=256)
            self.processed_img = cv2.cvtColor(self.processed_img, cv2.COLOR_GRAY2RGB)
        
        self.display_image(self.processed_img)

    def crop_image(self):
        if self.img is None:
            return
        roi = cv2.selectROI("Select ROI", cv2.cvtColor(self.img, cv2.COLOR_RGB2BGR), fromCenter=False, showCrosshair=True)
        cv2.destroyWindow("Select ROI")
        if roi[2] > 0 and roi[3] > 0:
            x, y, w, h = roi
            self.processed_img = self.img[y:y+h, x:x+w]
            self.display_image(self.processed_img)

    def remove_background(self):
        if self.img is None:
            return
        mask = np.zeros(self.img.shape[:2], np.uint8)
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)
        rect = (50, 50, self.img.shape[1] - 50, self.img.shape[0] - 50)
        cv2.grabCut(self.img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        self.processed_img = self.img * mask2[:, :, np.newaxis]
        self.display_image(self.processed_img)

    def reset_image(self):
        if self.original_img is not None:
            self.processed_img = self.original_img.copy()
            self.display_image(self.original_img)

    def save_image(self):
        if self.processed_img is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")])
            if file_path:
                save_img = cv2.cvtColor(self.processed_img, cv2.COLOR_RGB2BGR)
                cv2.imwrite(file_path, save_img)

    def change_brightness(self, value):
        if self.img is None:
            return
        value = int(value)
        hsv = cv2.cvtColor(self.img, cv2.COLOR_RGB2HSV)
        h, s, v = cv2.split(hsv)
        v = cv2.add(v, value)
        v = np.clip(v, 0, 255)
        hsv = cv2.merge((h, s, v))
        self.processed_img = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        self.display_image(self.processed_img)

    def change_contrast(self, value):
        if self.img is None:
            return
        value = float(value) / 100.0
        self.processed_img = cv2.addWeighted(self.img, 1 + value, np.zeros_like(self.img), 0, 0)
        self.display_image(self.processed_img)

    def change_saturation(self, value):
        if self.img is None:
            return
        value = int(value)
        hsv = cv2.cvtColor(self.img, cv2.COLOR_RGB2HSV)
        h, s, v = cv2.split(hsv)
        s = cv2.add(s, value)
        s = np.clip(s, 0, 255)
        hsv = cv2.merge((h, s, v))
        self.processed_img = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        self.display_image(self.processed_img)

if __name__ == "__main__":
    root = ctk.CTk()
    app = ImageEditor(root)
    root.mainloop()
