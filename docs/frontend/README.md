## The Stack

The frontend is written in [TypeScript](https://www.typescriptlang.org/), using the [React](https://reactjs.org/) framework. Files are packaged for server use via a [Webpack](https://webpack.js.org/) pipeline.

## Setting up a development environment

The only prerequisite for working with the frontend is [Node](https://nodejs.org/en/). We aim to use the latest Active LTS release (14.15.4). If you don't have Node installed or have another version, [nvm](https://github.com/nvm-sh/nvm) is a great way to install and manage Node.

From the **project root directory**:

1. Install nvm
```zsh
% curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.37.2/install.sh | bash
```

2. Install Node
```zsh
% nvm install
% nvm use
```

3. Install dependencies
```zsh
% npm --prefix src/ts install
```

## Running in development mode

1. Start Webpack in dev mode (watches for file changes)
```zsh
% npm --prefix src/ts start
```

That's it! Output files will automatically appear in the `static` folder of the Flask app (src/py/covidr/static). React hot reloading is not supported, so a browser refresh is required to see updated content.

## Linting / Style

```zsh
% npm --prefix src/ts run style
```
This will style and lint your code using the project's settings.

## Deployment

Once the source code has been placed on the target machine, but before the backend is started, the following command should be run:

```zsh
% npm --prefix src/ts run build
```

This creates a minimized production build and places it in the previously mentioned static folder.