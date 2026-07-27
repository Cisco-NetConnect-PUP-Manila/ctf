export default function Nav() {
  return (
    <nav className="nav">
      <div className="nav__inner">
        <a href="#top" className="nav__logo">
          PACKET<b>_</b>CAPTURE<span className="nav__blink">_</span>
        </a>
        <div className="nav__links">
          <a href="#about">About</a>
          <a href="#acts">Four Acts</a>
          <a href="#rules">Rules</a>
          <a href="#timeline">Timeline</a>
          <a href="#register">Register</a>
        </div>
      </div>
    </nav>
  );
}
