import React from 'react';
import Recaptcha from 'react-recaptcha';


export default {
    setup() {
        const head = document.getElementsByTagName("head")[0];
        const scr = document.createElement("script");
        scr.src = "https://www.google.com/recaptcha/api.js";
        head.appendChild(scr);
    },

    createComponent(verifyCallback, referenceObserver) {
        // oddly enough, without this empty onloadCallback
        // I couldn't use verifyCallback, so DON'T remove it
        var onloadCallback = function () {
        };
        const sitekey = MINTAX_RECAPTCHA_SITEKEY;
        return <Recaptcha
            sitekey={sitekey}
            render="explicit"
            ref={e => (referenceObserver || (function () {}))(e)}
            onloadCallback={onloadCallback}
            verifyCallback={verifyCallback} />
    }
}
