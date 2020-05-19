import React from "react";
import { cx, css } from "emotion";
import "bootstrap/dist/css/bootstrap.min.css" 
import "jquery/dist/jquery.slim"
import "bootstrap/dist/js/bootstrap.bundle"

function NaviBar(props) {
  const items = [
    {text: "主页", href: "#"},
    {text: "推荐", href: "#"},
    {text: "最新", href: "#"},
    {text: "关于", href: "#"},
  ]
  const navItems = items.map((info, index) => 
    <NavItem key={index} info={info} />
  )
  return (
    <nav className="navbar navbar-expand-lg navbar-light bg-light">
      <div className="collapse navbar-collapse">
        <ul className="navbar-nav">
          {navItems}
        </ul>
      </div>
    </nav>
  )
}

// function NaviItems(props) {
//   return (
//       <ul className="navbar-nav">
//         <NavItem item={props.items[0]}></NavItem>
//       </ul>
//   )
// }

function NavItem(props) {
  return (
    <li className="nav-item">
      <a className="nav-link" href={props.info.href}>
        {props.info.text}
      </a>
    </li>
  )
}

const Toolbar = ({ className, ...other }) => (
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

const Button = ({ className, active, ...other }) => (
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

const Icon = ({ className, ...other }) => (
  <i
    {...other}
    className={cx(
      "material-icons md-24",
      className
    )}
  />
);

export {NaviBar, Toolbar, Button, Icon};