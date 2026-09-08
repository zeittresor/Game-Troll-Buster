from eliza_engine import ElizaEngine

def main():
    e = ElizaEngine(seed=1)
    samples = [
        "do you want to support me",
        "you are stupid",
        "because you waste my time",
        "I need money",
        "are you even listening?",
    ]
    for text in samples:
        reply = e.respond(text)
        assert reply and reply.endswith("?"), (text, reply)
        print(f"[Troll]: {text}\n\n[ELIZA]: {reply}\n")
    print("ELIZA smoke test: OK")

if __name__ == "__main__":
    main()
