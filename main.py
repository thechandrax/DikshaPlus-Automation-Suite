"""
Main CLI entry point for DIKSHA Browser Automation Engine.
Includes:
- Security PIN Verification (6-digit PIN required at runtime)
- Multi-User Credentials Registry & Selection Menu
- Obfuscated Password Support
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
        import os
        env_user = os.getenv("SELECTED_USER", "").strip()
        if env_user:
            clean_env_u = env_user.lower()
            if clean_env_u == "all":
                logger.info(f"  🎯 [RAILWAY USER SELECTION] SELECTED_USER='all' detected. Processing ALL {len(config.USER_CREDENTIALS)} registered accounts in batch.")
                return [(u, p) for u, p in config.USER_CREDENTIALS.items()]
            elif env_user.isdigit():
                u_idx = int(env_user)
                if 1 <= u_idx <= len(user_keys):
                    selected_user = user_keys[u_idx - 1]
                    disp_name = config.USER_NAMES.get(selected_user, selected_user)
                    logger.info(f"  🎯 [RAILWAY USER SELECTION] Selected Account #{u_idx}: '{disp_name}' ({selected_user}).")
                    return [(selected_user, config.USER_CREDENTIALS[selected_user])]
            else:
                # Match by exact key, email, or display name keyword!
                matched_user = None
                for u_k in user_keys:
                    disp_n = config.USER_NAMES.get(u_k, "")
                    if clean_env_u == u_k.lower() or clean_env_u in u_k.lower() or (disp_n and clean_env_u in disp_n.lower()):
                        matched_user = u_k
                        break

                if matched_user:
                    disp_name = config.USER_NAMES.get(matched_user, matched_user)
                    logger.info(f"  🎯 [RAILWAY USER SELECTION] Matched Account by Keyword '{env_user}': '{disp_name}' ({matched_user}).")
                    return [(matched_user, config.USER_CREDENTIALS[matched_user])]

        default_user = user_keys[0]
        disp_name = config.USER_NAMES.get(default_user, default_user)
        logger.info(f"  🎯 [RAILWAY DEFAULT AUTO-START] No SELECTED_USER environment variable set. Auto-selecting Account #1: '{disp_name}' ({default_user}).")
        return [(default_user, config.USER_CREDENTIALS[default_user])]






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


def select_browser_mode():
    """
    Displays interactive CLI menu to select browser display mode:
    [1] Headless Mode (Silent Background Execution)
    [2] Visible GUI Mode (Show Browser Window on Screen)
    """
    if not sys.stdin.isatty():
        return

    print("\n\033[38;5;51m" + "=" * 67 + "\033[0m")
    print(" \033[1;38;5;220m🎭 CHOOSE BROWSER DISPLAY MODE\033[0m")
    print("\033[38;5;51m" + "=" * 67 + "\033[0m")


    print("  \033[38;5;220m[1]\033[0m \033[1;38;5;82mHeadless Mode\033[0m \033[38;5;245m(Silent Background Execution)\033[0m")
    print("  \033[38;5;220m[2]\033[0m \033[1;38;5;207mVisible GUI Mode\033[0m \033[38;5;245m(Show Browser Window on Screen)\033[0m")
    print("\033[38;5;51m" + "-" * 67 + "\033[0m")

    while True:
        try:
            mode_choice = input("\033[38;5;51m👉 Select browser mode (1 or 2): \033[0m").strip()
            if mode_choice == "1":
                config.HEADLESS = True
                logger.info("  ✔ Mode selected: \033[1;38;5;82m[1] Headless Mode (Silent Background Execution)\033[0m")
                break
            elif mode_choice == "2":
                config.HEADLESS = False
                logger.info("  ✔ Mode selected: \033[1;38;5;207m[2] Visible GUI Mode (Show Browser Window on Screen)\033[0m")
                break
            else:
                print("  \033[31m[!] Invalid selection. Please enter 1 or 2.\033[0m")
        except (KeyboardInterrupt, EOFError):
            sys.exit(0)
        except Exception:
            config.HEADLESS = True
            break
    print("\033[38;5;51m" + "=" * 67 + "\033[0m\n")




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

    # 0. Print Opening Launching Banner
    if sys.stdin.isatty():
        print("\n\033[38;5;51m" + "=" * 67 + "\033[0m")
        print("              \033[1;38;5;220m🚀 LAUNCHING DIKSHA+ AUTOMATION SUITE\033[0m")
        print("\033[38;5;51m" + "=" * 67 + "\033[0m\n")

    # 1. Security PIN Verification
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

    # 2.5 Prompt for Browser Display Mode Selection (Headless vs Visible GUI)
    if not args.headless and sys.stdin.isatty():
        select_browser_mode()


    # 3. Execute Automation Pipeline for selected user(s) with Auto-Reconnect Recovery
    for idx, (u, p) in enumerate(users_to_process, 1):
        disp = config.USER_NAMES.get(u, u)
        logger.info("\n" + "=" * 43)
        logger.info(f"   PROCESSING USER {idx}/{len(users_to_process)}: {disp} ({u})")
        logger.info("=" * 43)

        max_session_attempts = 3
        for s_attempt in range(1, max_session_attempts + 1):
            try:
                asyncio.run(run_diksha_automation(
                    target_course_url=args.target_course_url,
                    username=u,
                    password=p
                ))
                break  # Completed successfully — move to next user

            except KeyboardInterrupt:
                logger.info("Automation process interrupted by user.")
                sys.exit(0)

            except Exception as e:
                err_msg = str(e).lower()
                is_browser_disconnect = any(kw in err_msg for kw in [
                    "connection closed",
                    "target closed",
                    "browser has been closed",
                    "browser closed",
                    "playwright",
                    "websocket",
                    "pipe closed",
                ])

                if is_browser_disconnect:
                    logger.warning(f"\n⚠️  [BROWSER DISCONNECT] Session connection dropped (Attempt {s_attempt}/{max_session_attempts}).")
                    if s_attempt < max_session_attempts:
                        logger.warning("🚀 Cleaning browser session locks & auto-restarting fresh Chrome session in 3 seconds...")
                        import os, glob, time
                        try:
                            user_dir = getattr(config, "USER_DATA_DIR", "")
                            if user_dir and os.path.exists(user_dir):
                                for lf in glob.glob(os.path.join(user_dir, "*Singleton*")):
                                    try:
                                        os.remove(lf)
                                    except Exception:
                                        pass
                        except Exception:
                            pass
                        time.sleep(3)
                        logger.warning(f"🔄 [AUTO-RESTART] Starting fresh Chrome session (Attempt {s_attempt + 1}/{max_session_attempts})...\n")
                    else:
                        logger.error(f"❌ [SESSION FAILED] Browser disconnected {max_session_attempts} times for user '{disp}'. Skipping to next user.")
                else:
                    logger.error(f"Automation execution failure: {e}", exc_info=True)
                    break  # Non-browser error — don't retry


if __name__ == "__main__":
    main()
