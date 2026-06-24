import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

function SidebarItem({ active = false, icon, label, to = "#" }) {
  return (
    <Link
      to={to}
      className={`flex w-full items-center gap-2 rounded-full px-4 py-3 text-[18px] font-medium ${
        active ? "bg-[#E8FBF7] text-[#0FA99D]" : "text-[#0FA99D]"
      }`}
    >
      <span className="inline-flex h-6 w-6 items-center justify-center">
        {icon}
      </span>
      <span>{label}</span>
    </Link>
  );
}

// function DashboardIcon() {
//   return (
//     <svg
//       xmlns="http://www.w3.org/2000/svg"
//       viewBox="0 0 24 24"
//       fill="none"
//       stroke="#0FA99D"
//       strokeWidth="2.4"
//       strokeLinecap="round"
//       strokeLinejoin="round"
//       className="h-4 w-4 shrink-0"
//     >
//       <rect x="3" y="3" width="7" height="7" rx="1.5" />
//       <rect x="14" y="3" width="7" height="7" rx="1.5" />
//       <rect x="3" y="14" width="7" height="7" rx="1.5" />
//       <rect x="14" y="14" width="7" height="7" rx="1.5" />
//     </svg>
//   );
// }

function AnalyzeIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="-3 0 30 24"
      fill="none"
      stroke="#0FA99D"
      strokeWidth="2.4"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-5 w-5 shrink-0"
    >
      <path d="M20 16.5A4.5 4.5 0 0 0 17 8h-1.26A8 8 0 1 0 4 15.25" />
      <path d="M12 20V11" />
      <path d="m8.8 14.2 3.2-3.2 3.2 3.2" />
    </svg>
  );
}

function HistoryIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="#0FA99D"
      strokeWidth="2.4"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-4 w-4 shrink-0"
    >
      <path d="M3 12a9 9 0 1 0 3-6.7" />
      <path d="M3 4v5h5" />
      <path d="M12 7v5l3 2" />
    </svg>
  );
}

function UploadCloudIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="-3 0 30 24"
      fill="none"
      stroke="#9CA3AF"
      strokeWidth="2.4"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-8 w-8 shrink-0"
    >
      <path d="M20 16.5A4.5 4.5 0 0 0 17 8h-1.26A8 8 0 1 0 4 15.25" />
      <path d="M12 20V11" />
      <path d="m8.8 14.2 3.2-3.2 3.2 3.2" />
    </svg>
  );
}

function FileVideoIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="#9CA3AF"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-4 w-4"
    >
      <rect x="3" y="5" width="15" height="14" rx="2" />
      <path d="m18 10 3-2v8l-3-2" />
    </svg>
  );
}

function SmallUploadStatus() {
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-[#ECFDF3] px-2 py-1 text-[8px] font-medium text-[#16A34A]">
      <span className="h-2 w-2 rounded-full border border-[#16A34A]" />
      Uploaded
    </span>
  );
}

function JobDetailsCard({ roleName, setRoleName }) {
  return (
    <div className="rounded-[18px] bg-white px-6 py-5 shadow-sm">
      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#F3F4F6] text-[#A1A1AA]">
          🎁
        </div>
        <h3 className="text-[18px] font-bold text-[#7C7C7C]">Job Details</h3>
      </div>

      <label className="mb-2 block text-[14px] text-[#7C7C7C]">
        Target Role Name
      </label>
      <input
        type="text"
        value={roleName}
        onChange={(e) => setRoleName(e.target.value)}
        placeholder="e.g. Senior frontend developer"
        className="h-[42px] w-full rounded-full border border-[#D1D5DB] bg-[#F5F5F5] px-4 text-[12px] outline-none placeholder:text-[#B0B0B0]"
      />
    </div>
  );
}

function SliderRow({ label, value, onChange }) {
  return (
    <div>
      <div className="mb-1 flex items-center justify-between">
        <span className="text-[14px] text-[#7C7C7C]">{label}</span>
        <span className="text-[14px] font-semibold text-[#333]">%{value}</span>
      </div>

      <input
        type="range"
        min="0"
        max="100"
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="slider-teal h-[6px] w-full cursor-pointer appearance-none rounded-full bg-[#CDEDEA]"
      />
    </div>
  );
}

