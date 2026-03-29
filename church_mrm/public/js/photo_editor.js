frappe.provide("church_mrm.photo_editor");

(function() {
    var CROPPER_CSS = "https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.6.2/cropper.min.css";
    var CROPPER_JS = "https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.6.2/cropper.min.js";
    var _loaded = false;

    function load_cropper() {
        return new Promise(function(resolve) {
            if (_loaded || window.Cropper) {
                _loaded = true;
                resolve();
                return;
            }
            // Load CSS
            var link = document.createElement("link");
            link.rel = "stylesheet";
            link.href = CROPPER_CSS;
            document.head.appendChild(link);
            // Load JS
            var script = document.createElement("script");
            script.src = CROPPER_JS;
            script.onload = function() {
                _loaded = true;
                resolve();
            };
            document.head.appendChild(script);
        });
    }

    church_mrm.photo_editor.open = function(frm) {
        if (!frm.doc.image) {
            frappe.msgprint(__("Please upload a photo first."));
            return;
        }

        load_cropper().then(function() {
            show_editor(frm);
        });
    };

    function show_editor(frm) {
        var image_url = frm.doc.image;
        // Add cache-buster for edited images
        if (image_url.indexOf("?") === -1) {
            image_url += "?t=" + Date.now();
        }

        var d = new frappe.ui.Dialog({
            title: __("Edit Photo"),
            size: "extra-large",
            fields: [
                {
                    fieldtype: "HTML",
                    fieldname: "editor_html"
                }
            ],
            primary_action_label: __("Save"),
            primary_action: function() {
                save_photo(frm, d);
            }
        });

        var html = '<div class="photo-editor-wrapper">' +
            '<div class="photo-editor-toolbar">' +
                '<button class="btn btn-default btn-sm pe-move" title="' + __("Move") + '">' +
                    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 9l-3 3 3 3"/><path d="M9 5l3-3 3 3"/><path d="M15 19l-3 3-3-3"/><path d="M19 9l3 3-3 3"/><line x1="2" y1="12" x2="22" y2="12"/><line x1="12" y1="2" x2="12" y2="22"/></svg> ' +
                    __("Move") +
                '</button>' +
                '<button class="btn btn-default btn-sm pe-crop active" title="' + __("Crop") + '">' +
                    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 2v14a2 2 0 0 0 2 2h14"/><path d="M18 22V8a2 2 0 0 0-2-2H2"/></svg> ' +
                    __("Crop") +
                '</button>' +
                '<span class="pe-separator"></span>' +
                '<button class="btn btn-default btn-sm pe-rotate-left" title="' + __("Rotate Left") + '">' +
                    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 4v6h6"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg> ' +
                    __("Rotate Left") +
                '</button>' +
                '<button class="btn btn-default btn-sm pe-rotate-right" title="' + __("Rotate Right") + '">' +
                    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 4v6h-6"/><path d="M20.49 15a9 9 0 1 1-2.13-9.36L23 10"/></svg> ' +
                    __("Rotate Right") +
                '</button>' +
                '<button class="btn btn-default btn-sm pe-reset" title="' + __("Reset") + '">' +
                    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="1 4 1 10 7 10"/><polyline points="23 20 23 14 17 14"/><path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"/></svg> ' +
                    __("Reset") +
                '</button>' +
            '</div>' +
            '<div class="photo-editor-container">' +
                '<img id="pe-image" src="' + image_url + '" crossorigin="anonymous">' +
            '</div>' +
            '<div class="photo-editor-resize">' +
                '<div class="resize-group">' +
                    '<label>' + __("Resize Width") + '</label>' +
                    '<input type="number" id="pe-resize-w" class="form-control input-sm" placeholder="auto" min="1" max="4000">' +
                '</div>' +
                '<div class="resize-group">' +
                    '<label>' + __("Resize Height") + '</label>' +
                    '<input type="number" id="pe-resize-h" class="form-control input-sm" placeholder="auto" min="1" max="4000">' +
                '</div>' +
                '<div class="resize-group resize-lock">' +
                    '<label><input type="checkbox" id="pe-lock-ratio" checked> ' + __("Lock ratio") + '</label>' +
                '</div>' +
            '</div>' +
        '</div>';

        d.fields_dict.editor_html.$wrapper.html(html);
        d.show();

        // Initialize Cropper after dialog renders
        setTimeout(function() {
            var img = d.$wrapper.find("#pe-image")[0];
            var cropper = new Cropper(img, {
                viewMode: 1,
                dragMode: "crop",
                autoCropArea: 1,
                responsive: true,
                rotatable: true,
                scalable: false,
                guides: true,
                center: true,
                background: true,
                ready: function() {
                    // Populate resize fields with natural dimensions
                    var imageData = cropper.getImageData();
                    d._originalWidth = imageData.naturalWidth;
                    d._originalHeight = imageData.naturalHeight;
                }
            });

            d._cropper = cropper;

            // Toolbar buttons - Move/Crop toggle
            d.$wrapper.find(".pe-move").on("click", function() {
                cropper.setDragMode("move");
                d.$wrapper.find(".pe-move").addClass("active");
                d.$wrapper.find(".pe-crop").removeClass("active");
            });
            d.$wrapper.find(".pe-crop").on("click", function() {
                cropper.setDragMode("crop");
                d.$wrapper.find(".pe-crop").addClass("active");
                d.$wrapper.find(".pe-move").removeClass("active");
            });

            d.$wrapper.find(".pe-rotate-left").on("click", function() {
                cropper.rotate(-90);
            });
            d.$wrapper.find(".pe-rotate-right").on("click", function() {
                cropper.rotate(90);
            });
            d.$wrapper.find(".pe-reset").on("click", function() {
                cropper.reset();
                d.$wrapper.find("#pe-resize-w").val("");
                d.$wrapper.find("#pe-resize-h").val("");
            });

            // Resize lock ratio
            d.$wrapper.find("#pe-resize-w").on("input", function() {
                if (d.$wrapper.find("#pe-lock-ratio").is(":checked") && d._originalWidth) {
                    var w = parseInt($(this).val()) || 0;
                    if (w > 0) {
                        var ratio = d._originalHeight / d._originalWidth;
                        d.$wrapper.find("#pe-resize-h").val(Math.round(w * ratio));
                    }
                }
            });
            d.$wrapper.find("#pe-resize-h").on("input", function() {
                if (d.$wrapper.find("#pe-lock-ratio").is(":checked") && d._originalHeight) {
                    var h = parseInt($(this).val()) || 0;
                    if (h > 0) {
                        var ratio = d._originalWidth / d._originalHeight;
                        d.$wrapper.find("#pe-resize-w").val(Math.round(h * ratio));
                    }
                }
            });
        }, 300);
    }

    function save_photo(frm, dialog) {
        var cropper = dialog._cropper;
        if (!cropper) {
            frappe.msgprint(__("Editor not ready. Please try again."));
            return;
        }

        var data = cropper.getData(true); // rounded integers
        var resize_w = parseInt(dialog.$wrapper.find("#pe-resize-w").val()) || 0;
        var resize_h = parseInt(dialog.$wrapper.find("#pe-resize-h").val()) || 0;

        frappe.call({
            method: "church_mrm.api.photo_editor.process_photo",
            args: {
                file_url: frm.doc.image,
                crop_x: data.x,
                crop_y: data.y,
                crop_width: data.width,
                crop_height: data.height,
                rotate: data.rotate,
                resize_width: resize_w,
                resize_height: resize_h,
                doctype: frm.doctype,
                docname: frm.docname
            },
            freeze: true,
            freeze_message: __("Processing photo..."),
            callback: function(r) {
                if (r.message && r.message.file_url) {
                    frm.set_value("image", r.message.file_url);
                    frm.save().then(function() {
                        dialog.hide();
                        frappe.show_alert({
                            message: __("Photo updated successfully"),
                            indicator: "green"
                        });
                    });
                }
            },
            error: function() {
                frappe.msgprint(__("Failed to process photo. Please try again."));
            }
        });
    }
})();
