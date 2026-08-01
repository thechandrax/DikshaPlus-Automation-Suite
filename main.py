"""
Main CLI entry point for DIKSHA Browser Automation Engine.
Includes:
- Security PIN Verification (541563)
- Multi-User Credentials Registry & Selection Menu
- High-Security Encrypted Password Support
"""

import sys
import argparse
import asyncio
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from utils.security import verify_security_pin, decrypt_password
from automations.diksha_plus_engine import run_diksha_automation


from utils.logger import get_logger

logger = get_logger("Main")

def display_interactive_user_menu():
    """
    Displays interactive registered user selection menu matching design mockup with rich colors.
    """
    print("\033[38;5;51m\033[1m===================================================================\n ⚡ DIKSHA+ AUTOMATION SUITE\n===================================================================\033[0m")

    print("\033[38;5;220m\033[1m[Login] Registered accounts:\033[0m")
    user_keys = list(config.USER_CREDENTIALS.keys())
    for i, u_key in enumerate(user_keys, 1):
        display_name = config.USER_NAMES.get(u_key, "")
        if display_name:
            print(f"  \033[38;5;141m[{i}]\033[0m \033[38;5;220m{display_name:<24}\033[0m \033[38;5;245m:\033[0m \033[38;5;231m{u_key}\033[0m")
        else:
            print(f"  \033[38;5;141m[{i}]\033[0m \033[38;5;231m{u_key}\033[0m")
    print("\033[38;5;240m-------------------------------------------------------------------\033[0m")


    if not sys.stdin.isatty():
        logger.info("  [!] Non-interactive mode detected. Processing user [1] by default.")
        return [(user_keys[0], config.USER_CREDENTIALS[user_keys[0]])]

    try:
        choice = input(f"\033[38;5;51m👉 Select user number (1-{len(user_keys)}) or type custom email/mobile: \033[0m").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(user_keys):
            selected_user = user_keys[int(choice) - 1]
            return [(selected_user, config.USER_CREDENTIALS[selected_user])]
        elif choice in config.USER_CREDENTIALS:
            return [(choice, config.USER_CREDENTIALS[choice])]
        elif "@" in choice or choice.isdigit():
            pwd = input(f"Enter password for custom user '{choice}': ").strip()
            return [(choice, pwd)]
        else:
            print("  [!] Invalid selection. Defaulting to account [1].")
            return [(user_keys[0], config.USER_CREDENTIALS[user_keys[0]])]
    except Exception:
        return [(user_keys[0], config.USER_CREDENTIALS[user_keys[0]])]




def main():
    parser = argparse.ArgumentParser(description="DIKSHA LMS Multi-User Automation Engine")


    parser.add_argument("--url", dest="target_course_url", default=None, help="Direct Course URL")
    parser.add_argument("--username", dest="username", default=None, help="Specific Username / Mobile / Email")
    parser.add_argument("--password", dest="password", default=None, help="Specific Password")
    parser.add_argument("--user", dest="user_key", default=None, help="Select registered user key")
    parser.add_argument("--all-users", dest="all_users", action="store_true", help="Run batch processing for ALL registered users")
    parser.add_argument("--submit", dest="auto_submit", action="store_true", help="Enable automatic final quiz submission")
    parser.add_argument("--close", dest="auto_close", action="store_true", help="Automatically close browser after run completes")
    parser.add_argument("--headless", dest="headless", action="store_true", help="Run browser in background (headless)")
    parser.add_argument("--skip-pin", dest="skip_pin", action="store_true", help="Skip PIN verification (for automated tests)")
    args = parser.parse_args()

    if args.headless:
        config.HEADLESS = True

    if args.auto_close or args.headless:
        config.KEEP_BROWSER_OPEN = False

    if not config.AUTO_START:
        logger.info("\n===================================================================\n ⏸️ [RAILWAY STANDBY MODE] AUTO_START is set to False.\n Container is standing by on Railway Cloud. Automation paused.\n Set AUTO_START=True in Railway Variables to start execution.\n===================================================================\n")
        import time
        while True:
            time.sleep(3600)

    # Environment variable overrides for cloud deployments (e.g. Railway)
    import os

    env_user = os.getenv("SELECTED_USER", "").strip()
    if env_user:
        if env_user.lower() == "all":
            args.all_users = True
        elif env_user.isdigit():
            u_idx = int(env_user)
            u_keys = list(config.USER_CREDENTIALS.keys())
            if 1 <= u_idx <= len(u_keys):
                args.user_key = u_keys[u_idx - 1]

    # 1. Security PIN Verification (541563)
    if not args.skip_pin and sys.stdin.isatty():
        if not verify_security_pin():
            sys.exit(1)

    # 2. Determine target user list
    users_to_process = []

    if args.all_users:
        logger.info(f"Batch mode activated! Processing all {len(config.USER_CREDENTIALS)} registered users.")
        for u, p in config.USER_CREDENTIALS.items():
            users_to_process.append((u, p))
    elif args.user_key:
        if args.user_key in config.USER_CREDENTIALS:
            users_to_process.append((args.user_key, config.USER_CREDENTIALS[args.user_key]))
        else:
            logger.error(f"User key '{args.user_key}' not found in USER_CREDENTIALS registry.")
            sys.exit(1)

    elif args.username and args.password:
        users_to_process.append((args.username, args.password))
    else:
        # Display Interactive Registered User Selection Menu
        users_to_process = display_interactive_user_menu()

    # 3. Execute Automation Pipeline for selected user(s)
    try:
        for idx, (u, p) in enumerate(users_to_process, 1):
            disp = config.USER_NAMES.get(u, u)
            logger.info("\n" + "=" * 43)
            logger.info(f"   PROCESSING USER {idx}/{len(users_to_process)}: {disp} ({u})")
            logger.info("=" * 43)

            asyncio.run(run_diksha_automation(
                target_course_url=args.target_course_url,
                username=u,
                password=p
            ))

    except KeyboardInterrupt:
        logger.info("Automation process interrupted by user.")
    except Exception as e:
        logger.error(f"Automation execution failure: {e}", exc_info=True)

if __name__ == "__main__":
    main()
