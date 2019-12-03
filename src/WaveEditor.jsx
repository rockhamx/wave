// Editor
import React, { useEffect, useRef, useState } from "react";
import { Block } from "slate";
import { Editor, getEventTransfer } from "slate-react";
// import { initialValue, existingValue } from "./slateInitialValue";
import { html } from "./htmlSerializer";
import { Toolbar, Button, Icon } from "./components";
import { cx, css } from "emotion";
import { isKeyHotkey } from "is-hotkey";
import imageExtensions from "image-extensions";
import isUrl from "is-url";
// import { saveDraft } from "./draft";

const DEFAULT_NODE = "paragraph";
const isBoldHotkey = isKeyHotkey("mod+b");
const isItalicHotkey = isKeyHotkey("mod+i");
const isUnderlinedHotkey = isKeyHotkey("mod+u");
const isCodeHotkey = isKeyHotkey("mod+`");

const draftId = $("input#id");
const draftReferenceId = $("input#reference_id");
const draftType = $("input#type");
const draftTitle = $("input#title");
const draftSubtitle = $("input#subtitle");
const draftDescription = $("textarea#description");
const draftContent = $("input#content");
const draftPublication = $("select#publication");
const draftTags = $("input#tags");
const draftIsPublic = $("input#private");
const draft_progress = $("span#draft_progress")[0];
let draft = {};
if (draftId.length > 0) {
  draft = {
    id: draftId.val(),
    reference_id: draftReferenceId.val(),
    type: draftType.val(),
    title: draftTitle.val(),
    subtitle: draftSubtitle.val(),
    description: draftDescription.val(),
    publication: draftPublication.val(),
    tags: draftTags.val(),
    content: draftContent.val(),
    is_public: draftIsPublic[0].checked === false
  };
}

const saveDraft = () => {
  const json_draft = JSON.stringify(draft);
  console.log(draft);

  draft_progress.innerText = "Saving...";
  const url = "/api/v0/drafts/";
  $.ajax({
    url: url,
    type: "POST",
    data: json_draft,
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: data => {
      if (data.result === "success") {
        if (!draft.id) {
          draft.id = data.id;
          window.history.replaceState({}, "", `/d/${data.id}/edit`);
        }
        draft_progress.innerText = data.status;
        console.log(data.status + draft);
      }
    }
  });
};

const onChange = event => {
  switch (event.target.id) {
    case "title":
      draft.title = event.target.value;
      break;
    case "subtitle":
      draft.subtitle = event.target.value;
      break;
    case "description":
      draft.description = event.target.value;
      break;
    case "publication":
      draft.publication = event.target.value;
      break;
    case "tags":
      draft.tags = event.target.value;
      break;
    case "private":
      draft.is_public = event.target.checked === false;
      break;
  }
  saveDraft();
};

draftTitle.change(onChange);
draftSubtitle.change(onChange);
draftDescription.change(onChange);
draftPublication.change(onChange);
draftTags.change(onChange);
draftIsPublic.change(onChange);

/**
 * The editor's schema.
 *
 * @type {Object}
 */
const schema = {
  document: {
    last: { type: "paragraph" },
    normalize: (editor, { code, node, child }) => {
      switch (code) {
        case "last_child_type_invalid": {
          const paragraph = Block.create("paragraph");
          return editor.insertNodeByKey(node.key, node.nodes.size, paragraph);
        }
      }
    }
  },
  blocks: {
    image: {
      isVoid: true
    }
  }
};

