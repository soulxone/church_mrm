frappe.provide("church_mrm.photo_editor");

(function() {
    var CROPPER_CSS = "https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.6.2/cropper.min.css";
    var CROPPER_JS = "https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.6.2/cropper.min.js";
    var _loaded = false;
    var MAX_UNDO = 3;

    function load_cropper() {
        return new Promise(function(resolve) {
            if (_loaded || window.Cropper) { _loaded = true; resolve(); return; }
            var link = document.createElement("link");
            link.rel = "stylesheet"; link.href = CROPPER_CSS;
            document.head.appendChild(link);
            var script = document.createElement("script");
            script.src = CROPPER_JS;
            script.onload = function() { _loaded = true; resolve(); };
            document.head.appendChild(script);
        });
    }

    church_mrm.photo_editor.open = function(frm) {
        if (!frm.doc.image) {
            frappe.msgprint(__("Please upload a photo first."));
            return;
        }
        load_cropper().then(function() { show_editor(frm); });
    };

    function show_editor(frm) {
        var image_url = frm.doc.image;
        if (image_url.indexOf("?") === -1) image_url += "?t=" + Date.now();

        // Undo/redo state
        var undoStack = [];
        var redoStack = [];

        var d = new frappe.ui.Dialog({
            title: __("Edit Photo"),
            size: "extra-large",
            fields: [{ fieldtype: "HTML", fieldname: "editor_html" }],
            primary_action_label: __("Save"),
            primary_action: function() { save_photo(frm, d); }
        });

        d._undoStack = undoStack;
        d._redoStack = redoStack;
        d._originalImageUrl = frm.doc.image;

        var html = build_editor_html(image_url);
        d.fields_dict.editor_html.$wrapper.html(html);
        d.show();

        // Reset sliders/checkboxes to defaults
        reset_adjustments(d);

        setTimeout(function() {
            init_cropper(d);
            bind_toolbar(d);
            bind_adjustments(d);
            update_undo_redo_buttons(d);
        }, 300);
    }

    function build_editor_html(image_url) {
        return '<div class="photo-editor-wrapper">' +
            // Row 1: Tool buttons
            '<div class="photo-editor-toolbar">' +
                btn("pe-undo", "disabled", "Undo", '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 4v6h6"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg>') +
                btn("pe-redo", "disabled", "Redo", '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 4v6h-6"/><path d="M20.49 15a9 9 0 1 1-2.13-9.36L23 10"/></svg>') +
                '<span class="pe-separator"></span>' +
                btn("pe-move", "", "Move", '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 9l-3 3 3 3"/><path d="M9 5l3-3 3 3"/><path d="M15 19l-3 3-3-3"/><path d="M19 9l3 3-3 3"/><line x1="2" y1="12" x2="22" y2="12"/><line x1="12" y1="2" x2="12" y2="22"/></svg>') +
                btn("pe-crop", "active", "Crop", '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 2v14a2 2 0 0 0 2 2h14"/><path d="M18 22V8a2 2 0 0 0-2-2H2"/></svg>') +
                '<span class="pe-separator"></span>' +
                btn("pe-rotate-left", "", "Rotate Left", '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 4v6h6"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg>') +
                btn("pe-rotate-right", "", "Rotate Right", '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 4v6h-6"/><path d="M20.49 15a9 9 0 1 1-2.13-9.36L23 10"/></svg>') +
                btn("pe-flip-h", "", "Flip H", '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h3"/><path d="M16 3h3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-3"/><line x1="12" y1="2" x2="12" y2="22"/></svg>') +
                btn("pe-flip-v", "", "Flip V", '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 8V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v3"/><path d="M3 16v3a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-3"/><line x1="2" y1="12" x2="22" y2="12"/></svg>') +
                '<span class="pe-separator"></span>' +
                btn("pe-reset", "", "Reset", '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="1 4 1 10 7 10"/><polyline points="23 20 23 14 17 14"/><path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"/></svg>') +
            '</div>' +
            // Image canvas
            '<div class="photo-editor-container">' +
                '<img id="pe-image" src="' + image_url + '">' +
            '</div>' +
            // Row 2: Adjustments panel
            '<div class="photo-editor-adjustments">' +
                '<div class="pe-adj-title">Adjustments</div>' +
                '<div class="pe-adj-grid">' +
                    slider("brightness", "Brightness", 0.2, 3.0, 1.0, 0.05) +
                    slider("contrast", "Contrast", 0.2, 3.0, 1.0, 0.05) +
                    slider("sharpness", "Sharpness", 0.0, 3.0, 1.0, 0.1) +
                    slider("saturation", "Saturation", 0.0, 3.0, 1.0, 0.05) +
                    slider("blur", "Blur", 0, 10, 0, 0.5) +
                '</div>' +
                '<div class="pe-adj-title" style="margin-top:8px">Filters</div>' +
                '<div class="pe-filter-row">' +
                    filter_btn("pe-grayscale", "Grayscale") +
                    filter_btn("pe-sepia", "Sepia") +
                    filter_btn("pe-auto-enhance", "Auto Enhance") +
                    filter_btn("pe-invert", "Invert") +
                '</div>' +
            '</div>' +
            // Row 3: Resize
            '<div class="photo-editor-resize">' +
                '<div class="resize-group">' +
                    '<label>Resize Width</label>' +
                    '<input type="number" id="pe-resize-w" class="form-control input-sm" placeholder="auto" min="1" max="4000">' +
                '</div>' +
                '<div class="resize-group">' +
                    '<label>Resize Height</label>' +
                    '<input type="number" id="pe-resize-h" class="form-control input-sm" placeholder="auto" min="1" max="4000">' +
                '</div>' +
                '<div class="resize-group resize-lock">' +
                    '<label><input type="checkbox" id="pe-lock-ratio" checked> Lock ratio</label>' +
                '</div>' +
            '</div>' +
        '</div>';
    }

    function btn(cls, extra, label, svg) {
        return '<button class="btn btn-default btn-sm ' + cls + ' ' + extra + '" title="' + __(label) + '">' +
            svg + ' ' + __(label) + '</button>';
    }

    function slider(id, label, min, max, val, step) {
        return '<div class="pe-adj-item">' +
            '<label>' + __(label) + ' <span class="pe-adj-val" data-for="' + id + '">' + val + '</span></label>' +
            '<input type="range" id="pe-' + id + '" min="' + min + '" max="' + max + '" value="' + val + '" step="' + step + '">' +
        '</div>';
    }

    function filter_btn(cls, label) {
        return '<button class="btn btn-default btn-xs ' + cls + '">' + __(label) + '</button>';
    }

    function init_cropper(d) {
        var img = d.$wrapper.find("#pe-image")[0];
        var cropper = new Cropper(img, {
            viewMode: 1, dragMode: "crop", autoCropArea: 1,
            responsive: true, rotatable: true, scalable: false,
            guides: true, center: true, background: true,
            ready: function() {
                var data = cropper.getImageData();
                d._originalWidth = data.naturalWidth;
                d._originalHeight = data.naturalHeight;
            }
        });
        d._cropper = cropper;
    }

    function bind_toolbar(d) {
        var w = d.$wrapper;
        var cropper = function() { return d._cropper; };

        // Move/Crop toggle
        w.find(".pe-move").on("click", function() {
            cropper().setDragMode("move");
            w.find(".pe-move").addClass("active");
            w.find(".pe-crop").removeClass("active");
        });
        w.find(".pe-crop").on("click", function() {
            cropper().setDragMode("crop");
            w.find(".pe-crop").addClass("active");
            w.find(".pe-move").removeClass("active");
        });

        // Rotate
        w.find(".pe-rotate-left").on("click", function() { cropper().rotate(-90); });
        w.find(".pe-rotate-right").on("click", function() { cropper().rotate(90); });

        // Flip toggles
        d._flipH = false;
        d._flipV = false;
        w.find(".pe-flip-h").on("click", function() {
            d._flipH = !d._flipH;
            var sx = d._flipH ? -1 : 1;
            cropper().scaleX(sx);
            $(this).toggleClass("active", d._flipH);
        });
        w.find(".pe-flip-v").on("click", function() {
            d._flipV = !d._flipV;
            var sy = d._flipV ? -1 : 1;
            cropper().scaleY(sy);
            $(this).toggleClass("active", d._flipV);
        });

        // Reset
        w.find(".pe-reset").on("click", function() {
            cropper().reset();
            d._flipH = false;
            d._flipV = false;
            w.find(".pe-flip-h, .pe-flip-v").removeClass("active");
            w.find("#pe-resize-w, #pe-resize-h").val("");
            reset_adjustments(d);
        });

        // Undo / Redo
        w.find(".pe-undo").on("click", function() {
            if (d._undoStack.length === 0) return;
            var prev = d._undoStack.pop();
            d._redoStack.push(d._originalImageUrl);
            if (d._redoStack.length > MAX_UNDO) d._redoStack.shift();
            d._originalImageUrl = prev;
            reload_image(d, prev);
            update_undo_redo_buttons(d);
        });
        w.find(".pe-redo").on("click", function() {
            if (d._redoStack.length === 0) return;
            var next = d._redoStack.pop();
            d._undoStack.push(d._originalImageUrl);
            if (d._undoStack.length > MAX_UNDO) d._undoStack.shift();
            d._originalImageUrl = next;
            reload_image(d, next);
            update_undo_redo_buttons(d);
        });

        // Resize lock ratio
        w.find("#pe-resize-w").on("input", function() {
            if (w.find("#pe-lock-ratio").is(":checked") && d._originalWidth) {
                var v = parseInt($(this).val()) || 0;
                if (v > 0) w.find("#pe-resize-h").val(Math.round(v * (d._originalHeight / d._originalWidth)));
            }
        });
        w.find("#pe-resize-h").on("input", function() {
            if (w.find("#pe-lock-ratio").is(":checked") && d._originalHeight) {
                var v = parseInt($(this).val()) || 0;
                if (v > 0) w.find("#pe-resize-w").val(Math.round(v * (d._originalWidth / d._originalHeight)));
            }
        });
    }

    function bind_adjustments(d) {
        var w = d.$wrapper;

        // Slider value display
        w.find('.pe-adj-item input[type="range"]').on("input", function() {
            var id = $(this).attr("id").replace("pe-", "");
            w.find('.pe-adj-val[data-for="' + id + '"]').text($(this).val());
        });

        // Filter toggle buttons
        w.find(".pe-grayscale, .pe-sepia, .pe-auto-enhance, .pe-invert").on("click", function() {
            $(this).toggleClass("active");
        });
    }

    function reset_adjustments(d) {
        var w = d.$wrapper;
        var defaults = { brightness: 1.0, contrast: 1.0, sharpness: 1.0, saturation: 1.0, blur: 0 };
        for (var k in defaults) {
            w.find("#pe-" + k).val(defaults[k]);
            w.find('.pe-adj-val[data-for="' + k + '"]').text(defaults[k]);
        }
        w.find(".pe-grayscale, .pe-sepia, .pe-auto-enhance, .pe-invert").removeClass("active");
    }

    function reload_image(d, url) {
        if (d._cropper) d._cropper.destroy();
        var imgUrl = url + (url.indexOf("?") === -1 ? "?t=" : "&t=") + Date.now();
        d.$wrapper.find("#pe-image").attr("src", imgUrl);
        d._flipH = false;
        d._flipV = false;
        d.$wrapper.find(".pe-flip-h, .pe-flip-v").removeClass("active");
        reset_adjustments(d);
        setTimeout(function() { init_cropper(d); }, 300);
    }

    function update_undo_redo_buttons(d) {
        d.$wrapper.find(".pe-undo").toggleClass("disabled", d._undoStack.length === 0);
        d.$wrapper.find(".pe-redo").toggleClass("disabled", d._redoStack.length === 0);
    }

    function get_adjustment_args(d) {
        var w = d.$wrapper;
        return {
            brightness: parseFloat(w.find("#pe-brightness").val()) || 1.0,
            contrast: parseFloat(w.find("#pe-contrast").val()) || 1.0,
            sharpness: parseFloat(w.find("#pe-sharpness").val()) || 1.0,
            saturation: parseFloat(w.find("#pe-saturation").val()) || 1.0,
            blur: parseFloat(w.find("#pe-blur").val()) || 0,
            grayscale: w.find(".pe-grayscale").hasClass("active") ? 1 : 0,
            sepia: w.find(".pe-sepia").hasClass("active") ? 1 : 0,
            auto_enhance: w.find(".pe-auto-enhance").hasClass("active") ? 1 : 0,
            invert: w.find(".pe-invert").hasClass("active") ? 1 : 0
        };
    }

    function save_photo(frm, dialog) {
        var cropper = dialog._cropper;
        if (!cropper) { frappe.msgprint(__("Editor not ready.")); return; }

        var data = cropper.getData(true);
        var resize_w = parseInt(dialog.$wrapper.find("#pe-resize-w").val()) || 0;
        var resize_h = parseInt(dialog.$wrapper.find("#pe-resize-h").val()) || 0;
        var adj = get_adjustment_args(dialog);

        // Push current state to undo stack before saving
        dialog._undoStack.push(dialog._originalImageUrl);
        if (dialog._undoStack.length > MAX_UNDO) dialog._undoStack.shift();
        dialog._redoStack = []; // clear redo on new edit

        var args = {
            file_url: dialog._originalImageUrl,
            crop_x: data.x, crop_y: data.y,
            crop_width: data.width, crop_height: data.height,
            rotate: data.rotate,
            flip_h: dialog._flipH ? 1 : 0,
            flip_v: dialog._flipV ? 1 : 0,
            resize_width: resize_w, resize_height: resize_h,
            doctype: frm.doctype, docname: frm.docname
        };

        // Merge adjustment args
        for (var k in adj) args[k] = adj[k];

        frappe.call({
            method: "church_mrm.api.photo_editor.process_photo",
            args: args,
            freeze: true,
            freeze_message: __("Processing photo..."),
            callback: function(r) {
                if (r.message && r.message.file_url) {
                    var new_url = r.message.file_url;
                    dialog._originalImageUrl = new_url;
                    frm.set_value("image", new_url);
                    frm.save().then(function() {
                        // Reload the image in the editor instead of closing
                        reload_image(dialog, new_url);
                        update_undo_redo_buttons(dialog);
                        frappe.show_alert({
                            message: __("Photo saved. Continue editing or close."),
                            indicator: "green"
                        });
                    });
                }
            },
            error: function() {
                // Revert undo stack push on error
                dialog._undoStack.pop();
                frappe.msgprint(__("Failed to process photo. Please try again."));
            }
        });
    }
})();
