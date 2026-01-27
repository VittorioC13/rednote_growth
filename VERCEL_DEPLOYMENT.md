# 🚀 Vercel Deployment Guide

Deploy your 小红书 Content Generator to Vercel in 5 minutes!

## Step 1: Push to GitHub

Already done! Your code is at: https://github.com/VittorioC13/rednote_growth

## Step 2: Connect to Vercel

1. Go to **https://vercel.com**
2. Sign in with GitHub
3. Click **"Add New Project"**
4. Select **`rednote_growth`** repository
5. Click **"Import"**

## Step 3: Configure Environment Variable

Before deploying, add your API key:

1. In Vercel project settings, go to **"Environment Variables"**
2. Add a new variable:
   - **Name:** `DEEPSEEK_API_KEY`
   - **Value:** `your_actual_api_key`
   - **Environment:** All (Production, Preview, Development)
3. Click **"Save"**

## Step 4: Deploy

Click **"Deploy"** button - Vercel will automatically:
- Install dependencies from `requirements.txt`
- Build the serverless function
- Deploy your app

## Step 5: Access Your App

After deployment (1-2 minutes), you'll get a URL like:
```
https://rednote-growth.vercel.app
```

Visit it and click "Generate 10 Viral Posts"!

## 🎯 How It Works

**Serverless Architecture:**
- No file storage (posts stored in memory)
- Each request is a fresh instance
- API calls to DeepSeek on-demand
- Scales automatically

**Files Used:**
- `api/index.py` - Vercel entry point
- `vercel.json` - Vercel configuration
- `web_interface_vercel.py` - Serverless Flask app
- `rednote_content_generator_serverless.py` - No file I/O version

## 📝 Important Notes

1. **No File Downloads:** Since Vercel is serverless, you can't download PDFs. Posts are displayed in browser only.

2. **Memory Reset:** Generated posts are lost when the serverless function restarts (that's ok, you can copy them)

3. **Cold Starts:** First request might be slow (5-10 seconds) as Vercel spins up the function

4. **API Key Security:** Never commit your `.env` file. Always use Vercel environment variables.

## 🔧 Troubleshooting

### Deployment Failed?
- Check build logs in Vercel dashboard
- Verify `requirements.txt` has all dependencies
- Make sure Python version is compatible

### API Not Working?
- Verify `DEEPSEEK_API_KEY` is set in Vercel environment variables
- Check API key has sufficient credits
- Look at Function logs in Vercel

### 502 Error?
- Function timeout (max 10s on free plan)
- Try generating again (DeepSeek API might be slow)
- Upgrade Vercel plan for longer timeouts

## 💡 Tips

1. **Custom Domain:** Add your own domain in Vercel project settings
2. **Analytics:** Enable Vercel Analytics to track usage
3. **Monitoring:** Check Function logs regularly
4. **Updates:** Push to GitHub = auto-deploy to Vercel

## 🆚 Local vs Vercel

| Feature | Local | Vercel |
|---------|-------|--------|
| File storage | ✅ Yes | ❌ No |
| PDF downloads | ✅ Yes | ❌ No |
| Always on | ❌ Manual | ✅ Automatic |
| Accessible | 🏠 Localhost only | 🌍 Anywhere |
| Scaling | ❌ No | ✅ Auto |

## 🎉 That's It!

Your 小红书 content generator is now live and accessible from anywhere!

Need help? Check the Vercel docs or create an issue on GitHub.
