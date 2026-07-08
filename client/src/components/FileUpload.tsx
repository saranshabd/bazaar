"use client";

import { useRef, useState } from "react";

interface FileUploadProps {
  onUploaded: (file: File, cacheName: string) => void;
}

export function FileUpload({ onUploaded }: FileUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadingFile, setUploadingFile] = useState<File | null>(null);

  async function handleFile(file: File) {
    setError(null);

    if (!file.name.endsWith(".mp4")) {
      setError("Please upload an .mp4 video file.");
      return;
    }

    setUploadingFile(file);
    try {
      const opts = await import("@/lib/api").then((m) => m.cacheVideo(file));
      onUploaded(file, opts.cache_name);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Upload failed. Please try again.",
      );
    } finally {
      setUploadingFile(null);
    }
  }

  return (
    <div className="mx-auto flex w-full max-w-xl flex-col items-center gap-6">
      <div className="text-center">
        <h2 className="text-xl font-semibold tracking-tight">
          Upload your video
        </h2>
        <p className="mt-1 text-sm text-neutral-500 dark:text-neutral-400">
          We&apos;ll cache it so the focus group can review it frame-by-frame.
        </p>
      </div>

      <div
        role="button"
        tabIndex={0}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
        }}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={(e) => {
          e.preventDefault();
          setIsDragging(false);
        }}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          const file = e.dataTransfer.files?.[0];
          if (file) handleFile(file);
        }}
        className={[
          "flex w-full cursor-pointer flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed px-8 py-12 transition-colors",
          isDragging
            ? "border-blue-500 bg-blue-50 dark:bg-blue-950/30"
            : "border-neutral-300 hover:border-neutral-400 dark:border-neutral-700 dark:hover:border-neutral-600",
        ].join(" ")}
      >
        {uploadingFile ? (
          <div className="flex flex-col items-center gap-3">
            <div className="h-10 w-10 animate-spin rounded-full border-2 border-neutral-300 border-t-blue-500 dark:border-neutral-700 dark:border-t-blue-400" />
            <p className="text-sm font-medium text-neutral-600 dark:text-neutral-300">
              Uploading &amp; caching <span className="font-mono">{uploadingFile.name}</span>…
            </p>
            <p className="text-xs text-neutral-400">
              This can take ~3 minutes for large videos.
            </p>
          </div>
        ) : (
          <>
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-neutral-100 dark:bg-neutral-800">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
                className="h-6 w-6 text-neutral-500 dark:text-neutral-400"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5"
                />
              </svg>
            </div>
            <p className="text-sm font-medium">
              Drop your video here, or{" "}
              <span className="text-blue-600 dark:text-blue-400">browse</span>
            </p>
            <p className="text-xs text-neutral-400">MP4 files only</p>
          </>
        )}
      </div>

      {error && (
        <p className="text-sm text-red-600 dark:text-red-400" role="alert">
          {error}
        </p>
      )}

      <input
        ref={inputRef}
        type="file"
        accept="video/mp4"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleFile(file);
        }}
      />
    </div>
  );
}