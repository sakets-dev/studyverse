import { useState } from "react";
import { motion } from "framer-motion";
import { Sparkles, ArrowRight } from "lucide-react";

export default function App() {
  const [verse, setVerse] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (verse.trim()) setSubmitted(true);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-indigo-900 via-purple-800 to-pink-700 text-white relative overflow-hidden">
      {/* Subtle floating particles */}
      <div className="absolute inset-0 overflow-hidden">
        {[...Array(30)].map((_, i) => (
          <motion.span
            key={i}
            className="absolute w-1 h-1 bg-white rounded-full opacity-20"
            initial={{
              x: Math.random() * window.innerWidth,
              y: Math.random() * window.innerHeight,
            }}
            animate={{
              y: [Math.random() * window.innerHeight, -20],
              opacity: [0.4, 0],
            }}
            transition={{
              duration: Math.random() * 10 + 10,
              repeat: Infinity,
              ease: "linear",
            }}
          />
        ))}
      </div>

      {/* Main content */}
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1 }}
        className="text-center px-4 z-10"
      >
        <div className="flex justify-center mb-6">
          <Sparkles className="w-10 h-10 text-yellow-300 animate-pulse" />
        </div>

        <h1 className="text-6xl md:text-7xl font-extrabold tracking-tight drop-shadow-lg">
          Welcome to <span className="text-yellow-300">StudyVerse</span>
        </h1>
        <p className="mt-4 text-lg text-gray-200 max-w-xl mx-auto">
          Step into an immersive world built around your focus, creativity, and mood.
        </p>

        {!submitted ? (
          <form
            onSubmit={handleSubmit}
            className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-3"
          >
            <input
              type="text"
              placeholder="What verse would you like to be in?"
              value={verse}
              onChange={(e) => setVerse(e.target.value)}
              className="px-5 py-3 w-72 sm:w-96 rounded-xl text-gray-900 text-lg focus:outline-none focus:ring-4 focus:ring-pink-400"
            />
            <button
              type="submit"
              className="flex items-center gap-2 bg-yellow-400 text-indigo-900 font-semibold px-6 py-3 rounded-xl hover:bg-yellow-300 transition-all hover:scale-105 shadow-lg"
            >
              Enter
              <ArrowRight className="w-5 h-5" />
            </button>
          </form>
        ) : (
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.6 }}
            className="mt-16"
          >
            <h2 className="text-4xl font-bold mb-4">
              Loading <span className="text-yellow-300">{verse}</span>...
            </h2>
            <p className="text-gray-200">
              Generating your personalized world ✨
            </p>
          </motion.div>
        )}
      </motion.div>

      {/* footer */}
      <footer className="absolute bottom-4 text-sm text-gray-300">
        © 2025 StudyVerse • Made with ❤️ by Saket Sharma
      </footer>
    </div>
  );
}
