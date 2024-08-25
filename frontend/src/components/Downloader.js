import React, { useState } from 'react';
import './Downloader.css';

const Downloader = () => {
    const [url, setUrl] = useState('');
    const [platform, setPlatform] = useState('youtube_video');

    const downloadContent = async () => {
        try {
            const response = await fetch('http://127.0.0.1:5000/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url, platform }),
            });

            if (response.ok) {
                const blob = await response.blob();
                const link = document.createElement('a');
                link.href = window.URL.createObjectURL(blob);
                link.download = platform === 'youtube_video' ? 'video.mp4' :
                    platform === 'youtube_audio' ? 'audio.mp3' :
                        platform === 'instagram' ? 'video.mp4' :
                            platform === 'facebook' ? 'video.mp4' :
                                platform === 'twitter' ? 'video.mp4' :
                                    platform === 'spotify' ? 'audio.mp3' :
                                        'file';  // Default name
                link.click();
            } else {
                const error = await response.json();
                alert('Error: ' + error.error);
            }
        } catch (error) {
            console.error('Download failed:', error);
            alert('Download failed. Check console for details.');
        }
    };

    return (
        <>
            <video id="backgroundVideo" autoPlay loop muted>
                <source src="/Untitled design.mp4" type="video/mp4" />
                Your browser does not support the video tag.
            </video>

            <div className="container">
                <h1>Media on Demand</h1>
                <select id="platform" value={platform} onChange={(e) => setPlatform(e.target.value)}>
                    <option value="youtube_video">YouTube Video</option>
                    <option value="youtube_audio">YouTube Audio</option>
                    <option value="instagram">Instagram Reel</option>
                    <option value="facebook">Facebook Video</option>
                    <option value="twitter">Twitter Video</option>
                    <option value="spotify">Spotify Audio</option>
                </select>
                <input
                    type="text"
                    id="videoUrl"
                    placeholder="Paste URL here"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                />
                <button onClick={downloadContent}>Download</button>
            </div>
        </>
    );
}

export default Downloader;