const WaveEditor = props => {
  const editor = useRef(null);
  const initialValue = draftContent.val() || "<p></p>";
  const [value, setValue] = useState(html.deserialize(initialValue));
  const [count, setCount] = useState(0);

  // modal show event
  $("#publishModalForRichText").on("show.bs.modal", function(event) {
    // event.preventDefault();
    const $modal = $(this);
    draftContent.val(html.serialize(value));
  });

  const onClickMark = (event, type) => {
    event.preventDefault();
    editor.current.toggleMark(type);
  };

  const onClickBlock = (event, type) => {
    event.preventDefault();

    const current_editor = editor.current;
    // console.log(editor.current);
    const { value } = current_editor;
    // console.log(editor.current.setBlocks);
    const { document } = value;

    // Handle everything but list buttons.
    if (type !== "bulleted-list" && type !== "numbered-list") {
      const isActive = hasBlock(type);
      const isList = hasBlock("list-item");

      if (isList) {
        current_editor
          .setBlocks(isActive ? DEFAULT_NODE : type)
          .unwrapBlock("bulleted-list")
          .unwrapBlock("numbered-list");
      } else {
        current_editor.setBlocks(isActive ? DEFAULT_NODE : type);
      }
    } else {
      // Handle the extra wrapping required for list buttons.
      const isList = hasBlock("list-item");
      const isType = value.blocks.some(block => {
        return !!document.getClosest(block.key, parent => parent.type === type);
      });

      if (isList && isType) {
        current_editor
          .setBlocks(DEFAULT_NODE)
          .unwrapBlock("bulleted-list")
          .unwrapBlock("numbered-list");
      } else if (isList) {
        current_editor
          .unwrapBlock(
            type === "bulleted-list" ? "numbered-list" : "bulleted-list"
          )
          .wrapBlock(type);
      } else {
        current_editor.setBlocks("list-item").wrapBlock(type);
      }
    }
  };

  const hasMark = type => {
    return value.activeMarks.some(mark => mark.type === type);
  };

  const hasBlock = type => {
    return value.blocks.some(node => node.type === type);
  };

  const renderMarkButton = (type, icon) => {
    const isActive = hasMark(type);

    return (
      <Button active={isActive} onMouseDown={event => onClickMark(event, type)}>
        <Icon>{icon}</Icon>
      </Button>
    );
  };

  const renderBlockButton = (type, icon) => {
    let isActive = hasBlock(type);

    if (["numbered-list", "bulleted-list"].includes(type)) {
      const { document, blocks } = value;

      if (blocks.size > 0) {
        const parent = document.getParent(blocks.first().key);
        isActive = hasBlock("list-item") && parent && parent.type === type;
      }
    }

    return (
      <Button
        active={isActive}
        onMouseDown={event => onClickBlock(event, type)}
      >
        <Icon>{icon}</Icon>
      </Button>
    );
  };

  const handleChange = obj => {
    if (obj.value.document !== value.document) {
      // localStorage.setItem("content", content);
      setCount(count + 1);
      console.log(count);
      if (count > 2) {
        draft.content = html.serialize(obj.value);
        saveDraft();
        setCount(0);
      }
    }

    // console.log(value);
    setValue(obj.value);
  };

  const handleKeyDown = (event, editor, next) => {
    let mark;

    if (isBoldHotkey(event)) {
      mark = "bold";
    } else if (isItalicHotkey(event)) {
      mark = "italic";
    } else if (isUnderlinedHotkey(event)) {
      mark = "underlined";
    } else if (isCodeHotkey(event)) {
      mark = "code";
    } else {
      return next();
    }

    event.preventDefault();
    editor.toggleMark(mark);
  };

  const handleDropOrPaste = (event, editor, next) => {
    const target = editor.findEventRange(event);
    if (!target && event.type === "drop") return next();

    const transfer = getEventTransfer(event);
    const { type, text, files } = transfer;

    if (type === "files") {
      event.preventDefault();
      for (const file of files) {
        const reader = new FileReader();
        const [mime] = file.type.split("/");
        if (mime !== "image") continue;

        reader.addEventListener("load", () => {
          editor.command(insertImage, reader.result, target);
        });

        reader.readAsDataURL(file);
      }
      return;
    }

    if (["text", "html", "fragment"].includes(type)) {
      if (!isUrl(text)) return next();
      if (!isImageUrl(text)) return next();
      editor.command(insertImage, text, target);
      return;
    }

    next();
  };

  return (
    <div {...props}>
      <Toolbar>
        {renderMarkButton("bold", "format_bold")}
        {renderMarkButton("italic", "format_italic")}
        {renderMarkButton("underlined", "format_underlined")}
        {renderMarkButton("code", "code")}
        {renderBlockButton("heading-one", "looks_one")}
        {renderBlockButton("heading-two", "looks_two")}
        {renderBlockButton("block-quote", "format_quote")}
        {renderBlockButton("numbered-list", "format_list_numbered")}
        {renderBlockButton("bulleted-list", "format_list_bulleted")}
        {/*{renderBlockButton("insert-image", "insert_image")}*/}
      </Toolbar>
      <Editor
        ref={editor}
        spellCheck
        autoFocus
        placeholder="Enter some text..."
        className={cx(css`
          & > * + * {
            margin-top: 1rem;
          }
          font-size: 18px;
          min-height: 70rem;
          max-height: 80rem;
          overflow: auto;
        `)}
        value={value}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        onDrop={handleDropOrPaste}
        onPaste={handleDropOrPaste}
        schema={schema}
        renderMark={renderMark}
        renderBlock={renderBlock}
      />
    </div>
  );
};

/**
 * A function to determine whether a URL has an image extension.
 *
 * @param {String} url
 * @return {Boolean}
 */

function isImageUrl(url) {
  return imageExtensions.includes(getExtension(url));
}

/**
 * Get the extension of the URL, using the URL API.
 *
 * @param {String} url
 * @return {String}
 */

function getExtension(url) {
  return new URL(url).pathname.split(".").pop();
}

/**
 * A change function to standardize inserting images.
 *
 * @param {Editor} editor
 * @param {String} src
 * @param {Range} target
 */

function insertImage(editor, src, target) {
  if (target) {
    editor.select(target);
  }

  editor.insertBlock({
    type: "image",
    data: { src }
  });
}

const renderMark = (props, editor, next) => {
  const { children, attributes, mark } = props;

  switch (mark.type) {
    case "bold":
      return <strong {...attributes}>{children}</strong>;
    case "italic":
      return <em {...attributes}>{children}</em>;
    case "underlined":
      return <u {...attributes}>{children}</u>;
    case "code":
      return <code {...attributes}>{children}</code>;
    default:
      return next();
  }
};

const renderBlock = (props, editor, next) => {
  const { attributes, children, node, isFocused } = props;

  switch (node.type) {
    case "paragraph":
      return (
        <p {...attributes} className={cx(node.data.get("className"))}>
          {children}
        </p>
      );
    case "block-quote":
      return <blockquote {...attributes}>{children}</blockquote>;
    case "bulleted-list":
      return <ul {...attributes}>{children}</ul>;
    case "heading-one":
      return <h1 {...attributes}>{children}</h1>;
    case "heading-two":
      return <h2 {...attributes}>{children}</h2>;
    case "list-item":
      return <li {...attributes}>{children}</li>;
    case "numbered-list":
      return <ol {...attributes}>{children}</ol>;
    case "image":
      const src = node.data.get("src");
      return (
        <img
          {...attributes}
          src={src}
          alt=""
          className={css`
            display: block;
            max-width: 100%;
            max-height: 20em;
            box-shadow: ${isFocused
              ? "rgb(180, 213, 255) 0px 0px 0px 3px"
              : "none"};
          `}
        />
      );
    default:
      return next();
  }
};

export default WaveEditor;
