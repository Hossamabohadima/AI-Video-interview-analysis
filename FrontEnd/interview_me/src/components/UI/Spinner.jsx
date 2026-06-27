/**
 * LoadingOverlay
 * Full-screen loading overlay with branded spinner.
 * Blurs content behind it while keeping sidebar and header visible.
 *
 * Props:
 * - message    (string): main loading text
 * - submessage (string): smaller text below message
 */

const LoadingOverlay = ({
  message    = "Processing...",
  submessage = "This may take a few minutes",
}) => {
  return (
    <div className="fixed inset-0 z-30 flex flex-col items-center justify-center bg-white/30 backdrop-blur-md">

      {/* Spinner rings */}
      <div className="relative flex items-center justify-center w-32 h-32">

        {/* Static background ring */}
        <div className="absolute w-32 h-32 rounded-full border-8 border-[#009986]/20" />

        {/* Animated spinning ring */}
        <div className="absolute w-32 h-32 rounded-full border-8 border-transparent border-t-[#009986] border-r-[#009986] animate-spin" />

      </div>

      {/* Message */}
      <div className="mt-10 text-center space-y-2">
        <p className="text-xl font-bold text-[#009986]">{message}</p>
        <p className="text-sm text-gray-500 font-medium">{submessage}</p>
      </div>

      {/* Animated bouncing dots */}
      <div className="flex items-center gap-2 mt-6">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="w-2.5 h-2.5 rounded-full bg-[#009986]"
            style={{
              animation: `loadingBounce 1.2s ease-in-out ${i * 0.2}s infinite`,
            }}
          />
        ))}
      </div>

      <style>{`
        @keyframes loadingBounce {
          0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
          40%            { transform: scale(1);   opacity: 1;   }
        }
      `}</style>
    </div>
  );
};

export default LoadingOverlay;