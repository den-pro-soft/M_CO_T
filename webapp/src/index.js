import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap/dist/js/bootstrap.js';
import 'react-select/dist/react-select.css';
import 'react-datepicker/dist/react-datepicker.css';

import React from 'react';
import ReactDOM from 'react-dom';

import captcha from './shared/captcha';

import './index.css';
import App from './components/App';


captcha.setup();

const root = document.getElementById('root');
ReactDOM.render(
    <App />,
    root);
