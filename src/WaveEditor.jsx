// Editor
import React, { useEffect, useRef, useState } from "react";
import { Editor } from "slate-react";
// import { initialValue, existingValue } from "./slateInitialValue";
import { cx, css } from "emotion";
import { Toolbar, Button, Icon } from "./components";
import { html } from "./htmlSerializer";
import { isKeyHotkey } from "is-hotkey";

const DEFAULT_NODE = "paragraph";
const isBoldHotkey = isKeyHotkey("mod+b");
const isItalicHotkey = isKeyHotkey("mod+i");
const isUnderlinedHotkey = isKeyHotkey("mod+u");
const isCodeHotkey = isKeyHotkey("mod+`");

const WaveEditor = props => {
  const editor = useRef(null);
  const draftId = $("input#id");
  const draftReferenceId = $("input#reference_id");
  const draftType = $("input#type");
  const draftTitle = $("input#title");
  const draftSubtitle = $("input#subtitle");
  const draftDescription = $("textarea#description");
  const draftContent = $("input#content");
  const draftTags = $("input#tags");
  const draftIsPublic = $("input#is_public")[0];
  const initialValue = draftContent.val() || "<p></p>";
  const [value, setValue] = useState(html.deserialize(initialValue));
  let interval;

  const get_draft = () => {
    const id = draftId.val();
    const referenceId = draftReferenceId.val();
    const type = draftType.val();
    const title = draftTitle.val();
    const subtitle = draftSubtitle.val();
    const description = draftDescription.val();
    const tags = draftTags.val();
    const content = html.serialize(value);
    const isPublic = draftIsPublic.checked === false;
    return {
      id: id,
      reference_id: referenceId,
      type: type,
      title: title,
      subtitle: subtitle,
      description: description,
      tags: tags,
      content: content,
      is_public: isPublic
    };
  };
  const [lastSaveDraft, setLastSaveDraft] = useState(JSON.stringify(get_draft()));

  useEffect(() => {
    interval = setInterval(function() {
      const draft = JSON.stringify(get_draft());
      // console.log(JSON.parse(draft));
      // console.log(JSON.parse(lastSaveDraft));
      if (lastSaveDraft && lastSaveDraft === draft) return;
      console.log("content changed");

      const draft_progress = $("#draft_progress span")[0];
      draft_progress.innerText = "Saving...";
      const url = "/api/v0/drafts/";
      $.ajax({
        url: url,
        type: "POST",
        data: draft,
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: data => {
          if (data.status === "success") {
            if (!draftId.val()) {
              draftId.val(data.id);
              window.history.replaceState({}, "", `/d/${data.id}/edit`);
            }
            setLastSaveDraft(draft);
            draft_progress.innerText = "Saved";
            console.log("saved: " + draft);
          }
        }
      });
    }, 1000);

    return () => {
      clearInterval(interval);
    };
  });

  // modal show event
  $("#publishModalForRichText").on("show.bs.modal", function (event) {
    // event.preventDefault();
    // const $modal = $(this);
    // TODO: refurnish this dumb trick
    const content = $("input#content");
    content.val(html.serialize(value));

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
    const { attributes, children, node } = props;

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
      default:
        return next();
    }
  };

  const handleChange = obj => {
    // if (obj.value.document !== value.document) {
    //   const content = html.serialize(obj.value);
    //   localStorage.setItem("content", content);
    // }

    console.log(value);
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
        `)}
        value={value}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        renderMark={renderMark}
        renderBlock={renderBlock}
      />
    </div>
  );
};

export default WaveEditor;
