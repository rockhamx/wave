import React from "react";
import { cx, css } from "emotion";

export const Toolbar = ({ className, ...other }) => (
  <div
    {...other}
    className={cx(
      "toolbar",
      className,
      css`
        & > * {
          display: inline-block;
        }
        & > * + * {
          margin-left: 15px;
        }
        border-bottom: 2px solid #ddd;
        margin-bottom: 20px;
        padding-bottom: 10px;
      `
    )}
  />
);

export const Button = ({ className, active, ...other }) => (
  <span
    {...other}
    className={cx(
      className,
      css`
        cursor: pointer;
        color: ${active ? "#337AB7" : "#777"};
      `
    )}
  />
);

export const Icon = ({ className, ...other }) => (
  <i
    {...other}
    className={cx(
      "material-icons md-24",
      className
    )}
  />
);