function AnalysisWeightsCard({
  weights,
  setWeights,
  threshold,
  setThreshold,
  isRecruiter,
  weightError,
}) {
  const total = Object.values(weights).reduce((sum, val) => sum + val, 0);

  const updateWeight = (key, nextValue) => {
    setWeights((prev) => ({
      ...prev,
      [key]: nextValue,
    }));
  };

  return (
    <div className="rounded-[18px] bg-white px-6 py-5 shadow-sm">
      <div className="mb-6 flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#F3F4F6] text-[#A1A1AA]">
          🎚
        </div>
        <h3 className="text-[18px] font-bold text-[#7C7C7C]">
          Analysis Weights
        </h3>
      </div>

      <div className="space-y-5">
        <SliderRow
          label="Fillers Usage"
          value={weights.fillers}
          onChange={(v) => updateWeight("fillers", v)}
        />
        <SliderRow
          label="Pause Duration"
          value={weights.pause}
          onChange={(v) => updateWeight("pause", v)}
        />
        <SliderRow
          label="Emotion Intensity"
          value={weights.emotion}
          onChange={(v) => updateWeight("emotion", v)}
        />
        <SliderRow
          label="Energy Level"
          value={weights.energy}
          onChange={(v) => updateWeight("energy", v)}
        />
        <SliderRow
          label="Eye Contact"
          value={weights.eyeContact}
          onChange={(v) => updateWeight("eyeContact", v)}
        />
        <SliderRow
          label="Grammar Accuracy"
          value={weights.grammar}
          onChange={(v) => updateWeight("grammar", v)}
        />
      </div>

      <div className="mt-6 rounded-xl bg-[#F8FAFA] px-4 py-3 text-center">
        <div
          className={`text-[14px] font-semibold ${
            total === 100 ? "text-[#0FA99D]" : "text-red-500"
          }`}
        >
          Total: {total}%
        </div>
        {weightError && (
          <p className="mt-2 text-[13px] text-red-500">{weightError}</p>
        )}
      </div>

      {isRecruiter && (
        <div className="mt-6 flex items-center justify-center gap-3">
          <span className="text-[14px] text-[#7C7C7C]">Threshold</span>
          <input
            type="number"
            min="0"
            max="100"
            value={threshold}
            onChange={(e) => {
              let v = Number(e.target.value);
              if (Number.isNaN(v)) v = 0;
              if (v < 0) v = 0;
              if (v > 100) v = 100;
              setThreshold(v);
            }}
            className="h-[32px] w-[60px] rounded-md border border-[#D1D5DB] bg-[#F5F5F5] px-2 text-center text-[13px] outline-none"
          />
        </div>
      )}
    </div>
  );
}

