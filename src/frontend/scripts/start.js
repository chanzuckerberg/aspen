"use strict";

// Do this as the first thing so that any code reading it knows the right env.
process.env.BABEL_ENV = "development";
process.env.NODE_ENV = "development";

// Makes the script crash on unhandled rejections instead of silently
// ignoring them. In the future, promise rejections that are not handled will
// terminate the Node.js process with a non-zero exit code.
process.on("unhandledRejection", (err) => {
  throw err;
});

// Ensure environment variables are read.
require("../config/env");

const webpack = require("webpack");
const checkRequiredFiles = require("react-dev-utils/checkRequiredFiles");
const paths = require("../config/paths");
const configFactory = require("../config/webpack.config");
const getClientEnvironment = require("../config/env");

// Warn and crash if required files are missing
if (!checkRequiredFiles([paths.appHtml, paths.appIndexJs])) {
  process.exit(1);
}

const config = configFactory("development");
const compiler = webpack(config);
const watcher = compiler.watch({}, (err, stats) => {
  if (err) {
    console.error(err);
    return;
  }

  console.log(
    stats.toString({
      chunks: false, // Makes the build much quieter
      colors: true, // Shows colors in the console
    })
  );
});

console.log("Webpack is watching for changes...\n");
