
# main.py
# Klavia.io Bot - Full Automation Script
# Author: ChatGPT + Ethan
# Monolithic version, includes: FastAPI server, Playwright automation, Key verification, Task queue

import asyncio
import json
import os
import random
import time
from fastapi import FastAPI, Request, Form, HTTPException
from pydantic import BaseModel
from typing import List
from starlette.responses import HTMLResponse
from playwright.async_api import async_playwright
from datetime import datetime

# Load keys with slot limits
KEY_FILE = "keys.txt"
TASKS_FILE = "task_data.json"
LOG_DIR = "logs"

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def load_keys():
    keys = {}
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            for line in f:
                if ":" in line:
                    k, slots = line.strip().split(":")
                    keys[k.strip()] = int(slots)
    return keys

def save_task(task):
    try:
        with open(TASKS_FILE, "r") as f:
            data = json.load(f)
    except:
        data = []

    data.append(task)
    with open(TASKS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def purge_finished_tasks():
    try:
        with open(TASKS_FILE, "r") as f:
            tasks = json.load(f)
        tasks = [t for t in tasks if not t.get("finished", False)]
        with open(TASKS_FILE, "w") as f:
            json.dump(tasks, f, indent=2)
    except:
        pass

async def run_bot(task):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Go to login
            await page.goto("https://klavia.io/racers/sign_in")
            await page.fill("#racer_email", task["username"])
            await page.fill("#racer_password", task["password"])
            await page.click('input[type="submit"][value="Sign In"]')
            await page.wait_for_timeout(3000)

            # Go to Quick Race
            await page.goto("https://klavia.io/race")
            await page.wait_for_selector("#typing-text")

            for race_num in range(task["races"]):
                text = await page.eval_on_selector("#typing-text", "el => el.innerText")
                await page.click("#typing-text")  # Focus typing
                delay = 60 / (task["wpm"] * 5)  # Estimate: 1 word = 5 chars
                for char in text:
                    if random.random() < 0.015:
                        await page.keyboard.press("Backspace")
                    await page.keyboard.type(char, delay=delay * random.uniform(0.9, 1.3))
                await page.keyboard.press("Enter")
                await page.wait_for_timeout(3500)

            log_path = os.path.join(LOG_DIR, f"{task['username']}_{int(time.time())}.txt")
            with open(log_path, "w") as f:
                f.write(f"Bot completed {task['races']} races for {task['username']} at {datetime.now()}\n")
            task["finished"] = True
        except Exception as e:
            task["error"] = str(e)
        finally:
            await context.close()
            await browser.close()

        purge_finished_tasks()

# ========== FASTAPI BACKEND ==========
app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
      <body>
        <h1>Klavia Bot Running</h1>
        <p>Submit form at <code>/start-task</code></p>
      </body>
    </html>
    """

@app.post("/start-task")
async def start_task(
    username: str = Form(...),
    password: str = Form(...),
    wpm: int = Form(...),
    accuracy: int = Form(...),
    races: int = Form(...),
    key: str = Form(...)
):
    # Check if key exists and user has slot available
    keys = load_keys()
    if key not in keys:
        raise HTTPException(status_code=401, detail="Invalid key")

    # Check current usage
    with open(TASKS_FILE, "r") as f:
        existing = json.load(f)
    key_usage = sum(1 for t in existing if t["key"] == key and not t.get("finished", False))
    if key_usage >= keys[key]:
        raise HTTPException(status_code=403, detail="Key slot limit reached")

    task = {
        "username": username,
        "password": password,
        "wpm": wpm,
        "accuracy": accuracy,
        "races": races,
        "key": key,
        "timestamp": datetime.now().isoformat()
    }
    save_task(task)
    asyncio.create_task(run_bot(task))
    return {"status": "started", "task": task}

@app.get("/active-tasks")
async def active_tasks():
    with open(TASKS_FILE, "r") as f:
        return json.load(f)