function UploadDropzone({
  onFilesAdded,
  isDragging,
  setIsDragging,
  inputRef,
  isRecruiter,
}) {
  const handleFiles = (fileList) => {
    const allFiles = Array.from(fileList || []);
    const videoFiles = allFiles.filter((file) =>
      file.type.startsWith("video/"),
    );

    if (!videoFiles.length) return;

    if (isRecruiter) {
      onFilesAdded(videoFiles);
    } else {
      onFilesAdded([videoFiles[0]]);
    }
  };

  return (
    <div
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setIsDragging(false);
        handleFiles(e.dataTransfer.files);
      }}
      className={`flex min-h-[150px] cursor-pointer flex-col items-center justify-center rounded-[18px] border bg-white p-5 text-center shadow-sm transition ${
        isDragging
          ? "border-[#0FA99D] bg-[#F0FDFA]"
          : "border-dashed border-[#AFAFAF]"
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        accept="video/*"
        multiple={isRecruiter}
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />

      <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-full bg-[#F3F4F6]">
        <UploadCloudIcon />
      </div>

      <h3 className="text-[18px] font-bold text-[#7C7C7C]">
        Drag & drop candidates videos
      </h3>
      <p className="mt-3 text-[13px] text-[#A1A1AA]">
        Upload MP4, MOV, or WEBM files.
      </p>

      {isRecruiter ? (
        <p className="text-[13px] text-[#A1A1AA]">
          You can upload up to 300 videos at once for bulk processing.
        </p>
      ) : (
        <p className="text-[13px] text-[#A1A1AA]">
          You can upload only one video.
        </p>
      )}

      <p className="mt-3 text-[12px] font-medium text-[#0FA99D]">
        Click here to browse files
      </p>
    </div>
  );
}

function UploadedFileRow({ file, onRemove }) {
  return (
    <div className="flex items-center justify-between rounded-[14px] border border-[#E5E7EB] bg-white px-4 py-3">
      <div className="flex min-w-0 items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-full border border-[#E5E7EB]">
          <FileVideoIcon />
        </div>
        <span className="truncate text-[14px] font-medium text-[#6B7280]">
          {file.name}
        </span>
      </div>

      <div className="ml-4 flex items-center gap-4">
        <SmallUploadStatus />
        <button
          type="button"
          className="text-[#D1D5DB]"
          onClick={() => onRemove(file.id)}
        >
          ✕
        </button>
      </div>
    </div>
  );
}

function ReadyToProcessCard({ files, clearAllFiles, removeFile }) {
  return (
    <div className="rounded-[18px] bg-white px-5 py-5 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h3 className="text-[18px] font-bold text-[#7C7C7C]">
            Ready to process
          </h3>
          <span className="flex h-5 w-5 items-center justify-center rounded-full bg-[#E5E7EB] text-[11px] text-[#7C7C7C]">
            {files.length}
          </span>
        </div>
        <button
          type="button"
          className="text-[12px] text-[#7C7C7C]"
          onClick={clearAllFiles}
          disabled={!files.length}
        >
          Clear all
        </button>
      </div>

      <div className="space-y-3">
        {files.length ? (
          files
            .slice(0, 4)
            .map((file) => (
              <UploadedFileRow
                key={file.id}
                file={file}
                onRemove={removeFile}
              />
            ))
        ) : (
          <div className="rounded-[14px] border border-dashed border-[#E5E7EB] px-4 py-8 text-center text-[13px] text-[#A1A1AA]">
            No videos uploaded yet
          </div>
        )}
      </div>

      {files.length > 4 && (
        <div className="mt-4 text-center text-[13px] text-[#7C7C7C]">
          View more
        </div>
      )}
    </div>
  );
}

function StartProcessingButton({ disabled, onClick, loading }) {
  return (
    <button
      type="button"
      disabled={disabled || loading}
      onClick={onClick}
      className={`flex h-[58px] w-full items-center justify-center gap-3 rounded-[14px] text-[18px] font-bold text-white shadow-sm ${
        disabled || loading
          ? "cursor-not-allowed bg-[#9FDCD5]"
          : "bg-[#0FA99D] hover:bg-[#0c8f85]"
      }`}
    >
      <span className="text-[16px]">{loading ? "⏳" : "▶"}</span>
      {loading ? "Processing..." : "Start Processing"}
    </button>
  );
}

function ProcessVideoPage() {
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);
  const profileMenuRef = useRef(null);

  const navigate = useNavigate();

  const [roleName, setRoleName] = useState("");
  const [threshold, setThreshold] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [weightError, setWeightError] = useState("");

  const inputRef = useRef(null);

  const role = localStorage.getItem("role") || "";
  const name = localStorage.getItem("name") || "";
  const token = localStorage.getItem("access_token") || "";
  const handleLogout = () => {
    localStorage.clear();
    navigate("/signin");
  };

  const trimmedName = name.trim();

  const profileChar =
    trimmedName.split(" ").length >= 2
      ? trimmedName
          .split(" ")
          .slice(0, 2)
          .map((n) => n[0])
          .join("")
          .toUpperCase()
      : trimmedName.slice(0, 2).toUpperCase();

  const isRecruiter = role === "RECRUITER";

  const [weights, setWeights] = useState({
    fillers: 30,
    pause: 20,
    emotion: 20,
    energy: 10,
    eyeContact: 10,
    grammar: 10,
  });

  const [files, setFiles] = useState([]);

  const onFilesAdded = (newFiles) => {
    const prepared = newFiles.map((file, index) => ({
      id: `${file.name}-${file.size}-${file.lastModified}-${Date.now()}-${index}`,
      name: file.name,
      baseName: file.name.replace(/\.[^/.]+$/, ""),
      raw: file,
    }));

    if (isRecruiter) {
      setFiles((prev) => [...prev, ...prepared]);
    } else {
      setFiles(prepared.slice(0, 1));
    }
  };

  const clearAllFiles = () => setFiles([]);

  const removeFile = (id) =>
    setFiles((prev) => prev.filter((file) => file.id !== id));

  const totalWeight = useMemo(
    () => Object.values(weights).reduce((sum, value) => sum + value, 0),
    [weights],
  );

  useEffect(() => {
    function handleClickOutside(event) {
      if (
        profileMenuRef.current &&
        !profileMenuRef.current.contains(event.target)
      ) {
        setProfileMenuOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  useEffect(() => {
    if (totalWeight === 100) {
      setWeightError("");
    } else {
      setWeightError("Weights must sum up to 100%");
    }
  }, [totalWeight]);

  const handleStartProcessing = async () => {
    if (!files.length) return;

    if (totalWeight !== 100) {
      setWeightError("Weights must sum up to 100%");
      return;
    }

    setWeightError("");

    try {
      setLoading(true);

      const formData = new FormData();

      files.forEach((file) => {
        formData.append("files", file.raw);
        formData.append("video_names", file.baseName);
      });

      formData.append("fillers_weight", (weights.fillers / 100).toFixed(2));
      formData.append("pause_rate_weight", (weights.pause / 100).toFixed(2));
      formData.append("emotion_weight", (weights.emotion / 100).toFixed(2));
      formData.append("energy_weight", (weights.energy / 100).toFixed(2));
      formData.append(
        "eye_contact_weight",
        (weights.eyeContact / 100).toFixed(2),
      );
      formData.append("grammar_weight", (weights.grammar / 100).toFixed(2));

      const response = await fetch(
        "http://127.0.0.1:8000/users/videos/upload",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        },
      );

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(errText || "Failed to upload videos");
      }

      const data = await response.json();

      localStorage.setItem("candidateReportData", JSON.stringify(data));

      navigate("/candidate-history", { state: { reportData: data } });
    } catch (error) {
      console.error("Upload error:", error);
      alert(`Failed to process video(s).\n${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full bg-[#E8E6E2]">
      <style>{`
        .slider-teal::-webkit-slider-thumb {
          appearance: none;
          width: 16px;
          height: 16px;
          border-radius: 9999px;
          background: #0FA99D;
          cursor: pointer;
          border: none;
          margin-top: -5px;
        }
        .slider-teal::-moz-range-thumb {
          width: 16px;
          height: 16px;
          border-radius: 9999px;
          background: #0FA99D;
          cursor: pointer;
          border: none;
        }
      `}</style>

      <header className="flex h-[72px] items-center justify-between border-b border-[#D8D8D8] bg-white px-6">
        <div className="flex items-center gap-10">
          <div className="text-[34px] font-normal text-[#0FA99D] [font-family:'Pacifico',Helvetica]">
            Interview me
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="border-r border-[#E5E7EB] pr-3 text-right">
            <div className="text-[12px] font-semibold text-[#374151]">
              {name}
            </div>
            <div className="text-[10px] text-[#9CA3AF]">
              {isRecruiter ? "Recruiter Admin" : "User"}
            </div>
          </div>
          <div ref={profileMenuRef} className="relative">
            <button
              type="button"
              onClick={() => setProfileMenuOpen((prev) => !prev)}
              className="flex h-8 w-8 cursor-pointer items-center justify-center rounded-full bg-[#DDF8F2] text-[10px] font-bold text-[#0FA99D] transition hover:opacity-80"
            >
              {profileChar || "NA"}
            </button>

            {profileMenuOpen && (
              <div className="absolute right-0 mt-2 w-[170px] rounded-[14px] border border-[#E5E7EB] bg-white py-2 shadow-lg z-50">
                <button
                  type="button"
                  onClick={handleLogout}
                  className="block w-full px-4 py-2 text-left text-[14px] font-medium text-[#374151] hover:bg-[#F3F4F6]"
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="flex">
        <aside className="min-h-[calc(100vh-72px)] w-[240px] bg-white">
          <nav className="mt-10 flex flex-col gap-2 px-3">
            {/* <SidebarItem icon={<DashboardIcon />} label="Dashboard" to="/" /> */}
            <SidebarItem
              active
              icon={<AnalyzeIcon />}
              label="Analyze Interview"
              to="/process-video"
            />
            <SidebarItem icon={<HistoryIcon />} label="History" to="/candidate-history" />
          </nav>
        </aside>

        <main className="flex-1 bg-[#E8E6E2] px-6 py-6">
          <div className="mb-6">
            <h1 className="text-[24px] font-bold text-[#0FA99D]">
              New Processing
            </h1>

            {isRecruiter && (
              <p className="mt-1 text-[14px] text-[#7C7C7C]">
                Upload candidate videos and configure AI analysis parameters.
              </p>
            )}
          </div>

          <div className="grid grid-cols-[1fr_1.2fr] gap-6">
            <div className="space-y-5">
              <JobDetailsCard roleName={roleName} setRoleName={setRoleName} />
              <AnalysisWeightsCard
                weights={weights}
                setWeights={setWeights}
                threshold={threshold}
                setThreshold={setThreshold}
                isRecruiter={isRecruiter}
                weightError={weightError}
              />
            </div>

            <div className="space-y-5">
              <UploadDropzone
                onFilesAdded={onFilesAdded}
                isDragging={isDragging}
                setIsDragging={setIsDragging}
                inputRef={inputRef}
                isRecruiter={isRecruiter}
              />
              <ReadyToProcessCard
                files={files}
                clearAllFiles={clearAllFiles}
                removeFile={removeFile}
              />
              <StartProcessingButton
                disabled={!files.length}
                onClick={handleStartProcessing}
                loading={loading}
              />
            </div>
          </div>

          <footer className="mt-4 text-center text-[11px] text-[#9CA3AF]">
            © 2026 Interview Me. All rights reserved.
          </footer>
        </main>
      </div>
    </div>
  );
}

export default ProcessVideoPage;
