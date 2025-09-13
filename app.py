mport asyncio
import telebot
import requests
import json
import os
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from urllib.parse import urlparse
import tempfile
from PIL import Image
import io

# Bot Token
BOT_TOKEN = "8440949188:AAEGwF-XZjOXTDjv6Fz-iNkv4fVnXVDCjVE"
bot = telebot.TeleBot(BOT_TOKEN)

# API URLs
TIKTOK_API_URL = "https://sokii-tiktok-api.vercel.app/download?url="
YOUTUBE_VIDEO_API_URL = "https://you-tube-sokii-v2.vercel.app/video?url="
YOUTUBE_AUDIO_API_URL = "https://you-tube-sokii-v2.vercel.app/audio?url="
API_KEY = "demo_key"

# Required channels
REQUIRED_CHANNELS = ['@Sell_Acc_g', '@growaga156237']
CHANNEL_INVITE_LINK = "https://t.me/addlist/oLtulVwTOPthNzFl"
VERIFICATION_IMAGE = "https://ar-hosting.pages.dev/1745850609055.jpg"

# Maximum images per media group
MAX_IMAGES_PER_GROUP = 10

def is_tiktok_url(url):
    """Check if URL is a valid TikTok URL"""
    tiktok_domains = ['tiktok.com', 'www.tiktok.com', 'vm.tiktok.com', 'vt.tiktok.com']
    try:
        parsed = urlparse(url)
        return any(domain in parsed.netloc for domain in tiktok_domains)
    except Exception as e:
        print(f"Error checking TikTok URL: {e}")
        return False

def is_youtube_url(url):
    """Check if URL is a valid YouTube URL"""
    youtube_domains = ['youtube.com', 'www.youtube.com', 'youtu.be']
    try:
        parsed = urlparse(url)
        return any(domain in parsed.netloc for domain in youtube_domains)
    except Exception as e:
        print(f"Error checking YouTube URL: {e}")
        return False

