import $ from 'jquery';
import download from 'downloadjs';
import msgbox from '../shared/msgbox';
import redirectTo from '../shared/redirectTo';


export default {

    authenticated() {
        return localStorage.getItem("authTokenId") !== null;
    },

    logout() {
        localStorage.removeItem("authTokenId");
        return Promise.resolve();
    },

    exec(path, method, data, ajaxLoadingTarget, onProgress) {

        if (ajaxLoadingTarget) {
            $(ajaxLoadingTarget).addClass("mintax-ajax-in-progress");
        }

        return new Promise((resolve, reject) => {

            const url = MINTAX_API_BASE_URL + path;

            let succ = function (xhr) {

                if (ajaxLoadingTarget) {
                    $(ajaxLoadingTarget).removeClass("mintax-ajax-in-progress");
                }

                if (xhr.status === 200) {
                    try {
                        const json = JSON.parse(xhr.response);
                        resolve(json);
                    } catch (e) {
                        msgbox.alert("An unexpected error ocurred, please try again. If the problem "
                            + "persists please send an e-mail to contactus@e-taxconsulting.com.<br/><br/><small>"
                            + "Unable to convert return data</small>").then(reject);
                    }
                } else if (xhr.status === 204) {
                    resolve();
                } else if (xhr.status === 450) {
                    try {
                        const json = JSON.parse(xhr.response);
                        const payload = json.payload;
                        if (Array.isArray(payload)) {
                            let msg = "Your request was not fulfilled. Reasons:<br/><br/>";
                            msg += "<ul>";
                            payload.forEach(error => {
                                msg += "<li>" + error + "</li>";
                            });
                            msg += "</ul>";
                            msg += "<br/>Fix the problems above and try again.";
                            msgbox.alert(msg).then(reject);
                        } else {
                            msgbox.alert(payload).then(reject);
                        }
                    } catch (e) {
                        msgbox.alert("An unexpected error ocurred, please try again. If the problem "
                            + "persists please send an e-mail to contactus@e-taxconsulting.com.<br/><br/><small>"
                            + "Unable to convert return data</small>").then(reject);
                    }
                } else if (xhr.status === 403) {
                    redirectTo("/login");
                } else if (xhr.status === 455) {
                    msgbox.alert("You need admin privileges to access this page.").then(() => redirectTo("/"));
                } else if (xhr.status === 454) {
                    msgbox.alert("Your account is not active. Please send an e-mail to contactus@e-taxconsulting.com "
                            + "if you think this is an error.").then(() => {
                        localStorage.removeItem("authTokenId");
                        redirectTo("/login");
                    });
                } else if (xhr.status === 453) {
                    msgbox.alert("Your authentication has expired. Please sign in again and repeat the operation. " +
                                 "Sorry for any inconvenience caused.").then(() => {
                        redirectTo("/login");
                    });
                } else if (xhr.status === 550) {
                    msgbox.alert("An unexpected error ocurred, please try again. If the problem "
                            + "persists please send an e-mail to contactus@e-taxconsulting.com.").then(reject);
                } else if (xhr.status === 413) {
                    msgbox.alert("File too large (maximum allowed is 100mB).").then(reject);                    
                } else {
                    msgbox.alert("An unexpected error ocurred, please try again. If the problem "
                            + "persists please send an e-mail to contactus@e-taxconsulting.com. <br/><br/><small>"
                        + xhr.status + " " + xhr.statusText + "</small>").then(reject);
                }
            };

            let fail = function (xhr) {

                if (ajaxLoadingTarget) {
                    $(ajaxLoadingTarget).removeClass("mintax-ajax-in-progress");
                }

                msgbox.alert("An unexpected error ocurred, please try again. If the problem "
                            + "persists please send an e-mail to contactus@e-taxconsulting.com. <br/><br/><small>"
                    + xhr.responseText + "</small>").then(reject);
            };

            let finalMethod = method || 'GET';
            let body = undefined;
            let finalUrl = url;
            if (data) {
                if (finalMethod === 'GET') {
                    finalUrl += "?" + $.param(data);
                } else if (data instanceof FormData) {
                    body = data;
                } else {
                    body = JSON.stringify(data);
                }
            }

            const headers = {};
            if (!(data instanceof FormData)) {
                headers["Content-Type"] = "application/json";
            }
            const authTokenId = localStorage.getItem("authTokenId");
            if (authTokenId) {
                headers["X-MINTAX-AuthToken"] = authTokenId;
            }

            const xhr = new XMLHttpRequest();
            xhr.addEventListener("load", event => succ(xhr));
            xhr.addEventListener("error", event => fail(xhr));
            if (onProgress) {
                xhr.upload.addEventListener("progress", onProgress);
            }
            xhr.open(finalMethod, finalUrl, true);
            for (const header in headers) {
                xhr.setRequestHeader(header, headers[header]);
            }
            xhr.send(body);

        });
    },

    download(path, filename, ajaxLoadingTarget) {
        
        if (ajaxLoadingTarget) {
            $(ajaxLoadingTarget).addClass("mintax-ajax-in-progress");
        }

        const url = MINTAX_API_BASE_URL + path;

        let succ = function (resp) {
            resp.blob().then(data => download(data, filename));
            if (ajaxLoadingTarget) {
                $(ajaxLoadingTarget).removeClass("mintax-ajax-in-progress");
            }
        };

        let fail = function (err) {
            if (ajaxLoadingTarget) {
                $(ajaxLoadingTarget).removeClass("mintax-ajax-in-progress");
            }
            msgbox.alert("An unexpected error ocurred, please try again. If the problem "
                        + "persists please send an e-mail to contactus@e-taxconsulting.com. <br/><br/><small>"
                + err.message + "</small>").then(reject);
        };

        const headers = {};
        const authTokenId = localStorage.getItem("authTokenId");
        if (authTokenId) {
            headers["X-MINTAX-AuthToken"] = authTokenId;
        }

        fetch(url, {
            method: 'GET',
            headers: headers,
        }).then(succ, fail);

    },

    subscribe(eventChannel, dataConsumer) {
        const eventSource = new EventSource(MINTAX_API_BASE_URL + 'stream?channel=' + eventChannel);
        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            dataConsumer(data);
        };
        // it is very important to close the event source!
        // remember to call this in both success AND failure callbacks,
        // or, in the case of persistent channels, in both
        // didMount and willUnmount listeners
        return () => eventSource.close();
    }

};
