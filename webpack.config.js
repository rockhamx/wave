const path = require("path");
const webpack = require("webpack");
module.exports = {
    entry: [
        "./src/wave.js",
        "./src/App.jsx"
    ],
    // mode: "development",
    output: {
        path: __dirname + "/app/static/js",
        filename: "wave.js",
    },
    resolve: {
        extensions: [".js", ".jsx", ".css"]
    },
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/,
                exclude: /node_modules/,
                loader: "babel-loader",
                options: {
                    presets: ["@babel/preset-env", "@babel/preset-react"],
                    plugins: ["@babel/plugin-proposal-class-properties"]
                }
            }
        ]
    }
};