def get_tiktok_data(url):
    """Fetch TikTok data from API"""
    try:
        response = requests.get(TIKTOK_API_URL + url, timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error fetching TikTok data: {e}")
        return None

def get_youtube_video_data(url):
    """Fetch YouTube video data from API"""
    try:
        response = requests.get(f"{YOUTUBE_VIDEO_API_URL}{url}&key={API_KEY}", timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error fetching YouTube video data: {e}")
        return None

def get_youtube_audio_data(url):
    """Fetch YouTube audio data from API"""
    try:
        response = requests.get(f"{YOUTUBE_AUDIO_API_URL}{url}&key={API_KEY}", timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error fetching YouTube audio data: {e}")
        return None

def download_file(url, file_path):
    """Download file from URL"""
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False

def create_inline_keyboard(content_type, has_audio=False):
    """Create inline keyboard for download options"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    if content_type == "tiktok_video":
        keyboard.add(
            InlineKeyboardButton("🎬 វីដេអូ HD (គ្មាន Watermark)", callback_data="video_no_wm"),
            InlineKeyboardButton("🎬 វីដេអូ HD (មាន Watermark)", callback_data="video_with_wm")
        )
        if has_audio:
            keyboard.add(InlineKeyboardButton("🎵 សំឡេង", callback_data="audio_only"))
    elif content_type == "tiktok_image":
        keyboard.add(
            InlineKeyboardButton("🖼️ ទាញយករូបភាព", callback_data="download_images"),
            InlineKeyboardButton("🎵 សំឡេង", callback_data="audio_only")
        )
    elif content_type == "youtube":
        keyboard.add(
            InlineKeyboardButton("🎬 វីដេអូ HD", callback_data="youtube_video"),
            InlineKeyboardButton("🎵 សំឡេង", callback_data="youtube_audio")
        )
    
    return keyboard

def create_verification_keyboard():
    """Create inline keyboard for channel verification"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📢 ចូលរួម Channels", url=CHANNEL_INVITE_LINK),
        InlineKeyboardButton("✅ ផ្ទៀងផ្ទាត់សមាជិកភាព", callback_data="verify_membership")
    )
    return keyboard

def format_tiktok_engagement_stats(engagement):
    """Format TikTok engagement statistics"""
    stats = "📊 ស្ថិតិ:\n"
    stats += f"👁️ ចំនួនមើល: {engagement.get('play_count', 0):,}\n"
    stats += f"❤️ ចូលចិត្ត: {engagement.get('digg_count', 0):,}\n"
    stats += f"💬 មតិ: {engagement.get('comment_count', 0):,}\n"
    stats += f"🔄 ចែករំលែក: {engagement.get('share_count', 0):,}\n"
    stats += f"⭐ រក្សាទុក: {engagement.get('collect_count', 0):,}\n"
    stats += f"⬇️ ទាញយក: {engagement.get('download_count', 0):,}"
    return stats

def send_tiktok_video_info(chat_id, data):
    """Send TikTok video information with download options"""
    try:
        video_data = data['data']
        author = video_data['author']
        post_info = video_data['post_info']
        engagement = video_data['engagement']
        
        # Create info message
        info_text = "🎬 វីដេអូ TikTok\n\n"
        info_text += f"👤 អ្នកបង្កើត: @{author['username']} ({author['nickname']})\n"
        info_text += f"📝 ចំណងជើង: {post_info['title']}\n"
        info_text += f"⏱️ រយៈពេល: {post_info['duration']}\n"
        info_text += f"📅 បង្កើត: {post_info['create_time']}\n"
        info_text += f"🌍 តំបន់: {post_info['region']}\n\n"
        info_text += format_tiktok_engagement_stats(engagement)
        
        # Send cover image with info
        cover_url = video_data['covers']['cover']
        keyboard = create_inline_keyboard("tiktok_video", True)
        
        bot.send_photo(
            chat_id=chat_id,
            photo=cover_url,
            caption=info_text,
            reply_markup=keyboard
        )
        
        return True
    except Exception as e:
        print(f"Error sending TikTok video info: {e}")
        return False

def send_tiktok_image_info(chat_id, data):
    """Send TikTok image post information with download options"""
    try:
        image_data = data['data']
        author = image_data['author']
        post_info = image_data['post_info']
        engagement = image_data['engagement']
        
        # Create info message
        info_text = "🖼️ រូបភាព TikTok\n\n"
        info_text += f"👤 អ្នកបង្កើត: @{author['username']} ({author['nickname']})\n"
        info_text += f"📝 ចំណងជើង: {post_info['title']}\n"
        info_text += f"🖼️ ចំនួនរូបភាព: {image_data['image_downloads']['total_images']}\n"
        info_text += f"📅 បង្កើត: {post_info['create_time']}\n"
        info_text += f"🌍 តំបន់: {post_info['region']}\n\n"
        info_text += format_tiktok_engagement_stats(engagement)
        
        # Send cover image with info
        cover_url = image_data['covers']['cover']
        keyboard = create_inline_keyboard("tiktok_image", True)
        
        bot.send_photo(
            chat_id=chat_id,
            photo=cover_url,
            caption=info_text,
            reply_markup=keyboard
        )
        
        return True
    except Exception as e:
        print(f"Error sending TikTok image info: {e}")
        return False

def send_youtube_info(chat_id, data):
    """Send YouTube video/audio information with download options"""
    try:
        video_data = data['data']
        
        # Create info message
        info_text = "🎬 វីដេអូ YouTube\n\n"
        info_text += f"👤 អ្នកបង្កើត: {video_data['author']}\n"
        info_text += f"📝 ចំណងជើង: {video_data['title']}\n"
        info_text += f"⏱️ រយៈពេល: {video_data['duration']} វិនាទី\n"
        info_text += f"🆔 Video ID: {video_data['video_id']}\n"
        info_text += f"🔗 URL: {video_data['original_url']}\n"
        
        # Send thumbnail with info
        thumbnail_url = video_data['thumbnail']
        keyboard = create_inline_keyboard("youtube", True)
        
        bot.send_photo(
            chat_id=chat_id,
            photo=thumbnail_url,
            caption=info_text,
            reply_markup=keyboard
        )
        
        return True
    except Exception as e:
        print(f"Error sending YouTube info: {e}")
        return False

def send_tiktok_images_as_groups(chat_id, images):
    """Send TikTok images in groups (max 10 per group)"""
    try:
        total_images = len(images)
        groups = []
        
        for i in range(0, total_images, MAX_IMAGES_PER_GROUP):
            group = images[i:i + MAX_IMAGES_PER_GROUP]
            groups.append(group)
        
        for group_idx, group in enumerate(groups, 1):
            media_group = []
            
            for idx, image in enumerate(group):
                try:
                    # Calculate global index
                    global_idx = (group_idx - 1) * MAX_IMAGES_PER_GROUP + idx + 1
                    
                    caption = ""
                    if idx == 0:  # First image in group gets caption
                        if len(groups) > 1:
                            caption = f"🖼️ ក្រុម {group_idx}/{len(groups)} (រូបភាព {global_idx}-{min(global_idx + len(group) - 1, total_images)})"
                        else:
                            caption = f"🖼️ រូបភាព TikTok (សរុប {total_images})"
                    
                    media_group.append(telebot.types.InputMediaPhoto(
                        media=image['url'],
                        caption=caption
                    ))
                    
                except Exception as e:
                    print(f"Error adding image to group: {e}")
                    continue
            
            if media_group:
                try:
                    bot.send_media_group(chat_id, media_group)
                    time.sleep(1)  # Rate limiting
                except Exception as e:
                    print(f"Error sending media group: {e}")
                    # Fallback: send images individually
                    for image in group:
                        try:
                            bot.send_photo(chat_id, image['url'])
                            time.sleep(0.5)
                        except Exception as e:
                            print(f"Error sending individual image: {e}")
                            continue
        
        return True
    except Exception as e:
        print(f"Error sending TikTok images as groups: {e}")
        return False

def check_channel_membership(user_id, chat_id, message_id=None):
    """Check if user is a member of required channels"""
    try:
        for channel in REQUIRED_CHANNELS:
            member = bot.get_chat_member(channel, user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                # Send join message with image and verification button
                join_message = "📢 សូមចូលរួម Channels របស់យើងដើម្បីប្រើប្រាស់កម្មវិធីទាញយក!\n\n"
                join_message += "ចុចប៊ូតុងខាងក្រោមដើម្បីចូលរួម និងផ្ទៀងផ្ទាត់សមាជិកភាពរបស់អ្នក។"
                
                bot.send_photo(
                    chat_id=chat_id,
                    photo=VERIFICATION_IMAGE,
                    caption=join_message,
                    reply_markup=create_verification_keyboard()
                )
                if message_id:
                    bot.delete_message(chat_id, message_id)
                return False
        return True
    except Exception as e:
        print(f"Error checking channel membership: {e}")
        return False

# Store data temporarily
user_data = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = """
🎉 សូមស្វាគមន៍មកកាន់ Premium TikTok & YouTube Downloader Bot!

🚀 លក្ខណៈពិសេស:
• ទាញយកវីដេអូ TikTok និង YouTube គុណភាព HD
• ជម្រើសគ្មាន Watermark (សម្រាប់ TikTok)
• ទាញយករូបភាព TikTok គុណភាពខ្ពស់
• ស្រង់សំឡេងចេញពីវីដេអូ
• មើលស្ថិតិអន្តរកម្ម (សម្រាប់ TikTok)

📋 របៀបប្រើ:
1. ចូលរួម Channels ដែលតម្រូវ
2. ផ្ញើ URL របស់ TikTok ឬ YouTube
3. ជ្រើសរើសជម្រើសទាញយក
4. រីករាយជាមួយមាតិការបស់អ្នក!

💫 ទម្រង់ដែលគាំទ្រ:
• វីដេអូ: MP4 (គុណភាព HD)
• រូបភាព: JPEG (គុណភាពខ្ពស់)
• សំឡេង: MP3 (គុណភាពដើម)

🔗 ផ្ញើ URL ណាមួយរបស់ TikTok ឬ YouTube ដើម្បីចាប់ផ្តើម!
    """
    
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.strip()
    
    if not (is_tiktok_url(text) or is_youtube_url(text)):
        bot.reply_to(message, "❌ សូមផ្ញើ URL របស់ TikTok ឬ YouTube ដែលត្រឹមត្រូវ\n\nឧទាហរណ៍:\n- TikTok: https://www.tiktok.com/@username/video/1234567890\n- YouTube: https://youtu.be/Of45hunl_98")
        return
    
    # Check channel membership
    if not check_channel_membership(message.from_user.id, message.chat.id, message.message_id):
        return
    
    # Send processing message
    processing_msg = bot.reply_to(message, "🔄 កំពុងដំណើរការ URL...\nសូមរង់ចាំខណៈពេលយើងទាញយកព័ត៌មានមាតិកា។")
    
    try:
        data = None
        content_type = None
        
        if is_tiktok_url(text):
            # Get TikTok data
            data = get_tiktok_data(text)
            if data and data.get('success'):
                content_type = data['data']['content_type']
        elif is_youtube_url(text):
            # Get YouTube video data
            data = get_youtube_video_data(text)
            if data and data.get('status') == 'success':
                content_type = 'youtube'
        
        if not data or (is_tiktok_url(text) and not data.get('success')) or (is_youtube_url(text) and data.get('status') != 'success'):
            bot.edit_message_text(
                "❌ បរាជ័យក្នុងការទាញយកទិន្នន័យ។ សូមពិនិត្យ URL និងព្យាយាមម្តងទៀត។",
                chat_id=message.chat.id,
                message_id=processing_msg.message_id
            )
            return
        
        # Store data for callback handling
        user_data[message.chat.id] = data
        
        # Delete processing message
        bot.delete_message(message.chat.id, processing_msg.message_id)
        
        # Send appropriate info based on content type
        if content_type == "video":
            if not send_tiktok_video_info(message.chat.id, data):
                bot.send_message(message.chat.id, "❌ កំហុសក្នុងការបង្ហាញព័ត៌មានវីដេអូ")
        elif content_type == "image":
            if not send_tiktok_image_info(message.chat.id, data):
                bot.send_message(message.chat.id, "❌ កំហុសក្នុងការបង្ហាញព័ត៌មានរូបភាព")
        elif content_type == "youtube":
            if not send_youtube_info(message.chat.id, data):
                bot.send_message(message.chat.id, "❌ កំហុសក្នុងការបង្ហាញព័ត៌មាន YouTube")
        else:
            bot.send_message(message.chat.id, "❌ ប្រភេទមាតិកាមិនគាំទ្រ")
            
    except Exception as e:
        bot.edit_message_text(
            f"❌ កំហុសកើតឡើងអំឡុងពេលដំណើរការសំណើរបស់អ្នក: {str(e)}",
            chat_id=message.chat.id,
            message_id=processing_msg.message_id
        )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    
    if call.data == "verify_membership":
        if check_channel_membership(call.from_user.id, chat_id, call.message.message_id):
            bot.answer_callback_query(call.id, "✅ បានផ្ទៀងផ្ទាត់សមាជិកភាព! សូមផ្ញើ URL ដើម្បីបន្ត។")
        else:
            bot.answer_callback_query(call.id, "❌ សូមចូលរួម Channels ទាំងអស់ជាមុនសិន�।")
        return
    
    if chat_id not in user_data:
        bot.answer_callback_query(call.id, "❌ ទិន្នន័យផុតកំណត់។ សូមផ្ញើ URL ម្តងទៀត។")
        return
    
    # Check channel membership before processing download
    if not check_channel_membership(call.from_user.id, chat_id):
        return
    
    data = user_data[chat_id]
    
    try:
        if call.data == "video_no_wm":
            # Send TikTok video without watermark
            bot.answer_callback_query(call.id, "🔄 កំពុងផ្ញើវីដេអូគ្មាន Watermark...")
            video_url = data['data']['video_downloads']['no_watermark']['url']
            
            # Send video
            bot.send_video(
                chat_id=chat_id,
                video=video_url,
                caption="🎬 វីដេអូ TikTok (គ្មាន Watermark)"
            )
            
        elif call.data == "video_with_wm":
            # Send TikTok video with watermark
            bot.answer_callback_query(call.id, "🔄 កំពុងផ្ញើវីដេអូមាន Watermark...")
            video_url = data['data']['video_downloads']['with_watermark']['url']
            
            # Send video
            bot.send_video(
                chat_id=chat_id,
                video=video_url,
                caption="🎬 វីដេអូ TikTok (មាន Watermark)"
            )
            
        elif call.data == "audio_only":
            # Send TikTok audio
            bot.answer_callback_query(call.id, "🔄 កំពុងផ្ញើសំឡេង...")
            
            if data['data']['content_type'] == "video":
                audio_url = data['data']['video_downloads']['audio_only']['url']
            else:
                # For image posts, there might be background music
                audio_url = data['data'].get('music_info', {}).get('play_url', '')
            
            if audio_url:
                bot.send_audio(
                    chat_id=chat_id,
                    audio=audio_url,
                    caption="🎵 សំឡេង TikTok"
                )
            else:
                bot.send_message(chat_id, "❌ គ្មានសំឡេងសម្រាប់មាតិកានេះ")
                
        elif call.data == "download_images":
            # Send TikTok images
            bot.answer_callback_query(call.id, "🔄 កំពុងផ្ញើរូបភាព...")
            
            images = data['data']['image_downloads']['images']
            
            if send_tiktok_images_as_groups(chat_id, images):
                bot.send_message(
                    chat_id=chat_id,
                    text=f"✅ បានផ្ញើរូបភាពចំនួន {len(images)} ដោយជោគជ័យ!"
                )
            else:
                bot.send_message(chat_id, "❌ កំហុសក្នុងការផ្ញើរូបភាព")
                
        elif call.data == "youtube_video":
            # Send YouTube video download link
            bot.answer_callback_query(call.id, "🔄 កំពុងដំណើរការវីដេអូ YouTube...")
            video_url = data['download_url']
            
            # Send message with download link
            bot.send_message(
                chat_id=chat_id,
                text=f"❗ ខ្ញុំមិនអាចផ្ញើវីដេអូ YouTube ដោយផ្ទាល់បានទេ\n\n"
                     f"សូមចុចលើតំណភ្ជាប់ខាងក្រោមដើម្បីទាញយកវីដេអូ:\n🔗 {video_url}"
            )
            
        elif call.data == "youtube_audio":
            # Send YouTube audio
            bot.answer_callback_query(call.id, "🔄 កំពុងទាញយកសំឡេង YouTube...")
            
            # Get audio data
            audio_data = get_youtube_audio_data(data['data']['original_url'])
            if not audio_data or audio_data.get('status') != 'success':
                bot.send_message(chat_id, "❌ បរាជ័យក្នុងការទាញយកសំឡេង YouTube")
                return
            
            audio_url = audio_data['download_url']
            
            # Download audio to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_path = temp_file.name
                if download_file(audio_url, temp_path):
                    try:
                        # Send audio
                        with open(temp_path, 'rb') as audio_file:
                            bot.send_audio(
                                chat_id=chat_id,
                                audio=audio_file,
                                caption="🎵 សំឡេង YouTube"
                            )
                    except Exception as e:
                        bot.send_message(chat_id, f"❌ កំហុសក្នុងការផ្ញើសំឡេង: {str(e)}")
                    finally:
                        # Delete temporary file
                        try:
                            os.remove(temp_path)
                        except Exception as e:
                            print(f"Error deleting temporary file: {e}")
                else:
                    bot.send_message(chat_id, "❌ បរាជ័យក្នុងការទាញយកសំឡេង")
                    try:
                        os.remove(temp_path)
                    except Exception as e:
                        print(f"Error deleting temporary file: {e}")
                
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ កំហុស: {str(e)}")
        print(f"Callback error: {e}")

if __name__ == "__main__":
    print("🚀 TikTok & YouTube Downloader Bot is starting...")
    print("Bot is ready to serve!")
    bot.infinity_polling()
