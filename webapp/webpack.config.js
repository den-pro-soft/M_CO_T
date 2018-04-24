var path = require('path');
var webpack = require('webpack');
var HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  entry: './src/index.js',
  output: {
    path: __dirname + '/dist',
    filename: 'bundle.js',
    publicPath: '/',
  },
  module: {
    loaders: [
      {
        test: /.jsx?$/,
        loader: 'babel-loader',
        exclude: /node_modules/,
        query: {
          presets: ['es2015', 'react']
        }
      },
      {
        test: /\.css$/,
        loader: [
          'style-loader',
          'css-loader'
        ]
      },
      {
        test: /\.(png|svg|jpg|gif)$/,
        loader: [
          'file-loader'
        ]
      },
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/,
        loader: [
          'file-loader'
        ]
      },
      {
        test: /\.(xlsx)$/,
        loader: 'file-loader',
        options: {
          name: '[path][name].[ext]'
        }
      }
    ]
  },
  plugins: [
    // https://stackoverflow.com/questions/28969861/managing-jquery-plugin-dependency-in-webpack
    // 2. Use ProvidePlugin to inject implicit globals
    new webpack.ProvidePlugin({
      $: "jquery",
      jQuery: "jquery"
    }),
    new webpack.DefinePlugin({
      MINTAX_API_BASE_URL: "'" + (process.env.MINTAX_API_BASE_URL || "http://localhost:5000/") + "'",
      MINTAX_RECAPTCHA_SITEKEY: "'" + (process.env.MINTAX_RECAPTCHA_SITEKEY || "6LcOyCkUAAAAAJ5MjzhRbWdYC7b4AqDVyDvJ0BMf") + "'",
    }),
    new HtmlWebpackPlugin({
      title: "MinTax",
      template: "src/index.template.html",
    }),
  ],
};
