-- Suppression de la base de données si elle existe déjà
DROP DATABASE IF EXISTS EvaluationDB;

-- Création de la base de données
CREATE DATABASE EvaluationDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Sélection de la base de données
USE EvaluationDB;

-- --------------------------------------------------------

-- Structure de la table 'Eleves'
CREATE TABLE Eleves (
    id_eleve INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nom_eleve VARCHAR(100) NOT NULL,
    prenom_eleve VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- --------------------------------------------------------

-- Structure de la table 'Professionnels'
CREATE TABLE Professionnels (
    id_professionnel INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nom_professionnel VARCHAR(100) NOT NULL,
    prenom_professionnel VARCHAR(100) NOT NULL,
    email_professionnel VARCHAR(100)NOT NULL,
    tel_professionnel VARCHAR(100)NOT NULL,
    linkedin VARCHAR(100)NOT NULL,
    specialite VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- --------------------------------------------------------

-- Structure de la table 'Utilisateurs'
CREATE TABLE Utilisateurs (
    id_utilisateur INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_eleve INT UNSIGNED NULL,
    identifiant VARCHAR(100) UNIQUE NOT NULL,
    mot_de_passe VARCHAR(100) NOT NULL,
    role_utilisateur ENUM('admin', 'professeur', 'eleve') NOT NULL DEFAULT 'eleve',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_eleve) REFERENCES Eleves(id_eleve) ON DELETE CASCADE
);

-- --------------------------------------------------------

-- Structure de la table 'Criteres'
CREATE TABLE Criteres (
    id_critere INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nom_critere VARCHAR(255) UNIQUE NOT NULL,
    description_critere TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- --------------------------------------------------------

-- Structure de la table 'Grilles'
CREATE TABLE Grilles (
    id_grille INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nom_grille VARCHAR(100) UNIQUE NOT NULL,
    description_grille TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- --------------------------------------------------------

-- Structure de la table de liaison 'GrilleCriteres'
CREATE TABLE GrilleCriteres (
    id_grille_critere INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_grille INT UNSIGNED NOT NULL,
    id_critere INT UNSIGNED NOT NULL,
    ponderation INT UNSIGNED DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_grille) REFERENCES Grilles(id_grille) ON DELETE CASCADE,
    FOREIGN KEY (id_critere) REFERENCES Criteres(id_critere) ON DELETE CASCADE,
    UNIQUE KEY unique_grille_critere (id_grille, id_critere)
);

-- --------------------------------------------------------

-- Structure de la table 'Entretiens'
CREATE TABLE Entretiens (
    id_entretien INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_eleve INT UNSIGNED NOT NULL,
    id_professionnel INT UNSIGNED NOT NULL,
    date_entretien DATETIME NOT NULL,
    lieu_entretien VARCHAR(255),
    notes_entretien TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_eleve) REFERENCES Eleves(id_eleve) ON DELETE CASCADE,
    FOREIGN KEY (id_professionnel) REFERENCES Professionnels(id_professionnel) ON DELETE CASCADE
);

-- --------------------------------------------------------

-- Structure de la table 'Documents'
CREATE TABLE Documents (
    id_document INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_eleve INT UNSIGNED NOT NULL,
    nom_document VARCHAR(100) NOT NULL,
    nom_fichier VARCHAR(100) NOT NULL,
    date_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_eleve) REFERENCES Eleves(id_eleve) ON DELETE CASCADE
);

-- --------------------------------------------------------

-- Structure de la table 'Evaluations'
CREATE TABLE Evaluations (
    id_evaluation INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_entretien INT UNSIGNED NOT NULL,
    id_grille INT UNSIGNED NOT NULL,
    notes_evaluation TEXT,
    date_evaluation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_entretien) REFERENCES Entretiens(id_entretien) ON DELETE CASCADE,
    FOREIGN KEY (id_grille) REFERENCES Grilles(id_grille) ON DELETE CASCADE,
    UNIQUE KEY unique_evaluation_entretien_grille (id_entretien, id_grille)
);

-- --------------------------------------------------------

-- Structure de la table 'ScoresEvaluation'
CREATE TABLE ScoresEvaluation (
    id_score INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_evaluation INT UNSIGNED NOT NULL,
    id_critere INT UNSIGNED NOT NULL,
    score INT UNSIGNED,
    commentaire TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_evaluation) REFERENCES Evaluations(id_evaluation) ON DELETE CASCADE,
    FOREIGN KEY (id_critere) REFERENCES Criteres(id_critere) ON DELETE CASCADE,
    UNIQUE KEY unique_evaluation_critere (id_evaluation, id_critere)
);
