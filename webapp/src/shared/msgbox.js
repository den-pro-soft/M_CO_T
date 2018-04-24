
import bootbox from 'bootbox';


function centerDialog(box) {
    const dialog = box.find('.modal-dialog');
    box.css('display', 'block');
    dialog.css("margin-top", Math.max(0, ($(window).height() - dialog.height()) / 2));
}


export default {
    alert(msg) {
        return new Promise((resolve, reject) => {
            const box = bootbox.alert(msg, resolve);
            centerDialog(box);
        });
    },

    confirm(msg, confirmLabel, cancelLabel) {
        return new Promise((resolve, reject) => {
            const box = bootbox.confirm({
                message: msg,
                buttons: {
                    confirm: {
                        label: confirmLabel || 'Yes',
                        className: 'btn-danger',
                    },
                    cancel: {
                        label: cancelLabel || 'No',
                        className: 'btn-default',
                    }
                },
                callback: result => {
                    if (result) {
                        resolve();
                    } else {
                        reject();
                    }
                }
            });
            centerDialog(box);
        });
    }
};
