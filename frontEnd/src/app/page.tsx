"use client";
import React from "react";
import { motion } from "framer-motion";
import Link from "next/link";

export default function Home() {
  return (
    <div style={{ minHeight: "100vh", background: "linear-gradient(135deg, #e6e2c3 0%, #b7d7a8 100%)", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "Merriweather, serif" }}>
      <motion.div initial={{ opacity: 0, y: 40 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }} style={{ background: "rgba(255,255,245,0.97)", borderRadius: 24, boxShadow: "0 8px 32px rgba(34,49,63,0.12)", padding: "2.5rem 2rem 1.5rem 2rem", maxWidth: 700, width: "100%", textAlign: "center" }}>
        <motion.h1 initial={{ scale: 0.8 }} animate={{ scale: 1 }} transition={{ duration: 0.7 }} style={{ color: "#4e6e5d", fontSize: "2.5rem", marginBottom: 16, fontWeight: 700 }}>
          🌿 Ayurveda Remedy Bot 🌿
        </motion.h1>
        <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3, duration: 0.8 }} style={{ fontSize: "1.25rem", color: "#2d4739", marginBottom: 24 }}>
          Discover holistic health, natural remedies, and ancient wisdom with our AI-powered Ayurveda assistant.
        </motion.p>
        <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: 24, margin: "32px 0" }}>
          <motion.div whileHover={{ scale: 1.07 }}>
            <Link href="/chat" style={{ background: "#4e6e5d", color: "#fff", borderRadius: 16, padding: "1em 2em", fontSize: "1.1rem", textDecoration: "none", fontWeight: 500, boxShadow: "0 2px 8px rgba(34,49,63,0.06)" }}>
              Start Chatting
            </Link>
          </motion.div>
          <motion.div whileHover={{ scale: 1.07 }}>
            <Link href="/blog" style={{ background: "#b7d7a8", color: "#4e6e5d", borderRadius: 16, padding: "1em 2em", fontSize: "1.1rem", textDecoration: "none", fontWeight: 500, boxShadow: "0 2px 8px rgba(34,49,63,0.06)" }}>
              Read Blog
            </Link>
          </motion.div>
          <motion.div whileHover={{ scale: 1.07 }}>
            <Link href="/resources" style={{ background: "#e6e2c3", color: "#4e6e5d", borderRadius: 16, padding: "1em 2em", fontSize: "1.1rem", textDecoration: "none", fontWeight: 500, boxShadow: "0 2px 8px rgba(34,49,63,0.06)" }}>
              Resources
            </Link>
          </motion.div>
          <motion.div whileHover={{ scale: 1.07 }}>
            <Link href="/about" style={{ background: "#f6f5ee", color: "#4e6e5d", borderRadius: 16, padding: "1em 2em", fontSize: "1.1rem", textDecoration: "none", fontWeight: 500, boxShadow: "0 2px 8px rgba(34,49,63,0.06)" }}>
              About
            </Link>
          </motion.div>
          <motion.div whileHover={{ scale: 1.07 }}>
            <Link href="/contact" style={{ background: "#fff", color: "#4e6e5d", borderRadius: 16, padding: "1em 2em", fontSize: "1.1rem", textDecoration: "none", fontWeight: 500, boxShadow: "0 2px 8px rgba(34,49,63,0.06)" }}>
              Contact
            </Link>
          </motion.div>
        </div>
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.7, duration: 0.8 }} style={{ color: "#4e6e5d", fontSize: "1.1rem", marginTop: 24 }}>
          <b>Why Ayurveda?</b> Ayurveda is an ancient Indian system of medicine that emphasizes balance, prevention, and natural healing. Explore remedies, herbs, and wellness tips for a healthier life.
        </motion.div>
      </motion.div>
    </div>
  );
}
