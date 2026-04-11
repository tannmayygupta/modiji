"use client"

import React, { useEffect, useState } from "react"

export function BackgroundBeams() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({
        x: e.clientX,
        y: e.clientY,
      });
    };

    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  return (
    <div className="pointer-events-none fixed inset-0 z-[-1] overflow-hidden bg-background">
      {/* Background Mesh */}
      <div className="absolute inset-0 bg-grid-black opacity-30" />
      
      {/* Dynamic Cursor Spotlight Tracking */}
      <div 
        className="absolute inset-0 opacity-40 transition-opacity duration-300"
        style={{
          background: `radial-gradient(400px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(0,0,0,0.06), transparent 80%)`
        }}
      />
      
      {/* Heavy stylized contrast gradients for depth */}
      <div className="absolute top-[-10%] right-[-5%] w-[40%] h-[40%] bg-gradient-to-br from-black/5 to-transparent rounded-full blur-3xl opacity-60" />
    </div>
  )
}
