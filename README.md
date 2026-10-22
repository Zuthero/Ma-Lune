# Ma Lune 🌙

**Ma Lune** is a free WhatsApp companion that gives girls aged 10 to 19 and their parents in the Democratic Republic of the Congo trusted information about periods, puberty and their bodies. It is built by [Zuthero Business Solutions](https://www.zuthero.com).

*Français plus bas.*

## What it does
- 19 short lessons: the cycle, first period, hygiene, pain, emotions, anaemia, online safety, HPV vaccine and more
- A gentler, parent-guided path for girls under 13, and a 7-lesson space for parents
- A period calculator that estimates the next period
- A quiz to measure what girls learn
- Danger detection: worrying words open a private ticket so a trained person replies
- An AI assistant (in development) that answers girls' own questions from medically reviewed content only, and hands risky questions to a person

## How it is built
- **WhatsApp Business Cloud API** for the channel
- **RapidPro / TextIt** for the conversation flows
- **Call AI** (large language model) for open questions, with strict safety instructions in [`ai/instructions-fr.md`](ai/instructions-fr.md)
- Anonymised results (topics, quiz scores, feedback) to measure impact

## Repository contents
| Folder | What is inside |
| --- | --- |
| `flows/` | TextIt / RapidPro flow exports, ready to import |
| `content/` | All lesson messages in French |
| `ai/` | Instructions and safety rules for the AI assistant |
| `docs/` | Safety and privacy design |
| `tools/` | Python script that generates the flows from the content |

## Reuse it
1. Create a free workspace on TextIt or RapidPro and connect a WhatsApp number.
2. Import the JSON files from `flows/`.
3. Adapt the content to your country and have it reviewed by a health professional before use.

## Status
Pilot in development in Kinshasa. All health content is being reviewed by our medical advisor, a gynaecologist.

## Licence
- Code and flows: [MIT](LICENSE)
- Health content: [CC BY-SA 4.0](LICENSE-CONTENT.md)

## Contact
info@zuthero.com · https://www.zuthero.com

---

# Ma Lune 🌙 (français)

**Ma Lune** est une amie gratuite sur WhatsApp qui informe les filles de 10 à 19 ans et leurs parents en République démocratique du Congo sur les règles, la puberté et le corps. Elle est développée par [Zuthero Business Solutions](https://www.zuthero.com).

## Ce que fait Ma Lune
- 19 leçons courtes : le cycle, les premières règles, l'hygiène, les douleurs, les émotions, l'anémie, la sécurité en ligne, le vaccin HPV…
- Un parcours doux pour les moins de 13 ans, lu avec un parent, et un espace parents de 7 leçons
- Un calculateur qui estime la date des prochaines règles
- Un quiz pour mesurer ce que les filles apprennent
- Une détection de danger : les mots inquiétants ouvrent un ticket privé, et une personne formée répond
- Un assistant IA (en développement) qui répond aux questions à partir du contenu validé uniquement, et confie les questions à risque à une personne

## Réutiliser Ma Lune
1. Créez un espace gratuit sur TextIt ou RapidPro et connectez un numéro WhatsApp.
2. Importez les fichiers JSON du dossier `flows/`.
3. Adaptez le contenu à votre pays et faites-le valider par un professionnel de santé avant usage.

## Licence
Code et flows : MIT. Contenu santé : CC BY-SA 4.0.
