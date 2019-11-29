import React from "react";
import ReactDOM from "react-dom";
import WaveEditor from "./WaveEditor";
import { css, cx } from "emotion";

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

const slateEditor = document.getElementById("slate-editor");
if (slateEditor) ReactDOM.render(editor, slateEditor);
