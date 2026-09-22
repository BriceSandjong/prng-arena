# PRNG Arena 🎲🛡️

**Outil d'évaluation expérimentale de la robustesse des générateurs pseudo-aléatoires (PRNG) face aux solveurs de contraintes.**

## 📌 Contexte et Démarche Scientifique
Développé dans le cadre de ma spécialisation en cybersécurité, ce projet de recherche appliquée a pour but d'auditer et de comparer la sécurité de différents schémas cryptographiques. L'outil confronte ces générateurs à des modèles mathématiques pour identifier leurs limites et vulnérabilités structurelles.

## ⚙️ Fonctionnalités Principales
- **Modélisation algorithmique** de générateurs courants tels que les LCG et le Mersenne Twister.
- **Analyse de robustesse** en soumettant les suites générées au solveur de contraintes mathématiques **Z3** pour détecter des failles logiques.
- **Évaluation expérimentale** des performances et de la complexité de calcul de chaque algorithme.

## 🛠️ Technologies Utilisées
- **C++** : Pour garantir des performances d'exécution optimales lors des calculs complexes.
- **Z3 Theorem Prover** : Moteur de résolution de contraintes.
- **Mathématiques appliquées** : Cryptanalyse et modélisation logique.

## 📄 Livrable Technique
Une **note de synthèse technique** détaillant la démarche expérimentale, les contraintes d'implémentation et l'analyse des résultats obtenus est disponible à la racine de ce dépôt.
