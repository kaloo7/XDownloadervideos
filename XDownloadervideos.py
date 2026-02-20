#!/usr/bin/env python3
"""
X (Twitter) Video Downloader
Downloads all videos from a public X/Twitter account and saves them to a ZIP file.

Requirements:
    pip install yt-dlp requests

Usage:
    python x_video_downloader.py <username> [options]

Examples:
    python x_video_downloader.py nasa
    python x_video_downloader.py nasa --output nasa_videos.zip
    python x_video_downloader.py nasa --limit 20
    python x_video_downloader.py nasa --cookies cookies.txt
"""

import argparse
import os
import sys
import zipfile
import tempfile
import shutil
import re
import subprocess
import json
from pathlib import Path


def check_yt_dlp():
    """Check if yt-dlp is installed."""
    try:
        import yt_dlp
        return True
    except ImportError:
        print("❌ yt-dlp is not installed.")
        print("   Install it with: pip install yt-dlp")
        return False


def get_user_tweets_via_ytdlp(username: str, limit: int = None, cookies_file: str = None) -> list[str]:
    """
    Use yt-dlp to collect tweet URLs that contain videos from a user's timeline.
    Returns a list of tweet URLs.
    """
    import yt_dlp

    profile_url = f"https://twitter.com/{username}"
    # Also try x.com
    profile_url_x = f"https://x.com/{username}"

    ydl_opts = {
        "quiet": True,
        "extract_flat": True,       # Don't download, just collect info
        "skip_download": True,
        "ignoreerrors": True,
        "playlist_items": f"1-{limit}" if limit else None,
    }

    if cookies_file:
        ydl_opts["cookiefile"] = cookies_file

    tweet_urls = []

    for url in [profile_url, profile_url_x]:
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info and "entries" in info:
                    for entry in info["entries"]:
                        if entry and entry.get("url"):
                            tweet_urls.append(entry["url"])
                    if tweet_urls:
                        break
        except Exception:
            continue

    return tweet_urls


def download_videos(username: str, output_zip: str, limit: int = None, cookies_file: str = None, quality: str = "best"):
    """
    Main function to download videos from an X/Twitter user and zip them.
    """
    if not check_yt_dlp():
        sys.exit(1)

    import yt_dlp

    print(f"\n🐦 X/Twitter Video Downloader")
    print(f"{'='*50}")
    print(f"👤 Username  : @{username}")
    print(f"📦 Output ZIP: {output_zip}")
    if limit:
        print(f"🔢 Limit     : {limit} videos")
    if cookies_file:
        print(f"🍪 Cookies   : {cookies_file}")
    print(f"{'='*50}\n")

    # Create a temp directory to store downloaded videos
    temp_dir = tempfile.mkdtemp(prefix=f"x_videos_{username}_")

    try:
        profile_url = f"https://x.com/{username}/media"

        # yt-dlp options for downloading
        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" if quality == "best" else quality,
            "outtmpl": os.path.join(temp_dir, "%(id)s.%(ext)s"),
            "ignoreerrors": True,
            "quiet": False,
            "no_warnings": False,
            "writeinfojson": False,
            "writethumbnail": False,
            "merge_output_format": "mp4",
        }

        if limit:
            ydl_opts["playlist_items"] = f"1-{limit}"

        if cookies_file:
            if not os.path.exists(cookies_file):
                print(f"⚠️  Warning: Cookies file '{cookies_file}' not found.")
            else:
                ydl_opts["cookiefile"] = cookies_file

        print(f"⬇️  Downloading videos from @{username}...")
        print(f"   Source: {profile_url}\n")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([profile_url])

        # Collect downloaded files
        downloaded_files = [
            f for f in os.listdir(temp_dir)
            if os.path.isfile(os.path.join(temp_dir, f))
               and f.lower().endswith((".mp4", ".webm", ".mkv", ".mov", ".avi"))
        ]

        if not downloaded_files:
            print("\n⚠️  No videos were downloaded.")
            print("   Possible reasons:")
            print("   • The account is private (use --cookies for authenticated access)")
            print("   • The account has no videos")
            print("   • Rate limiting by Twitter/X")
            print("   • Username is incorrect")
            print("\n   Tip: Export your browser cookies and use --cookies cookies.txt")
            return False

        print(f"\n✅ Downloaded {len(downloaded_files)} video(s)")

        # Create ZIP
        print(f"📦 Creating ZIP archive: {output_zip}")
        zip_path = os.path.abspath(output_zip)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for filename in sorted(downloaded_files):
                filepath = os.path.join(temp_dir, filename)
                # Rename files to be more descriptive: username_tweetid.ext
                new_name = f"{username}_{filename}"
                zf.write(filepath, arcname=new_name)
                size_mb = os.path.getsize(filepath) / (1024 * 1024)
                print(f"   📹 Added: {new_name} ({size_mb:.1f} MB)")

        zip_size_mb = os.path.getsize(zip_path) / (1024 * 1024)
        print(f"\n🎉 Done! ZIP file created: {zip_path}")
        print(f"   Total videos : {len(downloaded_files)}")
        print(f"   ZIP size     : {zip_size_mb:.1f} MB")
        return True

    finally:
        # Clean up temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(
        description="Download all videos from an X (Twitter) account and save them in a ZIP file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python x_video_downloader.py nasa
  python x_video_downloader.py nasa --output nasa_videos.zip
  python x_video_downloader.py nasa --limit 10
  python x_video_downloader.py nasa --cookies cookies.txt
  python x_video_downloader.py nasa --quality "bestvideo[height<=720]+bestaudio/best[height<=720]"

Notes:
  • Public accounts work without cookies for many cases.
  • Private accounts require authentication via --cookies.
  • To get a cookies file, use a browser extension like "Get cookies.txt LOCALLY"
    and export cookies from twitter.com while logged in.
  • yt-dlp must be installed: pip install yt-dlp
        """
    )

    parser.add_argument(
        "username",
        help="X/Twitter username (without @)"
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output ZIP filename (default: <username>_videos.zip)"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=None,
        help="Maximum number of videos to download (default: all)"
    )
    parser.add_argument(
        "--cookies", "-c",
        default=None,
        help="Path to cookies file for authenticated access (Netscape format)"
    )
    parser.add_argument(
        "--quality", "-q",
        default="best",
        help='Video quality format string for yt-dlp (default: "best")'
    )

    args = parser.parse_args()

    # Clean username
    username = args.username.lstrip("@").strip()
    if not re.match(r'^[A-Za-z0-9_]{1,50}$', username):
        print(f"❌ Invalid username: '{username}'")
        sys.exit(1)

    # Output filename
    output_zip = args.output or f"{username}_videos.zip"
    if not output_zip.endswith(".zip"):
        output_zip += ".zip"

    success = download_videos(
        username=username,
        output_zip=output_zip,
        limit=args.limit,
        cookies_file=args.cookies,
        quality=args.quality
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
