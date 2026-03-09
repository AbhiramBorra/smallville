import sys, os, json, argparse

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "reverie", "backend_server")
)

from persona.persona import Persona
from persona.cognitive_modules.converse import interview_conspiracy_belief


def main():
    parser = argparse.ArgumentParser(
        description="Interview agents about conspiracy beliefs"
    )
    parser.add_argument("--sim", required=True, help="Simulation name")
    parser.add_argument("--persona", help="Persona name (use --all for all personas)")
    parser.add_argument("--theory", help="Conspiracy theory to rate")
    parser.add_argument("--view", action="store_true", help="View existing ratings")
    args = parser.parse_args()

    sim_folder = f"../environment/frontend_server/storage/{args.sim}"

    if args.view:
        if args.persona:
            persona_folder = f"{sim_folder}/personas/{args.persona}"
            persona = Persona(args.persona, persona_folder)
            beliefs = persona.load_conspiracy_beliefs()
            print(json.dumps(beliefs, indent=2))
        else:
            theories = Persona.get_all_theories_in_simulation(sim_folder)
            print(json.dumps(theories, indent=2))
        return

    if not args.theory:
        print("Error: --theory required")
        return

    if args.persona == "--all":
        personas_folder = f"{sim_folder}/personas"
        for persona_name in os.listdir(personas_folder):
            if persona_name.startswith("."):
                continue
            persona_folder = f"{personas_folder}/{persona_name}"
            persona = Persona(persona_name, persona_folder)
            result = interview_conspiracy_belief(persona, args.theory, save=True)
            print(f"{persona_name}: {result['rating']}/10 - {result['explanation']}")
    elif args.persona:
        persona_folder = f"{sim_folder}/personas/{args.persona}"
        persona = Persona(args.persona, persona_folder)
        result = interview_conspiracy_belief(persona, args.theory, save=True)
        print(f"{args.persona}: {result['rating']}/10 - {result['explanation']}")


if __name__ == "__main__":
    main()
