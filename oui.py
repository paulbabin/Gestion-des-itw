# -*- coding: utf-8 -*-
"""
Created on Fri May  9 09:53:16 2025
@author: estho
"""
import sys
import os
import datetime
import time
import cProfile
import pstats
from io import StringIO
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import Calendar

# Configuration MySQL robuste
def init_mysql():
    try:
        import mysql.connector as mysql_connector
        from mysql.connector import Error
        
        # Configuration des locales
        try:
            os.environ['LANG'] = 'fra'
            mysql_connector.locales.set_locale('fra')
        except:
            try:
                from mysql.connector import locales
                locales._DEFAULT_LOCALE = 'fra'
            except:
                pass
        
        return mysql_connector, Error
    
    except ImportError as e:
        messagebox.showerror("Erreur Critique", f"Échec du chargement de mysql-connector: {e}")
        sys.exit(1)

# Initialisation globale
mysql, Error = init_mysql()

class DBManagerPro:
    def __init__(self, root):
        self.root = root
        self.db_connection = None
        self.current_role = None
        self.current_user_id = None
        self.current_eleve_id = None
        self.setup_ui()
        self.connect_db()

    def connect_db(self):
        """Établit la connexion à la base de données"""
        try:
            self.db_connection = mysql.connect(
                host="localhost",
                user="root",
                password="",
                database="EvaluationDB",
                auth_plugin='mysql_native_password'
            )
        except Error as e:
            messagebox.showerror("Erreur", f"Connexion échouée: {e}")
            self.db_connection = None
        except ImportError as locale_error:
            if "No localization support" in str(locale_error):
                messagebox.showwarning("Avertissement", 
                                     "Problème de localisation mineur - L'application continue...")
                self.db_connection = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="EvaluationDB"
                )
            else:
                raise

    def close_db(self):
        """Ferme la connexion à la base de données si elle est active."""
        if self.db_connection and self.db_connection.is_connected():
            self.db_connection.close()
            self.db_connection = None

    def setup_ui(self):
        self.root.title("DB Manager Pro")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)
        self.root.configure(bg="#4A5568")
        self.setup_styles()
        self.create_login_ui()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.colors = {
            "bg": "#4A5568",
            "card": "#2D3748",
            "text": "#F7FAFC",
            "accent": "#00CED1",
            "highlight": "#48D1CC",
            "entry": "#2D3748",
            "header": "#36454F",
            "error": "#FF6B6B",
            "warning": "#FF6B6B",
            "secondary_text": "#A0AEC0"
        }
        self.style.configure(".", background=self.colors["bg"], foreground=self.colors["text"],
                             font=("Segoe UI", 11), borderwidth=0, padding=8)
        self.style.configure("Card.TFrame", background=self.colors["card"], padding=15)
        self.style.configure("Accent.TButton", background=self.colors["accent"],
                             foreground="white", font=("Segoe UI", 12, "bold"), padding=(15, 10))
        self.style.configure("Warning.TButton", background=self.colors["warning"],
                             foreground="white", font=("Segoe UI", 12, "bold"), padding=(15, 10))
        self.style.map("Accent.TButton",
                       background=[("active", self.colors["highlight"]), ("pressed", "#00B2A5")])
        self.style.map("Warning.TButton",
                       background=[("active", "#FF8C8C"), ("pressed", "#CC5A5A")])
        self.style.configure("TButton", background=self.colors["card"], foreground=self.colors["text"],
                             font=("Segoe UI", 10, "bold"), padding=(10, 8))
        self.style.map("TButton", background=[("active", "#3A4A6A"), ("pressed", "#1A202C")])
        self.style.configure("Treeview", background=self.colors["card"], rowheight=30,
                             fieldbackground=self.colors["card"], foreground=self.colors["text"])
        self.style.configure("Treeview.Heading", background=self.colors["header"], foreground=self.colors["text"], padding=10)
        self.style.map("Treeview", background=[("selected", self.colors["accent"])],
                       foreground=[("selected", "white")])
        self.style.configure("TEntry", fieldbackground=self.colors["entry"], foreground=self.colors["text"], padding=5)
        self.style.configure("TCombobox", fieldbackground=self.colors["entry"], foreground=self.colors["text"],
                             background=self.colors["card"], padding=5)
        self.style.configure("TLabel", foreground=self.colors["text"])

    def create_login_ui(self):
        self.login_frame = ttk.Frame(self.root, style="Card.TFrame", padding=30)
        self.login_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        ttk.Label(self.login_frame,
                  text="🚪 Connexion",
                  font=("Segoe UI", 28, "bold"), foreground=self.colors["accent"]).pack(pady=(0, 5))

        ttk.Label(self.login_frame,
                  text="Accédez à votre espace EvaluationDB",
                  font=("Segoe UI", 12), foreground=self.colors["secondary_text"]).pack(pady=(0, 20))

        form_frame = ttk.Frame(self.login_frame, style="Card.TFrame", padding=20)
        form_frame.pack(fill=tk.X)

        ttk.Label(form_frame, text="Identifiant :", font=("Segoe UI", 11)).pack(anchor="w", pady=(5, 2))
        self.username_entry = ttk.Entry(form_frame)
        self.username_entry.pack(fill=tk.X, pady=5, ipady=8)

        ttk.Label(form_frame, text="Mot de passe :", font=("Segoe UI", 11)).pack(anchor="w", pady=(15, 2))
        self.pass_entry = ttk.Entry(form_frame, show="•")
        self.pass_entry.pack(fill=tk.X, pady=5, ipady=8)

        login_button = ttk.Button(
            form_frame,
            text="SE CONNECTER",
            style="Accent.TButton",
            command=self.handle_login
        )
        login_button.pack(pady=20, fill=tk.X, ipady=10)

        register_label = ttk.Label(self.login_frame, text="Pas de compte ?", font=("Segoe UI", 10), foreground=self.colors["secondary_text"])
        register_label.pack(pady=(15, 2))
        register_button = ttk.Button(
            self.login_frame,
            text="Créer un compte étudiant",
            style="TButton",
            command=self.show_register_student
        )
        register_button.pack(fill=tk.X, pady=(0, 10))

        self.pass_entry.bind("<Return>", lambda e: self.handle_login())

    def execute_query(self, query, params=None):
        """Exécute une requête SQL en utilisant la connexion persistante."""
        if self.db_connection is None or not self.db_connection.is_connected():
            self.connect_db()
            if self.db_connection is None:
                return None
        cursor = self.db_connection.cursor()
        try:
            cursor.execute(query, params)
            self.db_connection.commit()
            return cursor
        except Error as e:
            self.db_connection.rollback()
            messagebox.showerror("Erreur SQL", f"Erreur lors de l'exécution de la requête : {e}")
            return None
        finally:
            cursor.close() # Fermer le curseur après l'exécution

    def fetch_one(self, query, params=None):
        """Récupère une seule ligne en utilisant la connexion persistante."""
        if self.db_connection is None or not self.db_connection.is_connected():
            self.connect_db()
            if self.db_connection is None:
                return None
        cursor = self.db_connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            return cursor.fetchone()
        except Error as e:
            messagebox.showerror("Erreur SQL", f"Erreur lors de la récupération d'une ligne : {e}")
            return None
        finally:
            cursor.close()

    def fetch_all(self, query, params=None):
        """Récupère toutes les lignes en utilisant la connexion persistante."""
        if self.db_connection is None or not self.db_connection.is_connected():
            self.connect_db()
            if self.db_connection is None:
                return []
        cursor = self.db_connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        except Error as e:
            messagebox.showerror("Erreur SQL", f"Erreur lors de la récupération de plusieurs lignes : {e}")
            return []
        finally:
            cursor.close()

    def handle_login(self, event=None):
        if self.db_connection is None or not self.db_connection.is_connected():
            self.connect_db()
            if self.db_connection is None:
                return

        username = self.username_entry.get()
        password = self.pass_entry.get()
        cursor = self.db_connection.cursor(dictionary=True)

        try:
            query = "SELECT id_utilisateur, role_utilisateur, id_eleve FROM Utilisateurs WHERE identifiant = %s AND mot_de_passe = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()

            if user:
                self.current_user_id = user["id_utilisateur"]
                self.current_role = user["role_utilisateur"]
                self.current_eleve_id = user.get("id_eleve")
                self.create_main_ui()
            else:
                messagebox.showerror("Erreur d'authentification", "Identifiant ou mot de passe incorrect.")
                self.pass_entry.delete(0, tk.END)
        except Error as e:
            messagebox.showerror("Erreur SQL", f"Erreur lors de la requête de connexion : {e}")
        finally:
            cursor.close()

    def show_register_student(self):
        self.login_frame.destroy()
        self.register_frame = ttk.Frame(self.root, style="Card.TFrame", padding=30)
        self.register_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        ttk.Label(self.register_frame, text="✍️ Créer un compte Étudiant", font=("Segoe UI", 24, "bold"), foreground=self.colors["accent"]).pack(pady=(0, 10))

        ttk.Label(self.register_frame, text="Nom :", font=("Segoe UI", 11)).pack(anchor="w", pady=(5, 2))
        self.reg_nom_entry = ttk.Entry(self.register_frame)
        self.reg_nom_entry.pack(fill=tk.X, pady=5, ipady=8)

        ttk.Label(self.register_frame, text="Prénom :", font=("Segoe UI", 11)).pack(anchor="w", pady=(15, 2))
        self.reg_prenom_entry = ttk.Entry(self.register_frame)
        self.reg_prenom_entry.pack(fill=tk.X, pady=5, ipady=8)

        ttk.Label(self.register_frame, text="Identifiant :", font=("Segoe UI", 11)).pack(anchor="w", pady=(15, 2))
        self.reg_username_entry = ttk.Entry(self.register_frame)
        self.reg_username_entry.pack(fill=tk.X, pady=5, ipady=8)

        ttk.Label(self.register_frame, text="Mot de passe :", font=("Segoe UI", 11)).pack(anchor="w", pady=(15, 2))
        self.reg_pass_entry = ttk.Entry(self.register_frame, show="•")
        self.reg_pass_entry.pack(fill=tk.X, pady=5, ipady=8)

        register_button = ttk.Button(
            self.register_frame,
            text="S'INSCRIRE",
            style="Accent.TButton",
            command=self.register_new_student
        )
        register_button.pack(pady=20, fill=tk.X, ipady=10)

        back_to_login = ttk.Button(
            self.register_frame,
            text="Retour à la connexion",
            style="TButton",
            command=self.show_login_ui
        )
        back_to_login.pack(fill=tk.X, pady=(10, 0))

    def register_new_student(self):
        if self.db_connection is None or not self.db_connection.is_connected():
            self.connect_db()
            if self.db_connection is None:
                return

        nom = self.reg_nom_entry.get()
        prenom = self.reg_prenom_entry.get()
        username = self.reg_username_entry.get()
        password = self.reg_pass_entry.get()
        cursor = self.db_connection.cursor()

        try:
            # 1. Créer l'élève dans la table Eleves
            query_eleve = "INSERT INTO Eleves (nom_eleve, prenom_eleve) VALUES (%s, %s)"
            cursor.execute(query_eleve, (nom, prenom))
            eleve_id = cursor.lastrowid

            # 2. Créer l'utilisateur dans la table Utilisateurs
            query_user = "INSERT INTO Utilisateurs (id_eleve, identifiant, mot_de_passe, role_utilisateur) VALUES (%s, %s, %s, 'eleve')"
            cursor.execute(query_user, (eleve_id, username, password))
            self.db_connection.commit()
            messagebox.showinfo("Inscription réussie", "Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter.")
            self.register_frame.destroy()
            self.create_login_ui()
        except Error as e:
            self.db_connection.rollback()
            messagebox.showerror("Erreur d'inscription", f"Erreur lors de l'inscription : {e}")
        finally:
            cursor.close()

    def show_login_ui(self):
        if hasattr(self, 'register_frame'):
            self.register_frame.destroy()
        self.create_login_ui()

    def create_main_ui(self):
        if hasattr(self, 'login_frame'):
            self.login_frame.destroy()

        self.main_frame = ttk.Frame(self.root, style="Main.TFrame")  # Appliquer un style ttk
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        sidebar = ttk.Frame(self.main_frame, width=200, style="Card.TFrame")
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.content = ttk.Frame(self.main_frame, padding=15, style="Content.TFrame") # Appliquer un style ttk
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        header = ttk.Frame(self.content, style="Header.TFrame") # Appliquer un style ttk
        header.pack(fill=tk.X, pady=(0, 15))
        self.title_label = ttk.Label(header, text="Bienvenue",
                                     font=("Segoe UI", 18, "bold"), foreground=self.colors["accent"])
        self.title_label.pack(side=tk.LEFT, padx=10)

        self.card_container = ttk.Frame(self.content, style="Card.TFrame")
        self.card_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Configuration des styles pour les Frames
        self.style.configure("Main.TFrame", background=self.colors["bg"])
        self.style.configure("Content.TFrame", background=self.colors["bg"])
        self.style.configure("Header.TFrame", background=self.colors["bg"])

        self.setup_sidebar(sidebar)
        self.show_dashboard_based_on_role()

    def setup_sidebar(self, sidebar):
        buttons = []
        if self.current_role == "admin":
            buttons = [
                ("📊 Gestion Globale", self.show_admin_dashboard),
                ("🧑‍🎓 Gestion Élèves", self.show_manage_eleves),
                ("🏢 Gestion Professionnels", self.show_manage_professionnels),
                ("🗓️ Gestion Entretiens", self.show_manage_entretiens),
                ("📝 Gestion Critères", self.show_manage_criteres),
                ("⚙️ Gestion Grilles", self.show_manage_grilles),
                ("📁 Gestion Documents", self.show_manage_documents),
                ("👤 Gestion Utilisateurs", self.show_manage_users),
                ("ℹ️ Aide", self.show_help),
                ("🚪 Déconnexion", self.handle_logout)
            ]
        elif self.current_role == "eleve":
            buttons = [
                ("👤 Mon Profil", self.show_eleve_profile),
                ("➕ Ajouter Professionnel", self.show_add_professional),
                ("🏢 Gestion Professionnels", self.show_manage_professionnels),
                ("📄 Déposer Rapport", self.show_upload_report),
                ("📝 Mes Notes", self.show_my_notes),
                ("ℹ️ Aide", self.show_help),
                ("🚪 Déconnexion", self.handle_logout)
            ]
        else:
            buttons = [("ℹ️ Aide", self.show_help), ("🚪 Déconnexion", self.handle_logout)]

        for text, cmd in buttons:
            btn = ttk.Button(sidebar, text=text, command=cmd, style="TButton")
            btn.pack(fill=tk.X, pady=5, padx=5)

    def show_dashboard_based_on_role(self):
        if self.current_role == "admin":
            self.show_admin_dashboard()
        elif self.current_role == "eleve":
            self.show_eleve_profile()
        else:
            self.show_help()

    def handle_logout(self):
        if hasattr(self, 'main_frame'):
            self.main_frame.destroy()
        self.current_role = None
        self.current_user_id = None
        self.current_eleve_id = None
        self.create_login_ui()
        # Fermer la connexion lors de la déconnexion (ou à la fermeture de l'application)
        self.close_db()

    def clear_content(self):
        for widget in self.card_container.winfo_children():
            widget.destroy()

    def show_help(self):
        self.clear_content()
        self.title_label.config(text="Aide Utilisateur", foreground=self.colors["accent"])
        help_text = "Bienvenue dans l'application EvaluationDB.\n\n"
        if self.current_role == "eleve":
            help_text += "En tant qu'étudiant, vous disposez des fonctionnalités suivantes :\n\n"

            help_text += "**Mon Profil :**\n"
            help_text += "- Affiche les informations de votre compte (nom, prénom, identifiant).\n"
            help_text += "- Permet d'afficher votre mot de passe après une confirmation de sécurité.\n"
            help_text += "- Liste les entretiens que vous avez effectués, avec la date et les informations du professionnel (nom, email, téléphone).\n"
            help_text += "- Affiche les rapports que vous avez déposés, avec le nom du fichier et la date de dépôt.\n\n"

            help_text += "**Ajouter un Professionnel :**\n"
            help_text += "- Vous permet d'enregistrer les informations d'un professionnel que vous avez interviewé (nom de l'entreprise, nom du professionnel, poste, email, téléphone).\n"
            help_text += "- Après avoir enregistré un professionnel, vous êtes automatiquement redirigé pour enregistrer l'entretien associé (date et commentaire).\n\n"

            help_text += "**Déposer Rapport :**\n"
            help_text += "- Vous permet de sélectionner un fichier PDF depuis votre ordinateur et de le déposer. Le nom du fichier et la date de dépôt sont enregistrés.\n\n"

            help_text += "**Mes Notes :**\n"
            help_text += "- Affiche les notes qui vous ont été attribuées pour chaque entretien, critère par critère.\n"
            help_text += "- Affiche également le commentaire associé à chaque entretien (si un commentaire a été laissé).\n"
            help_text += "- Si les notes ou le commentaire pour un entretien ne sont pas encore disponibles, un message vous en informe.\n\n"

            help_text += "Utilisez le menu à gauche pour naviguer entre ces différentes sections de l'application."
        elif self.current_role == "admin":
            help_text += "En tant que professeur (administrateur), vous avez un accès complet à toutes les données et pouvez les gérer.\n\n"
            help_text += "Utilisez le menu à gauche pour naviguer entre les différentes sections de l'application."
        else:
            help_text += "Vous êtes connecté en tant qu'utilisateur non spécifié. Veuillez contacter l'administrateur pour plus d'informations."

        help_label = ttk.Label(self.card_container, text=help_text, justify=tk.LEFT, font=("Segoe UI", 11), foreground=self.colors["text"])
        help_label.pack(padx=20, pady=20)

    def show_admin_dashboard(self):
        self.clear_content()
        self.title_label.config(text="Tableau de Bord Administrateur", foreground=self.colors["accent"])
        admin_label = ttk.Label(self.card_container, text="Bienvenue sur le tableau de bord administrateur.", font=("Segoe UI", 12), foreground=self.colors["text"])
        admin_label.pack(padx=20, pady=20)

    def show_manage_eleves(self):
        self.clear_content()
        self.title_label.config(text="Gestion des Élèves", foreground=self.colors["accent"])

        analyzer = PerformanceAnalyzer() # Crée une instance de l'analyseur

        search_frame = ttk.Frame(self.card_container, style="Card.TFrame", padding=10)
        search_frame.pack(pady=(0, 10), fill=tk.X)

        ttk.Label(search_frame, text="Rechercher un élève:", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.eleve_search_entry = ttk.Entry(search_frame)
        self.eleve_search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.eleve_search_entry.bind("<KeyRelease>", self.update_eleve_list)

        columns = ("ID", "Nom", "Prénom")
        self.eleves_tree = ttk.Treeview(self.card_container, columns=columns, show="headings")

        # Masquer la colonne ID
        self.eleves_tree.column("ID", width=0, stretch=tk.NO)
        self.eleves_tree.heading("ID", text="ID")

        self.eleves_tree.heading("Nom", text="Nom")
        self.eleves_tree.column("Nom", anchor=tk.W)

        self.eleves_tree.heading("Prénom", text="Prénom")
        self.eleves_tree.column("Prénom", anchor=tk.W)

        self.eleves_tree.pack(expand=True, fill="both")

        # Analyse de la performance de l'appel initial à update_eleve_list
        analyzer.analyze_function_performance(self.update_eleve_list)

        self.update_eleve_list()

    def update_eleve_list(self, event=None):
        analyzer = PerformanceAnalyzer()

        search_term = self.eleve_search_entry.get().lower()
        query = f"""
            SELECT id_eleve, nom_eleve, prenom_eleve
            FROM Eleves
            WHERE LOWER(nom_eleve) LIKE '%{search_term}%' OR LOWER(prenom_eleve) LIKE '%{search_term}%'
            ORDER BY nom_eleve, prenom_eleve
        """

        data = self.fetch_all(query)

        analyzer.analyze_treeview_update_performance(self.eleves_tree, data)

        for item in self.eleves_tree.get_children():
            self.eleves_tree.delete(item)

        if data:
            for eleve in data:
                self.eleves_tree.insert("", tk.END, values=(
                    eleve['id_eleve'],
                    eleve['nom_eleve'],
                    eleve['prenom_eleve']
                ))
        else:
            pass

    def show_manage_professionnels(self):
        self.clear_content()
        self.title_label.config(text="Gestion des Professionnels", foreground=self.colors["accent"])

        manage_prof_frame = ttk.Frame(self.card_container, style="Card.TFrame", padding=10)
        manage_prof_frame.pack(pady=(0, 10), fill=tk.X)

        ttk.Label(manage_prof_frame, text="Nom du professionnel:", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.prof_search_entry = ttk.Entry(manage_prof_frame)
        self.prof_search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.prof_search_entry.bind("<KeyRelease>", self.update_professionnel_list)

        columns = ("ID", "Nom", "Prénom")
        self.professionnels_tree = ttk.Treeview(self.card_container, columns=columns, show="headings")

        self.professionnels_tree.column("ID", width=0, stretch=tk.NO)
        self.professionnels_tree.heading("ID", text="ID")

        self.professionnels_tree.heading("Nom", text="Nom")
        self.professionnels_tree.column("Nom", anchor=tk.W)

        self.professionnels_tree.heading("Prénom", text="Prénom")
        self.professionnels_tree.column("Prénom", anchor=tk.W)

        self.professionnels_tree.pack(expand=True, fill="both")

        self.update_professionnel_list()

    def update_professionnel_list(self, event=None):
        search_term = self.prof_search_entry.get().lower()
        query = f"""
            SELECT id_professionnel, nom_professionnel, prenom_professionnel
            FROM Professionnels
            WHERE LOWER(nom_professionnel) LIKE '%{search_term}%' OR LOWER(prenom_professionnel) LIKE '%{search_term}%'
            ORDER BY nom_professionnel, prenom_professionnel
        """
        data = self.fetch_all(query)

        for item in self.professionnels_tree.get_children():
            self.professionnels_tree.delete(item)

        if data:
            for pro in data:
                self.professionnels_tree.insert("", tk.END, values=(
                    pro['id_professionnel'],
                    pro['nom_professionnel'],
                    pro['prenom_professionnel']
                ))

    def show_manage_entretiens(self):
        self.clear_content()
        self.title_label.config(text="Gestion des Entretiens", foreground=self.colors["accent"])
        # Ajouter ici l'interface pour la gestion des entretiens
        entretiens_label = ttk.Label(self.card_container, text="Interface de gestion des entretiens.", font=("Segoe UI", 12), foreground=self.colors["text"])
        entretiens_label.pack(padx=20, pady=20)

    def show_manage_criteres(self):
        self.clear_content()
        self.title_label.config(text="Gestion des Critères", foreground=self.colors["accent"])
        # Ajouter ici l'interface pour la gestion des critères
        criteres_label = ttk.Label(self.card_container, text="Interface de gestion des critères.", font=("Segoe UI", 12), foreground=self.colors["text"])
        criteres_label.pack(padx=20, pady=20)

    def show_manage_grilles(self):
        self.clear_content()
        self.title_label.config(text="Gestion des Grilles d'Évaluation", foreground=self.colors["accent"])
        # Ajouter ici l'interface pour la gestion des grilles
        grilles_label = ttk.Label(self.card_container, text="Interface de gestion des grilles d'évaluation.", font=("Segoe UI", 12), foreground=self.colors["text"])
        grilles_label.pack(padx=20, pady=20)

    def show_manage_documents(self):
        self.clear_content()
        title_label = ttk.Label(self.card_container, text="Gestion des Documents Déposés", style="Title.TLabel")
        title_label.pack(pady=(0, 10), padx=20)

        download_latest_button = ttk.Button(
            self.card_container,
            text="Télécharger les derniers fichiers par élève",
            style="Accent.TButton",
            command=self.download_latest_documents_by_eleve
        )
        download_latest_button.pack(pady=(0, 10), padx=20, fill=tk.X)

        columns = ("ID", "Nom de l'élève", "Prénom de l'élève", "Titre du document", "Nom du fichier", "Date de dépôt", "Action")
        self.documents_tree = ttk.Treeview(self.card_container, columns=columns, show="headings", style="Treeview")

        self.documents_tree.column("ID", width=0, stretch=tk.NO)
        self.documents_tree.heading("ID", text="ID")
        self.documents_tree.heading("Nom de l'élève", text="Nom de l'élève")
        self.documents_tree.column("Nom de l'élève", anchor=tk.W)
        self.documents_tree.heading("Prénom de l'élève", text="Prénom de l'élève")
        self.documents_tree.column("Prénom de l'élève", anchor=tk.W)
        self.documents_tree.heading("Titre du document", text="Titre du document")
        self.documents_tree.column("Titre du document", anchor=tk.W)
        self.documents_tree.heading("Nom du fichier", text="Nom du fichier")
        self.documents_tree.column("Nom du fichier", anchor=tk.W)
        self.documents_tree.heading("Date de dépôt", text="Date de dépôt")
        self.documents_tree.column("Date de dépôt", anchor=tk.W)
        self.documents_tree.heading("Action", text="Action")
        self.documents_tree.column("Action", anchor=tk.W)
        self.documents_tree.pack(expand=True, fill="both", padx=20)

        documents = self.fetch_all("""
            SELECT d.id_document, e.nom_eleve, e.prenom_eleve, d.nom_document, d.nom_fichier, d.date_upload
            FROM Documents d
            JOIN Eleves e ON d.id_eleve = e.id_eleve
            ORDER BY e.nom_eleve, e.prenom_eleve, d.date_upload DESC
        """)
        if documents:
            for doc in documents:
                self.documents_tree.insert("", tk.END, values=(
                    doc['id_document'],
                    doc['nom_eleve'],
                    doc['prenom_eleve'],
                    doc['nom_document'],
                    doc['nom_fichier'],
                    doc['date_upl'],
                    doc['date_upload'],
                    "Télécharger" # Placeholder pour le bouton de téléchargement
                ))

    def download_latest_documents_by_eleve(self):
        latest_documents = self.fetch_all("""
            SELECT d.id_document, e.nom_eleve, e.prenom_eleve, d.nom_fichier, d.contenu_fichier, d.nom_document
            FROM Documents d
            JOIN Eleves e ON d.id_eleve = e.id_eleve
            WHERE d.id_document IN (
                SELECT MAX(id_document)
                FROM Documents
                GROUP BY id_eleve
            )
        """)

        if not latest_documents:
            messagebox.showinfo("Information", "Aucun document n'a été trouvé.")
            return

        download_dir = filedialog.askdirectory(title="Sélectionner le dossier de téléchargement")
        if not download_dir:
            return

        success_count = 0
        error_count = 0

        for doc in latest_documents:
            filepath = f"{download_dir}/{doc['nom_eleve']}_{doc['prenom_eleve']}_{doc['nom_fichier']}"
            try:
                with open(filepath, 'wb') as f:
                    f.write(doc['contenu_fichier'])
                success_count += 1
            except Exception as e:
                messagebox.showerror("Erreur de téléchargement", f"Erreur lors du téléchargement de {doc['nom_document']} de {doc['nom_eleve']} {doc['prenom_eleve']}: {e}")
                error_count += 1

        message = f"{success_count} fichiers téléchargés avec succès."
        if error_count > 0:
            message += f"\n{error_count} fichiers n'ont pas pu être téléchargés."
        messagebox.showinfo("Téléchargement terminé", message)
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".pdf",
            filetypes=[("Fichiers PDF", "*.pdf"), ("Tous les fichiers", "*.*")]
        )
        if file_path:
            self.file_path_label.config(text=file_path)
    def download_selected_document(self, event):
        selected_item = self.documents_tree.selection()
        if selected_item:
            file_info = self.documents_tree.item(selected_item, 'values')
            document_id = self.get_document_id_from_treeview(selected_item) # Nouvelle fonction pour récupérer l'ID

            if document_id:
                document_data = self.fetch_one("SELECT nom_fichier, contenu_fichier, nom_document FROM Documents WHERE id_document = %s", (document_id,))
                if document_data and document_data['contenu_fichier']:
                    save_path = filedialog.asksaveasfilename(
                        defaultextension=".pdf",
                        initialfile=document_data['nom_fichier'],
                        title="Enregistrer le rapport"
                    )
                    if save_path:
                        try:
                            with open(save_path, 'wb') as f:
                                f.write(document_data['contenu_fichier'])
                            messagebox.showinfo("Téléchargement réussi", f"Le fichier '{document_data['nom_document']}' a été enregistré avec succès.")
                        except Exception as e:
                            messagebox.showerror("Erreur de sauvegarde", f"Erreur lors de la sauvegarde du fichier : {e}")
                else:
                    messagebox.showerror("Erreur", "Le contenu du fichier est introuvable.")
            else:
                messagebox.showerror("Erreur", "Impossible de récupérer l'ID du document.")

    def get_document_id_from_treeview(self, selected_item):
        """Récupère l'ID du document à partir de l'élément sélectionné du Treeview."""
        values = self.documents_tree.item(selected_item, 'values')
        if values:
            return values[0]  # L'ID est la première colonne (masquée)
        return None

    def show_manage_users(self):
        self.clear_content()
        self.title_label.config(text="Gestion des Utilisateurs", foreground=self.colors["accent"])
        # Ajouter ici l'interface pour la gestion des utilisateurs
        users_label = ttk.Label(self.card_container, text="Interface de gestion des utilisateurs.", font=("Segoe UI", 12), foreground=self.colors["text"])
        users_label.pack(padx=20, pady=20)

    def show_eleve_profile(self):
        self.clear_content()
        self.title_label.config(text="Mon Profil", foreground=self.colors["accent"])

        if self.current_eleve_id:
            eleve_info = self.fetch_one("SELECT nom_eleve, prenom_eleve FROM Eleves WHERE id_eleve = %s", (self.current_eleve_id,))
            user_info = self.fetch_one("SELECT identifiant FROM Utilisateurs WHERE id_utilisateur = %s", (self.current_user_id,))

            if eleve_info and user_info:
                info_frame = ttk.Frame(self.card_container, style="Card.TFrame", padding=20)
                info_frame.pack(pady=10, padx=10, fill=tk.X)

                ttk.Label(info_frame, text=f"Nom: {eleve_info['nom_eleve']}", font=("Segoe UI", 11)).pack(pady=2, anchor="w")
                ttk.Label(info_frame, text=f"Prénom: {eleve_info['prenom_eleve']}", font=("SegoeUI", 11)).pack(pady=2, anchor="w")
                ttk.Label(info_frame, text=f"Identifiant: {user_info['identifiant']}", font=("Segoe UI", 11)).pack(pady=2, anchor="w")

                show_password_button = ttk.Button(info_frame, text="Afficher le mot de passe", command=self.show_password, style="TButton")
                show_password_button.pack(pady=10, fill=tk.X)

                # Afficher les entretiens de l'élève
                entretiens = self.fetch_all("""
                    SELECT e.date_entretien, e.lieu_entretien, pro.nom_professionnel, pro.prenom_professionnel
                    FROM Entretiens e
                    JOIN Professionnels pro ON e.id_professionnel = pro.id_professionnel
                    WHERE e.id_eleve = %s
                    ORDER BY e.date_entretien DESC
                """, (self.current_eleve_id,))

                if entretiens:
                    ttk.Label(self.card_container, text="Mes Entretiens:", font=("Segoe UI", 12, "bold")).pack(pady=(15, 5), padx=10, anchor="w")
                    entretiens_tree = ttk.Treeview(self.card_container, columns=("Date", "Lieu", "Professionnel"), show="headings")
                    entretiens_tree.heading("Date", text="Date")
                    entretiens_tree.heading("Lieu", text="Lieu")
                    entretiens_tree.heading("Professionnel", text="Professionnel")
                    for entretien in entretiens:
                        entretiens_tree.insert("", tk.END, values=(
                            entretien['date_entretien'],
                            entretien['lieu_entretien'] if entretien['lieu_entretien'] else "N/A",
                            f"{entretien['prenom_professionnel']} {entretien['nom_professionnel']}"
                        ))
                    entretiens_tree.pack(fill=tk.X, padx=10, pady=(0, 10))
                else:
                    ttk.Label(self.card_container, text="Aucun entretien réalisé pour le moment.", font=("Segoe UI", 11, "italic"), foreground=self.colors["secondary_text"]).pack(pady=(5, 10), padx=10, anchor="w")

                # Afficher les rapports déposés par l'élève
                rapports = self.fetch_all("SELECT nom_document, nom_fichier, date_upload FROM Documents WHERE id_eleve = %s ORDER BY date_upload DESC", (self.current_eleve_id,))
                if rapports:
                    ttk.Label(self.card_container, text="Mes Rapports Déposés:", font=("Segoe UI", 12, "bold")).pack(pady=(15, 5), padx=10, anchor="w")
                    rapports_tree = ttk.Treeview(self.card_container, columns=("Titre du Fichier", "Nom du Fichier", "Date de Dépôt"), show="headings")
                    rapports_tree.heading("Titre du Fichier", text="Titre du Fichier")
                    rapports_tree.heading("Nom du Fichier", text="Nom du Fichier")
                    rapports_tree.heading("Date de Dépôt", text="Date de Dépôt")
                    for rapport in rapports:
                        rapports_tree.insert("", tk.END, values=(rapport['nom_document'], rapport['nom_fichier'], rapport['date_upload']))
                    rapports_tree.pack(fill=tk.X, padx=10, pady=(0, 10))
                else:
                    ttk.Label(self.card_container, text="Aucun rapport déposé pour le moment.", font=("Segoe UI", 11, "italic"), foreground=self.colors["secondary_text"]).pack(pady=(5, 10), padx=10, anchor="w")

            else:
                ttk.Label(self.card_container, text="Informations de profil non trouvées.", font=("Segoe UI", 11, "italic"), foreground=self.colors["error"]).pack(pady=20, padx=20)
        else:
            ttk.Label(self.card_container, text="Impossible de récupérer l'ID de l'élève.", font=("Segoe UI", 11, "italic"), foreground=self.colors["error"]).pack(pady=20, padx=20)

    def show_password(self):
        if self.current_user_id:
            password_info = self.fetch_one("SELECT mot_de_passe FROM Utilisateurs WHERE id_utilisateur = %s", (self.current_user_id,))
            if password_info and messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir afficher votre mot de passe ?"):
                messagebox.showinfo("Votre mot de passe", f"Votre mot de passe est : {password_info['mot_de_passe']}")
        else:
            messagebox.showerror("Erreur", "Impossible de récupérer l'ID de l'utilisateur.")

    def show_add_professional(self):
        self.clear_content()
        self.title_label.config(text="Ajouter un Professionnel", foreground=self.colors["accent"])

        add_prof_frame = ttk.Frame(self.card_container, style="Card.TFrame", padding=20)
        add_prof_frame.pack(pady=10, padx=10, fill=tk.X)

        ttk.Label(add_prof_frame, text="Nom de l'entreprise:", font=("Segoe UI", 11)).grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.prof_entreprise_entry = ttk.Entry(add_prof_frame)
        self.prof_entreprise_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(add_prof_frame, text="Intitulé du métier:", font=("Segoe UI", 11)).grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.prof_intitule_entry = ttk.Entry(add_prof_frame)
        self.prof_intitule_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(add_prof_frame, text="Secteur d'activité:", font=("Segoe UI", 11)).grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.prof_secteur_entry = ttk.Entry(add_prof_frame)
        self.prof_secteur_entry.grid(row=2, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(add_prof_frame, text="Nom du professionnel:", font=("Segoe UI", 11)).grid(row=3, column=0, sticky="w", pady=5, padx=5)
        self.prof_nom_entry = ttk.Entry(add_prof_frame)
        self.prof_nom_entry.grid(row=3, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(add_prof_frame, text="Prénom du professionnel:", font=("Segoe UI", 11)).grid(row=4, column=0, sticky="w", pady=5, padx=5)
        self.prof_prenom_entry = ttk.Entry(add_prof_frame)
        self.prof_prenom_entry.grid(row=4, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(add_prof_frame, text="Email du professionnel:", font=("Segoe UI", 11)).grid(row=5, column=0, sticky="w", pady=5, padx=5)
        self.prof_email_entry = ttk.Entry(add_prof_frame)
        self.prof_email_entry.grid(row=5, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(add_prof_frame, text="Numéro du professionnel:", font=("Segoe UI", 11)).grid(row=6, column=0, sticky="w", pady=5, padx=5)
        self.prof_numero_entry = ttk.Entry(add_prof_frame)
        self.prof_numero_entry.grid(row=6, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(add_prof_frame, text="Linkedin du professionnel:", font=("Segoe UI", 11)).grid(row=7, column=0, sticky="w", pady=5, padx=5)
        self.prof_linkedin_entry = ttk.Entry(add_prof_frame)
        self.prof_linkedin_entry.grid(row=7, column=1, sticky="ew", pady=5, padx=5)

        add_button = ttk.Button(add_prof_frame, text="Ajouter et enregistrer l'entretien", command=self.add_professional_and_show_entretien_form, style="Accent.TButton")
        add_button.grid(row=8, column=0, columnspan=2, pady=15, padx=5, sticky="ew")
        add_prof_frame.columnconfigure(1, weight=1)

    def add_professional_and_show_entretien_form(self):
        nom_entreprise = self.prof_entreprise_entry.get()
        intitule_metier = self.prof_intitule_entry.get()
        secteur = self.prof_secteur_entry.get()
        nom = self.prof_nom_entry.get()
        prenom = self.prof_prenom_entry.get()
        email = self.prof_email_entry.get()
        numero = self.prof_numero_entry.get()
        linkedin = self.prof_linkedin_entry.get()

        if not nom or not prenom or not nom_entreprise:
            messagebox.showerror("Erreur", "Veuillez remplir au moins le nom de l'entreprise, le nom et le prénom du professionnel.")
            return

        cursor = self.execute_query(
            "INSERT INTO Professionnels (nom_professionnel, prenom_professionnel, email_professionnel, tel_professionnel,entreprise,linkedin, intitule_metier, secteur) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (nom_entreprise, intitule_metier, secteur, nom, prenom, email, numero, linkedin)
        )
        if cursor:
            professionnel_id = cursor.lastrowid
            cursor.close()
            self.show_add_entretien(professionnel_id)
        else:
            messagebox.showerror("Erreur", "Erreur lors de l'enregistrement du professionnel.")

    def show_add_entretien(self, professionnel_id):
        self.clear_content()
        self.title_label.config(text="Enregistrer l'Entretien", foreground=self.colors["accent"])

        entretien_frame = ttk.Frame(self.card_container, style="Card.TFrame", padding=20)
        entretien_frame.pack(pady=10, padx=10, fill=tk.X)

        ttk.Label(entretien_frame, text="Date de l'entretien (JJ-MM-AAAA):", font=("Segoe UI", 11)).grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.entretien_date_entry = ttk.Entry(entretien_frame)
        self.entretien_date_entry.insert(0, "JJ-MM-AAAA")  # Format affiché
        self.entretien_date_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=5)

        # Ajouter le bouton pour afficher le calendrier
        ttk.Button(entretien_frame, text="Choisir une date", command=self.afficher_calendrier_entretien).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(entretien_frame, text="Lieu de l'entretien (facultatif):", font=("Segoe UI", 11)).grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.entretien_lieu_entry = ttk.Entry(entretien_frame)
        self.entretien_lieu_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=5)

        save_button = ttk.Button(entretien_frame, text="Enregistrer l'entretien", command=lambda: self.save_entretien(professionnel_id), style="Accent.TButton")
        save_button.grid(row=2, column=0, columnspan=3, pady=15, padx=5, sticky="ew")
        entretien_frame.columnconfigure(1, weight=1)

    def afficher_calendrier_entretien(self):
        top = tk.Toplevel(self.root)
        cal = Calendar(top, selectmode='day',
                       locale='fr_FR',  # Pour afficher le calendrier en français
                       date_pattern='dd-mm-yyyy') # Format de la date sélectionnée

        def selectionner_date():
            date_selectionnee = cal.get_date()
            self.entretien_date_entry.delete(0, tk.END)
            self.entretien_date_entry.insert(0, date_selectionnee)
            top.destroy()

        ttk.Button(top, text="Sélectionner", command=selectionner_date).pack(pady=10)
        cal.pack(padx=10, pady=10)

    def save_entretien(self, professionnel_id):
        date_entretien_str = self.entretien_date_entry.get()
        lieu_entretien = self.entretien_lieu_entry.get().strip()

        try:
            # Valider le format de la date (JJ-MM-AAAA)
            time.strptime(date_entretien_str, "%d-%m-%Y")
            # Convertir la date au format AAAA-MM-JJ pour la base de données
            jour, mois, annee = date_entretien_str.split('-')
            date_entretien = f"{annee}-{mois}-{jour}"
        except ValueError:
            messagebox.showerror("Erreur de format", "Le format de la date doit être JJ-MM-AAAA.")
            return

        if self.current_eleve_id:
            cursor = self.execute_query(
                "INSERT INTO Entretiens (id_eleve, id_professionnel, date_entretien, lieu_entretien) VALUES (%s, %s, %s, %s)",
                (self.current_eleve_id, professionnel_id, date_entretien, lieu_entretien)
            )
            if cursor:
                cursor.close()
                messagebox.showinfo("Succès", "L'entretien a été enregistré avec succès.")
                self.show_eleve_profile() # Retourner au profil après l'enregistrement
            else:
                messagebox.showerror("Erreur", "Erreur lors de l'enregistrement de l'entretien.")
        else:
            messagebox.showerror("Erreur", "Impossible de récupérer l'ID de l'élève.")

    def show_upload_report(self):
        self.clear_content()
        self.title_label.config(text="Déposer un Rapport", foreground=self.colors["accent"])

        upload_frame = ttk.Frame(self.card_container, style="Card.TFrame", padding=20)
        upload_frame.pack(pady=10, padx=10, fill=tk.X)

        ttk.Label(upload_frame, text="Titre du document:", font=("Segoe UI", 11)).pack(pady=5, anchor="w")
        self.report_title_entry = ttk.Entry(upload_frame)
        self.report_title_entry.pack(fill=tk.X, pady=5, ipady=8)

        ttk.Label(upload_frame, text="Sélectionner un fichier PDF:", font=("Segoe UI", 11)).pack(pady=5, anchor="w")
        self.file_path_label = ttk.Label(upload_frame, text="Aucun fichier sélectionné", foreground=self.colors["secondary_text"])
        self.file_path_label.pack(pady=5, anchor="w")

        def browse_file():
            file_path = filedialog.askopenfilename(
                defaultextension=".pdf",
                filetypes=[("Fichiers PDF", "*.pdf"), ("Tous les fichiers", "*.*")]
            )
            if file_path:
                self.file_path_label.config(text=file_path)

        browse_button = ttk.Button(upload_frame, text="Parcourir...", command=browse_file, style="TButton")
        browse_button.pack(pady=10, fill=tk.X)

        upload_button = ttk.Button(upload_frame, text="Déposer le rapport", command=self.upload_report, style="Accent.TButton")
        upload_button.pack(pady=10, fill=tk.X)

    def show_upload_report(self):
        self.clear_content()
        title_label = ttk.Label(self.card_container, text="Déposer un Rapport", style="Title.TLabel")
        title_label.pack(padx=20, pady=10)
    
        form_frame = ttk.Frame(self.card_container, style="Card.TFrame", padding=20)
        form_frame.pack(padx=20, pady=10, fill=tk.X)
    
        ttk.Label(form_frame, text="Sélectionner le fichier PDF :", font=("Segoe UI", 11)).pack(anchor="w", pady=(5, 2))
        self.file_path_label = ttk.Label(form_frame, text="Aucun fichier sélectionné", style="Info.TLabel")
        self.file_path_label.pack(fill=tk.X, pady=5)
    
        browse_button = ttk.Button(form_frame, text="Parcourir...", command=self.browse_file, style="TButton")
        browse_button.pack(pady=10, fill=tk.X)
    
        ttk.Label(form_frame, text="Nom du document (optionnel) :", font=("Segoe UI", 11)).pack(anchor="w", pady=(10, 2))
        self.document_name_entry = ttk.Entry(form_frame, style="TEntry")
        self.document_name_entry.pack(fill=tk.X, pady=5, ipady=8)
    
        upload_button = ttk.Button(form_frame, text="Déposer le rapport", style="Accent.TButton", command=self.upload_file)
        upload_button.pack(pady=20, fill=tk.X, ipady=10)
    
    def upload_file(self):
        file_path = self.file_path_label.cget("text")
        document_name = self.document_name_entry.get().strip()

        if file_path == "Aucun fichier sélectionné":
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier à déposer.")
            return

        file_name = os.path.basename(file_path)
        upload_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Simuler l'enregistrement du chemin du fichier (en réalité, on pourrait le stocker dans un dossier sur le serveur)
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        destination_path = os.path.join(upload_dir, file_name)

        try:
            import shutil
            shutil.copy2(file_path, destination_path)
            cursor = self.execute_query(
                "INSERT INTO Documents (id_eleve, nom_document, nom_fichier, date_upload) VALUES (%s, %s, %s, %s)",
                (self.current_eleve_id, document_name if document_name else file_name, file_name, upload_date)
            )
            if cursor:
                messagebox.showinfo("Dépôt réussi", f"Le fichier '{file_name}' a été déposé avec succès.")
                self.file_path_label.config(text="Aucun fichier sélectionné")
                self.document_name_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Erreur", "Erreur lors de l'enregistrement des informations du fichier.")
        except Exception as e:
            messagebox.showerror("Erreur de dépôt", f"Une erreur s'est produite lors du dépôt du fichier : {e}")
    def show_my_notes(self):
        self.clear_content()
        self.title_label.config(text="Mes Notes", foreground=self.colors["accent"])

        if self.current_eleve_id:
            notes_data = self.fetch_all("""
                SELECT e.date_entretien, pro.nom_professionnel, pro.prenom_professionnel,
                       c.nom_critere, sc.score, sc.commentaire
                FROM ScoresEvaluation sc
                JOIN Evaluations ev ON sc.id_evaluation = ev.id_evaluation
                JOIN Entretiens e ON ev.id_entretien = e.id_entretien
                JOIN Professionnels pro ON e.id_professionnel = pro.id_professionnel
                JOIN Criteres c ON sc.id_critere = c.id_critere
                WHERE e.id_eleve = %s
                ORDER BY e.date_entretien DESC, c.nom_critere
            """, (self.current_eleve_id,))

            if notes_data:
                # Organiser les notes par entretien
                entretiens_notes = {}
                for note in notes_data:
                    entretien_key = (note['date_entretien'], f"{note['prenom_professionnel']} {note['nom_professionnel']}")
                    if entretien_key not in entretiens_notes:
                        entretiens_notes[entretien_key] = []
                    entretiens_notes[entretien_key].append(note)

                if entretiens_notes:
                    for (date_entretien, nom_professionnel), notes in entretiens_notes.items():
                        entretien_label = ttk.Label(self.card_container, text=f"Entretien du {date_entretien} avec {nom_professionnel}:", font=("Segoe UI", 12, "bold")).pack(pady=(10, 2), padx=10, anchor="w")
                        notes_tree = ttk.Treeview(self.card_container, columns=("Critère", "Note", "Commentaire"), show="headings")
                        notes_tree.heading("Critère", text="Critère")
                        notes_tree.heading("Note", text="Note")
                        notes_tree.heading("Commentaire", text="Commentaire")
                        for note_item in notes:
                            notes_tree.insert("", tk.END, values=(note_item['nom_critere'], note_item['score'] if note_item['score'] is not None else "N/A", note_item['commentaire'] if note_item['commentaire'] else "N/A"))
                        notes_tree.pack(fill=tk.X, padx=10, pady=(0, 5))
                else:
                    ttk.Label(self.card_container, text="Aucune note disponible pour vos entretiens.",font=("Segoe UI", 11, "italic"), foreground=self.colors["secondary_text"]).pack(pady=20, padx=20)

            else:
                ttk.Label(self.card_container, text="Vos notes ne sont pas encore disponibles.", font=("Segoe UI", 11, "italic"), foreground=self.colors["secondary_text"]).pack(pady=20, padx=20)
        else:
            ttk.Label(self.card_container, text="Impossible de récupérer l'ID de l'élève.", font=("Segoe UI", 11, "italic"), foreground=self.colors["error"]).pack(pady=20, padx=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = DBManagerPro(root)
    root.mainloop()