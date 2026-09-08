from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Callable, Optional


class SteamBackendError(RuntimeError):
    pass


class SteamBackend:
    """
    Optional Steam network backend based on ValvePython/steam.

    Important design rule:
    - does not initiate conversations;
    - emits incoming friend messages;
    - sends only when the GUI explicitly asks it to answer a selected contact.
    """

    def __init__(
        self,
        on_status: Callable[[str], None],
        on_message: Callable[[str, str, str], None],
        on_friends: Callable[[list[tuple[str, str]]], None],
        on_auth_required: Callable[[str], None],
    ) -> None:
        self.on_status = on_status
        self.on_message = on_message
        self.on_friends = on_friends
        self.on_auth_required = on_auth_required
        self.client = None
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._username = ""
        self._password = ""

    @staticmethod
    def dependency_available() -> bool:
        try:
            import steam  # noqa: F401
            return True
        except Exception:
            return False

    def connect(self, username: str, password: str, code: str = "") -> None:
        if self._thread and self._thread.is_alive():
            raise SteamBackendError("Steam backend is already running.")
        if not username or not password:
            raise SteamBackendError("Steam account name and password are required.")
        self._username, self._password = username, password
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._run,
            args=(code.strip(),),
            daemon=True,
            name="SteamBackend",
        )
        self._thread.start()

    def _run(self, code: str) -> None:
        try:
            from steam.client import SteamClient
            from steam.enums import EResult
            from steam.enums.emsg import EMsg
        except Exception as exc:
            self.on_status(f"Steam library missing: {exc}")
            return

        try:
            client = SteamClient()
            self.client = client
            cred_dir = Path.home() / ".game_troll_buster" / "steam"
            cred_dir.mkdir(parents=True, exist_ok=True)
            client.set_credential_location(str(cred_dir))

            # Legacy direct friend-message event is still understood by Steam's CM protocol.
            @client.on(EMsg.ClientFriendMsgIncoming)
            def _friend_msg(msg):
                try:
                    body = msg.body
                    sid = str(int(body.steamid_from))
                    entry_type = int(body.chat_entry_type)
                    if entry_type not in (1, 4):  # ChatMsg / Emote
                        return
                    raw = body.message
                    if isinstance(raw, bytes):
                        text = raw.decode("utf-8", errors="replace").rstrip("\x00")
                    else:
                        text = str(raw)
                    if not text.strip():
                        return
                    name = sid
                    try:
                        user = client.get_user(int(sid))
                        if getattr(user, "name", None):
                            name = user.name
                    except Exception:
                        pass
                    self.on_message(sid, name, text)
                except Exception as exc:
                    self.on_status(f"Incoming message parse error: {exc}")

            self.on_status("Connecting to Steam …")
            kwargs = {}
            if code:
                # Steam Guard mobile codes are normally 5 chars. Email codes are
                # accepted as auth_code; try 2FA first, then GUI can retry.
                kwargs["two_factor_code"] = code

            result = client.login(self._username, self._password, **kwargs)

            if result == EResult.AccountLogonDenied:
                self.on_auth_required("email")
                self.on_status("Steam Guard email code required.")
                return
            if result in (EResult.AccountLoginDeniedNeedTwoFactor, EResult.TwoFactorCodeMismatch):
                self.on_auth_required("2fa")
                self.on_status("Steam Guard 2FA code required.")
                return
            if result == EResult.InvalidLoginAuthCode:
                self.on_auth_required("email")
                self.on_status("Steam Guard email code was rejected.")
                return
            if result != EResult.OK:
                self.on_status(f"Steam login failed: {result!s}")
                return

            self.on_status("Steam connected.")
            # Give persona/friend state a moment to populate.
            for _ in range(20):
                if self._stop.is_set():
                    break
                try:
                    if getattr(client.friends, "ready", False):
                        break
                except Exception:
                    pass
                client.sleep(0.25)

            friends: list[tuple[str, str]] = []
            try:
                for friend in client.friends:
                    sid = str(int(friend.steam_id))
                    name = getattr(friend, "name", None) or sid
                    friends.append((sid, name))
            except Exception as exc:
                self.on_status(f"Connected; friend list not fully available: {exc}")
            self.on_friends(friends)

            while not self._stop.is_set() and getattr(client, "connected", False):
                client.sleep(0.25)

        except Exception as exc:
            self.on_status(f"Steam backend error: {type(exc).__name__}: {exc}")
        finally:
            try:
                if self.client:
                    self.client.logout()
            except Exception:
                pass
            self.client = None

    def connect_with_email_code(self, username: str, password: str, code: str) -> None:
        # Separate route because ValvePython login distinguishes auth_code vs 2FA.
        if self._thread and self._thread.is_alive():
            self.disconnect()
            time.sleep(0.2)
        self._username, self._password = username, password
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._run_email_code,
            args=(code.strip(),),
            daemon=True,
            name="SteamBackend",
        )
        self._thread.start()

    def _run_email_code(self, code: str) -> None:
        try:
            from steam.client import SteamClient
            from steam.enums import EResult
            from steam.enums.emsg import EMsg
        except Exception as exc:
            self.on_status(f"Steam library missing: {exc}")
            return

        try:
            client = SteamClient()
            self.client = client
            cred_dir = Path.home() / ".game_troll_buster" / "steam"
            cred_dir.mkdir(parents=True, exist_ok=True)
            client.set_credential_location(str(cred_dir))

            @client.on(EMsg.ClientFriendMsgIncoming)
            def _friend_msg(msg):
                try:
                    body = msg.body
                    if int(body.chat_entry_type) not in (1, 4):
                        return
                    sid = str(int(body.steamid_from))
                    raw = body.message
                    text = raw.decode("utf-8", errors="replace").rstrip("\x00") if isinstance(raw, bytes) else str(raw)
                    name = sid
                    try:
                        user = client.get_user(int(sid))
                        name = getattr(user, "name", None) or sid
                    except Exception:
                        pass
                    if text.strip():
                        self.on_message(sid, name, text)
                except Exception as exc:
                    self.on_status(f"Incoming message parse error: {exc}")

            self.on_status("Connecting to Steam with email code …")
            result = client.login(self._username, self._password, auth_code=code)
            if result != EResult.OK:
                self.on_status(f"Steam login failed: {result!s}")
                return
            self.on_status("Steam connected.")
            for _ in range(20):
                if self._stop.is_set():
                    break
                try:
                    if getattr(client.friends, "ready", False):
                        break
                except Exception:
                    pass
                client.sleep(0.25)

            friends = []
            try:
                for friend in client.friends:
                    sid = str(int(friend.steam_id))
                    friends.append((sid, getattr(friend, "name", None) or sid))
            except Exception:
                pass
            self.on_friends(friends)

            while not self._stop.is_set() and getattr(client, "connected", False):
                client.sleep(0.25)
        except Exception as exc:
            self.on_status(f"Steam backend error: {type(exc).__name__}: {exc}")
        finally:
            try:
                if self.client:
                    self.client.logout()
            except Exception:
                pass
            self.client = None

    def send_message(self, steam_id: str, text: str) -> None:
        if not self.client or not getattr(self.client, "logged_on", False):
            raise SteamBackendError("Not connected to Steam.")
        try:
            from steam.core.msg import MsgProto
            from steam.enums.emsg import EMsg
            msg = MsgProto(EMsg.ClientFriendMsg)
            msg.body.steamid = int(steam_id)
            msg.body.chat_entry_type = 1
            msg.body.message = text.encode("utf-8")
            self.client.send(msg)
        except Exception as exc:
            raise SteamBackendError(str(exc)) from exc

    def disconnect(self) -> None:
        self._stop.set()
        try:
            if self.client:
                self.client.disconnect()
        except Exception:
            pass
