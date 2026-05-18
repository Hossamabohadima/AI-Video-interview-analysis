import { useState, useEffect } from "react";

/**
 * Manages mobile sidebar open/close state.
 * Auto-closes when screen resizes to desktop (md breakpoint).
 */
const useMobileMenu = () => {
  const [isOpen, setIsOpen] = useState(false);

  const open  = () => setIsOpen(true);
  const close = () => setIsOpen(false);
  const toggle = () => setIsOpen((prev) => !prev);

  // Auto-close on desktop resize
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 768) close();
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  // Prevent body scroll when menu is open on mobile
  useEffect(() => {
    document.body.style.overflow = isOpen ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [isOpen]);

  return { isOpen, open, close, toggle };
};

export default useMobileMenu;