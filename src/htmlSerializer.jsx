import React from "react";

const BLOCK_TAGS = {
  div: "paragraph",
  p: "paragraph",
  h1: "heading-one",
  h2: "heading-two",
  ul: "bulleted-list",
  ol: "numbered-list",
  li: "list-item",
  blockquote: "block-quote",
  pre: "code"
};

const MARK_TAGS = {
  em: "italic",
  strong: "bold",
  u: "underlined",
  code: "code"
};

const rules = [
  {
    deserialize(el, next) {
      const type = BLOCK_TAGS[el.tagName.toLowerCase()];
      if (type) {
        return {
          object: "block",
          type: type,
          data: {
            className: el.getAttribute("class")
          },
          nodes: next(el.childNodes)
        };
      }
    },
    serialize(obj, children) {
      if (obj.object === "block") {
        switch (obj.type) {
          case "code":
            return (
              <pre>{children}</pre>
            );
          case "paragraph":
            return <p className={obj.data.get("className")}>{children}</p>;
          case "heading-one":
            return <h1>{children}</h1>;
          case "heading-two":
            return <h2>{children}</h2>;
          case "numbered-list":
            return <ol>{children}</ol>;
          case "bulleted-list":
            return <ul>{children}</ul>;
          case "list-item":
            return <li>{children}</li>;
          case "block-quote":
            return <blockquote>{children}</blockquote>;
        }
      }
    }
  },
  // Add a new rule that handles marks...
  {
    deserialize(el, next) {
      const type = MARK_TAGS[el.tagName.toLowerCase()];
      if (type) {
        return {
          object: "mark",
          type: type,
          nodes: next(el.childNodes)
        };
      }
    },
    serialize(obj, children) {
      if (obj.object === "mark") {
        switch (obj.type) {
          case "bold":
            return <strong>{children}</strong>;
          case "italic":
            return <em>{children}</em>;
          case "underlined":
            return <u>{children}</u>;
          case "code":
            return <code>{children}</code>;
        }
      }
    }
  }
];

import Html from "slate-html-serializer";

export const html = new Html({ rules });
