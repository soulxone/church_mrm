frappe.ui.form.on("Church Video", {
    youtube_url(frm) {
        if (!frm.doc.youtube_url) return;

        frappe.call({
            method: "church_mrm.api.youtube.fetch_oembed",
            args: { youtube_url: frm.doc.youtube_url },
            callback: function(r) {
                if (r.message) {
                    // Only auto-fill if fields are empty (allow manual override)
                    if (!frm.doc.title && r.message.title) {
                        frm.set_value("title", r.message.title);
                    }
                    if (r.message.thumbnail_url) {
                        frm.set_value("thumbnail_url", r.message.thumbnail_url);
                    }
                    if (r.message.video_id) {
                        frm.set_value("video_id", r.message.video_id);
                    }
                    frm.refresh_fields();
                    frappe.show_alert({
                        message: __("Video info fetched from YouTube"),
                        indicator: "green"
                    });
                }
            }
        });
    },

    refresh(frm) {
        // Show thumbnail preview if available
        if (frm.doc.thumbnail_url && !frm.is_new()) {
            frm.set_df_property("thumbnail_url", "description",
                '<img src="' + frm.doc.thumbnail_url + '" style="max-width:320px;border-radius:8px;margin-top:8px;">');
        }
    }
});
