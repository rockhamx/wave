import React from "react";
import ReactDOM from "react-dom";
import { css, cx } from "emotion";
import WaveEditor from "./WaveEditor";
import {NaviBar} from "./components"
import "./sass/wave.sass"


const rootElement = document.getElementById("root");
if (rootElement) {
  const navbar = (
    <NaviBar />
  );
  ReactDOM.render(navbar, rootElement);
}

const slateEditor = document.getElementById("slate-editor");
if (slateEditor) {

  const editor = (
    <WaveEditor
      className={cx(css`
        background-color: #f8f8f8;
        width: inherit;
        // min-height: 50rem;
        padding: 20px;
      `)}
    />
  );
  ReactDOM.render(editor, slateEditor);
}
