import { useState, useRef } from 'react';
import Webcam from 'react-webcam';
import { uploadVideo } from '../../services/api';
export default function VideoRecorder({ onUploadComplete }) {
  const webcamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const [recording, setRecording] = useState(false);
  const [recordedChunks, setRecordedChunks] = useState([]);
  const [caption, setCaption] = useState('');
  const [uploading, setUploading] = useState(false);
  const startRecording = () => {
    setRecording(true);
    mediaRecorderRef.current = new MediaRecorder(webcamRef.current.stream, {
      mimeType: 'video/webm'
    });

    mediaRecorderRef.current.addEventListener('dataavailable', ({ data }) => {
      if (data.size > 0) {
        setRecordedChunks(prev => [...prev, data]);
      }
    });

    mediaRecorderRef.current.start();

    // Auto-stop after 60 seconds
    setTimeout(() => {
      if (mediaRecorderRef.current?.state === 'recording') {
        stopRecording();
      }
    }, 60000);
  };
  const stopRecording = () => {
    mediaRecorderRef.current.stop();
    setRecording(false);
  };
  const handleUpload = async () => {
    if (recordedChunks.length === 0) return;

    setUploading(true);

    const blob = new Blob(recordedChunks, { type: 'video/webm' });
    const formData = new FormData();
    formData.append('file', blob, 'video.webm');
    formData.append('caption', caption);

    try {
      const result = await uploadVideo(formData);
      onUploadComplete(result);
    } catch (error) {
      alert('Upload failed: ' + error.message);
    } finally {
      setUploading(false);
    }
  };
  return (
    <div className="max-w-md mx-auto p-4 space-y-4">
      <Webcam
        ref={webcamRef}
        audio={true}
        videoConstraints={{ facingMode: 'user' }}
        className="w-full rounded-lg"
      />

      <div className="flex gap-4">
        {!recording ? (
          <button
            onClick={startRecording}
            className="flex-1 bg-red-600 text-white py-3 rounded-full"
          >
            Start Recording
          </button>
        ) : (
          <button
            onClick={stopRecording}
            className="flex-1 bg-gray-600 text-white py-3 rounded-full"
          >
            Stop (60s max)
          </button>
        )}
      </div>

      {recordedChunks.length > 0 && (
        <div className="space-y-4">
          <input
            type="text"
            placeholder="Add a caption..."
            value={caption}
            onChange={(e) => setCaption(e.target.value)}
            className="w-full px-4 py-2 border rounded-lg"
          />

          <button
            onClick={handleUpload}
            disabled={uploading}
            className="w-full bg-green-600 text-white py-3 rounded-full disabled:bg-gray-400"
          >
            {uploading ? 'Uploading...' : 'Post Video'}
          </button>
        </div>
      )}
    </div>
  );
}
export default function VideoPlayer({ muxPlaybackId, caption, author }) {
  const videoUrl = `https://stream.mux.com/${muxPlaybackId}.m3u8`;

  return (
    <div className="relative h-screen w-full bg-black">
      <video
        src={videoUrl}
        controls
        autoPlay
        loop
        playsInline
        className="h-full w-full object-contain"
      />

      <div className="absolute bottom-20 left-0 right-0 p-4 text-white">
        <p className="font-semibold">@{author}</p>
        <p className="mt-2">{caption}</p>
      </div>
    </div>
  );
}
