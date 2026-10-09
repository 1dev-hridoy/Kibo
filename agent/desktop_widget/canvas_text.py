class CanvasText:
    def __init__(self, root, canvas, slot, fill, font, row, east=False):
        self.root = root
        self.cv = canvas
        self.slot = slot
        self.fill = fill
        self.font = font
        self.row = row
        self.east = east
        self.wrap = 0
        self._anim_id = None
        while len(self.cv.texts) <= slot:
            self.cv.texts.append({})
        self.cv.texts[slot] = {"text": "", "fill": fill, "font": font,
                               "anchor": "e" if east else "w",
                               "row": row, "east": east,
                               "wrap": 0, "x": 0, "y": 0}



    def _place(self):
        e = self.cv.texts[self.slot]
        e["fill"] = self.fill
        e["font"] = self.font
        e["row"] = self.row
        e["east"] = self.east

    def _cancel(self):
        if self._anim_id:
            try:
                self.root.after_cancel(self._anim_id)
            except Exception:
                pass
            self._anim_id = None



    def _mix(self, target, t):
        try:
            r2 = int(target[1:3], 16); g2 = int(target[3:5], 16)
            b2 = int(target[5:7], 16)
            dim = (r2 // 3, g2 // 3, b2 // 3)
            r = int(dim[0] + (r2 - dim[0]) * t)
            g = int(dim[1] + (g2 - dim[1]) * t)
            b = int(dim[2] + (b2 - dim[2]) * t)
            return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, IndexError):
            return target
        



    def set_animated(self, text, delay_ms=0, mode="fade"):
        self._cancel()
        self._place()
        e = self.cv.texts[self.slot]
        e["text"] = ""
        if mode == "type":
            self._anim_id = self.root.after(
                delay_ms or 0, lambda: self._typewriter(text, 0))
        elif mode == "hearts":
            shown = f"\u2665\u2665 {text} \u2665\u2665"
            self._anim_id = self.root.after(
                delay_ms or 0, lambda: self._color_in(shown, "#f38ba8", 0))
        else:
            self._anim_id = self.root.after(
                delay_ms or 0, lambda: self._color_in(text, self.fill, 0))

            

    def _typewriter(self, text, i):
        if i > len(text):
            self._anim_id = None
            return
        self._place()
        self.cv.texts[self.slot]["text"] = text[:i]
        self._anim_id = self.root.after(
            35, lambda: self._typewriter(text, i + 1))

        

    def _color_in(self, text, target, step):
        self._place()
        e = self.cv.texts[self.slot]
        e["text"] = text
        steps = 9
        if step >= steps:
            e["fill"] = target
            self._anim_id = None
            return
        e["fill"] = self._mix(target, step / steps)
        self._anim_id = self.root.after(
            50, lambda: self._color_in(text, target, step + 1))

        

    def set_wrap(self, width):
        self.wrap = width
        self.cv.texts[self.slot]["wrap"] = width

    def set_style(self, fill=None, font=None):
        if fill is not None:
            self.fill = fill
        if font is not None:
            self.font = font
        self._place()

    def config(self, **kwargs):
        if "text" in kwargs:
            self._cancel()
            self._place()
            e = self.cv.texts[self.slot]
            e["text"] = kwargs["text"]
            e["fill"] = self.fill



    def hide(self):
        self._cancel()
        if self.slot < len(self.cv.texts):
            self.cv.texts[self.slot]["text"] = ""


