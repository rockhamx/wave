import {Value} from "slate";

export const existingValue = JSON.parse(localStorage.getItem('content'));
export const initialValue = Value.fromJSON(existingValue || {
  document: {
    nodes: [
      {
        object: "block",
        type: "paragraph",
        nodes: [
          {
            object: "text",
            text: "A line of text in a paragraph."
          }
        ]
      }
    ]
  }
});